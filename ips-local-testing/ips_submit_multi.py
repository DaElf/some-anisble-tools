#!/usr/bin/env python

import sys
import os
import os.path
import boto3
import random
import string
import argparse
import subprocess
import tempfile
import shutil


def parse_command_line():
    """Parse the command line

    Returns:
        args <Namespace>: the arguments from the command line
    """

    parser = argparse.ArgumentParser(
            description = "Submit ESPA jobs for processing")
    parser.add_argument('count',
            type = int,
            nargs = '?',
            default = 0,
            help = 'Number of jobs to submit')
    parser.add_argument('--batch-command',
            dest = 'batch_cmd',
            action = 'store',
            default = None,
            help = "Command to run in batch container")
    parser.add_argument('--input-bucket',
            type = str,
            dest = 'input_bucket',
            action = 'store',
            default = 'usgs-landsat',
            help = "Input S3 bucket (default: usgs-landsat)")
    parser.add_argument('--input-job-file',
            type = str,
            dest = 'input_job_file',
            action = 'store',
            default = None,
            help = "File of input file names to submit")
    parser.add_argument('--job-definition',
            type = str,
            dest = 'job_definition',
            action = 'store',
            default = None,
            help = "Batch job definition")
    parser.add_argument('--prefix',
            type = str,
            dest = 'prefix',
            action = 'store',
            default = None,
            help = "Comma-separated list of prefixes of S3 input files (default: ignore prefix)")
    parser.add_argument('--queue',
            dest = 'queue',
            type = str,
            action = 'store',
            default = None,
            help = "Batch queue to submit jobs in")

    args = parser.parse_args()

    return args


def get_arg_value(arg_value, environ_var, default_value):
    """Get the value of an argument based on the values from
    the command-line arguments, the value of an associated
    environment variable, and a default value for the argument.

    Args:
        arg_value <str>: the value from the command line arguments
        environ_var <str>: the name of the environment variable
        default_value <str>: the default value

    Returns:
        value <str>: the value for the argument
    """

    value = None
    if arg_value is not None:
        value = arg_value
    elif environ_var in os.environ:
        value = os.environ[environ_var]
    elif default_value is not None:
        value = default_value

    return value


def validate_args(args):
    """Validate the command line arguments and check for
    environment variables where appropriate.  We make some of
    the values global because otherwise we'd have some long
    argument lists.

    Args:
        args <dict>: The parsed command line arguments
    """

    global batch_cmd
    global job_definition
    global queue

    queue = get_arg_value(args.queue, 'ipsQueue', None)
    if queue is None:
        sys.stderr.write("Error: queue not specified\n" +
                "       Must use --queue or set ipsQueue\n")
        exit(1)

    if 'AWSRegion' in os.environ:
        client = boto3.client('batch', region_name=os.environ['AWSRegion'])
    else:
        client = boto3.client('batch')
    job_queues = client.describe_job_queues(jobQueues=[queue])
    if len(job_queues['jobQueues']) == 0:
        sys.stderr.write("Error: queue {} not found\n".format(queue))
        exit(1)

    job_definition = get_arg_value(args.job_definition,
            'ipsJobDefinition', None)
    if job_definition is None:
        sys.stderr.write("Error: job definition not specified\n" +
                "       Must use --job-definition or set ipsJobDefinition\n")
        exit(1)

    defs = client.describe_job_definitions(jobDefinitionName=job_definition)
    if len(defs['jobDefinitions']) == 0:
        sys.stderr.write("Error: job definition {} not found\n".
                format(job_definition))
        exit(1)

    # Validate the imput bucket name
    if 'AWSRegion' in os.environ:
        client = boto3.client('s3', region_name=os.environ['AWSRegion'])
    else:
        client = boto3.client('s3')
    try:
        acl = client.get_bucket_acl(Bucket=args.input_bucket)
    except Exception:
        sys.stderr.write("Error: input bucket {} not found\n".
                format(args.input_bucket))
        exit(1)

    # Provide a default for the batch command
    if args.batch_cmd is not None:
        batch_cmd = args.batch_cmd
    else:
        batch_cmd = '/opt/bin/ips-batch-worker.sh'


def get_satellite_from_product_id(pid):
    """Get the number of the satellite associate with a scene.

    Args:
        pid <str>: The product ID of the scene

    Returns:
        satellite <str>: A single digit identifying the satellite
                that acquired the image
    """

    return pid[2:3]


def parse_s3_object(bucket, s3_obj):
    """Parse an S3 object and return an S3 directory and product ID.
    Tar file names have (at least) two formats:
        LC80170392013141LGN03.tar.gz
        LC80220292013112LGN03_L0R.tar.gz
    This function attempts to extract the product ID from either
    format.

    Args:
        s3_obj <S3 object>: S3 object to be parsed

    Returns:
        (inputURL, inputProductId) (<str>, <str>):  an S3
                filename and product ID corresponding to the object
    """

    if not s3_obj.key.endswith('tar.gz'):
        return (None, None)
    inputURL = os.path.join('s3://', bucket, s3_obj.key)
    tarfile = os.path.basename(s3_obj.key)
    file_root = tarfile.replace('.tar.gz', '')
    inputProductId = file_root.split('_')[0]

    # Don't return TIRS-only or OLI-only scenes
    if inputProductId.startswith('LT8') or inputProductId.startswith('LO8'):
        return (None, None)

    return (inputURL, inputProductId)


def getS3ObjectList(bucket, prefixList):
    """Get a list of objects in an S3 bucket

    Get a list of objects in an S3 bucket, either by using a
    list of prefixes, or listing all the objects in the bucket.

    Args:
        bucket <str>: input bucket name
        prefixList <list>: list of prefixes (e.g. [L7, L8])

    Returns:
        List of the objects in the S3 bucket that start with
        one of the given prefixes.
    """

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    objectList = []
    if prefixList is not None:
        for prefix in prefixList:
            for s3_obj in my_bucket.objects.filter(Prefix=prefix):
                (inputURL, inputProductId) = parse_s3_object(bucket, s3_obj)
                if inputURL is not None:
                    objectList.append([inputURL, inputProductId])
    else:
        for s3_obj in my_bucket.objects.all():
            (inputURL, inputProductId) = parse_s3_object(bucket, s3_obj)
            if inputURL is not None:
                objectList.append([inputURL, inputProductId])

    return objectList


def get_list_from_file(filename):
    """ Read a list of scenes from a file.  This is an alternative
    to getting the list from the S3 bucket.  Each line of the file
    contains an S3 URL pointing to a tar file with the scene to
    be processed.

    Args:
        filename <str>: The name of the file with the list of scenes

    Returns:
        objectList <list>: A list of scenes from the file
    """

    try:
        file = open(filename)
    except IOError:
        sys.stderr.write("Error: Can't open input file {}\n".format(filename))
        exit(1)

    objectList = []
    for line in file:
        # Strip comments starting with '#'
        s = line.split('#')
        # Strip trailing whitewpace (including newlines)
        url = s[0].strip()
        if len(url) == 0:
            continue
        inputProductId = os.path.basename(url).split('.')[0].split('_')[0]
        objectList.append([url, inputProductId])

    file.close()
    return objectList


def write_list_to_file(filename, list):
    """Write the contents of a list to a file.  The list is
    assumed to consist of strings and a new line is put at
    the end of each list element, so the file will have a
    line for each item in the list.

    Args:
        filename <str>: The name for the file
        list <list>: The list to be written to the file
    """

    try:
        ofile = open(filename, 'w')
    except Exception as e:
        sys.stderr.write("Error: can't create file '{}': {}\n".
                format(filename, e))
        exit(1)

    for item in list:
        try:
            ofile.write("{}\n".format(item))
        except Exception as e:
            sys.stderr.write("Error: can't write file '{}': {}\n".
                    format(filename, e))
            exit(1)

    ofile.close()


def get_bpf_lists(bucket, prefix):
    """Get a list of objects in an S3 bucket

    Get a list of objects in an S3 bucket, either by using a
    list of prefixes, or listing all the objects in the bucket.

    Args:
        bucket <str>: input bucket name
        prefixList <list>: list of prefixes (e.g. [L7, L8])

    Returns:
        List of the objects in the S3 bucket that start with
        one of the given prefixes.
    """

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    oli_list = []
    tirs_list = []

    sys.stdout.write("Gathering list of BPF file names ... ")
    sys.stdout.flush()
    for s3_obj in my_bucket.objects.filter(Prefix=prefix):
        filename = os.path.basename(s3_obj.key).rstrip()
        if filename.startswith('LO8BPF'):
            oli_list.append(filename)
        elif filename.startswith('LT8BPF'):
            tirs_list.append(filename)
    print('done')

    return (oli_list, tirs_list)


def create_bpf_name_files(job_bucket, job_prefix):
    """ Create two files containing lists of the BPF files
    in the auxiliary data subdirectory of the usgs-landsat bucket.
    One file will contain names of all the OLI BPF files, the
    other will contain names of all the TIRS BPF files.  The
    files are provided so that find_aux_files.py can use them
    instead of gathering the list itself.  A large number of
    jobs hitting the bucket at the same time causes problems.

    Args:
        job_bucket <str>: The name of the bucket holding the job files
        job_prefix <str>: The prefix (directory path) for the files
    """

    bpf_oli_fn = 'bpf_oli_filenames.txt'
    bpf_tirs_fn = 'bpf_tirs_filenames.txt'

    (oli_list, tirs_list) = get_bpf_lists('usgs-landsat', 'data/auxiliary/bpf')
    oli_list.sort()
    tirs_list.sort()

    tmpdir = tempfile.mkdtemp()
    oli_file = os.path.join(tmpdir, bpf_oli_fn)
    write_list_to_file(oli_file, oli_list)
    tirs_file = os.path.join(tmpdir, bpf_tirs_fn)
    write_list_to_file(tirs_file, tirs_list)

    s3 = boto3.client('s3')
    s3.upload_file(oli_file, job_bucket,
            os.path.join(job_prefix, bpf_oli_fn))
    s3.upload_file(tirs_file, job_bucket,
            os.path.join(job_prefix, bpf_tirs_fn))

    shutil.rmtree(tmpdir)


def job_prefix(uniq):
    """Return the job prefix associated with a random string.

    Args:
        A randomly-chosen string that assures uniqueness for the job prefix

    Returns:
        The job prefix (subdirectory name in the job bucket)
    """

    return 'ips-' + uniq


def create_job_file(uniq, batch_index):
    """Create a file with the list of scenes for an array job.

    Args:
        uniq <str>: The unique prefix for the job
        batch_index <int>: The index of this file in the sequence

    Returns:
        job_file <file>: the file object associated with the new file
    """

    dir = tempfile.gettempdir()
    fn = os.path.join(dir,
            job_prefix(uniq) + '-' +  str(batch_index).zfill(3) + '.jobctl')
    try:
        job_file = open(fn, 'w')
    except IOError as e:
        sys.stderr.write("Error: can't create batch array file {}: {}\n".
                format(fn, e))
        exit(1)

    return job_file


def submit_job(job_file_name, size):
    """Submit an array job to the AWS batch queue

    Args:
        job_file_name <str>: The name of the file with the job array
        size <int>:  The number of jobs in the array
    """

    if 'AWSRegion' in os.environ:
        client = boto3.client('batch', region_name=os.environ['AWSRegion'])
        s3_client = boto3.client('s3', region_name=os.environ['AWSRegion'])
    else:
        client = boto3.client('batch')
        s3_client = boto3.client('s3')

    # Copy the job file to the job bucket
    job_bucket = 'usgs-landsat'
    job_key_prefix = 'projects/lpip/test/job'
    job_name_base = os.path.basename(job_file_name).split('.')[0]
    prefix = os.path.join(job_key_prefix,
            '-'.join(job_name_base.split('-')[:-1]))
    s3_key = os.path.join(prefix, os.path.basename(job_file_name))
    s3_client.upload_file(job_file_name, job_bucket, s3_key)
    s3_url = os.path.join('s3://', job_bucket, s3_key)
    os.remove(job_file_name)

    # Put the batch command into an array
    cmd_array = ['sudo', '-E', '-u', 'ips']
    cmd_array.extend(batch_cmd.split(' '))
    cmd_array.append('Ref::order_url')

    # Submit the job to AWS
    client.submit_job(
            jobName = job_name_base,
            jobQueue = queue,
            jobDefinition = job_definition,
            parameters = {'order_url': s3_url},
            containerOverrides = {
                'command': cmd_array
            },
            arrayProperties={
                'size': size
            },
            retryStrategy={
                'attempts': 1
            }
    )


def main():
    """Submit an AWS batch array job.
    """

    args = parse_command_line()
    validate_args(args)

    prefixList = None
    if args.prefix is not None:
        prefixList = []
        prefixes = args.prefix.split(',')
        for prefix in prefixes:
            prefixList.append(prefix)

    uniq = ''.join(random.choice(string.ascii_lowercase)
            for _ in range(4))

    array_count = 0
    job_count = 0
    batch_index = 0
    job_file = None

    if args.input_job_file is not None:
        obj_list = get_list_from_file(args.input_job_file)
    else:
        sys.stdout.write("Gathering list of scenes ... ")
        sys.stdout.flush()
        obj_list = getS3ObjectList(args.input_bucket, prefixList)
        sys.stdout.write("done\n")

    for (url, pid) in obj_list:
        if get_satellite_from_product_id(pid) == '8':
            create_bpf_name_files(job_bucket,
                    os.path.join(job_key_prefix, job_prefix(uniq)))
            break

    for (url, pid) in obj_list:

        if job_file is None:
            job_file = create_job_file(uniq, batch_index)
            batch_index += 1

        job_file.write(url + ' ' + pid + '\n')
        array_count += 1
        job_count += 1
        if job_count == args.count:
            break

        if (array_count == 10000):
            job_file_name = job_file.name
            job_file.close()
            submit_job(job_file_name, array_count)
            job_file = None
            array_count = 0

    if (array_count != 0):
        job_file_name = job_file.name
        job_file.close()
        submit_job(job_file_name, array_count)

    print("{} jobs submitted, prefix is {}".format(job_count, uniq))


batch_cmd = None
job_definition = None
queue = None
job_bucket = 'usgs-landsat'
job_key_prefix = 'projects/lpip/test/job'

if __name__ == '__main__':
        main()
