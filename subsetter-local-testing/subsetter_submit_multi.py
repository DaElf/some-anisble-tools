#!/usr/bin/env python

import sys
import os
import os.path
import urlparse
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
            description = "Submit subsetter jobs for processing")
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

    queue = get_arg_value(args.queue, 'subsetterQueue', None)
    if queue is None:
        sys.stderr.write("Error: queue not specified\n" +
                "       Must use --queue or set subsetterQueue\n")
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
            'subsetterJobDefinition', None)
    if job_definition is None:
        sys.stderr.write("Error: job definition not specified\n" +
                "       Must use --job-definition or set subsetterJobDefinition\n")
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
        batch_cmd = '/opt/bin/subsetter-batch-worker.sh'


def get_interval_from_file_key(key):
    """Get an interval ID from the key for a tar file.
    The key will be of the form '<dir>/.../<interval>.tar.gz'.

    Args:
        key <str>: the key for a tar file

    Returns:
        interval_id <str>: the interval ID associated with
                the tar file
    """

    return key.split('/')[-1].split('.')[0]


def get_interval_from_dir_key(key):
    """Get an interval ID from the key for a directory
    containing a scene.  Some scenes aren't packaged up
    in tar files, but consist of a directory containing
    the scene files.  The key will be of the form
    '<dir>/.../<interval>/<file>'.

    Args:
        key <str>: the key for a scene file

    Returns:
        interval_id <str>: the interval ID associated with
                the file
    """

    return key.split('/')[-2]


def getS3ObjectList(bucket, prefixList):
    """Get a list of scenes in an S3 bucket

    Get a list of scene objects in an S3 bucket, either by using a
    list of prefixes, or listing all the objects in the bucket.  A
    scene object may be a .tar.gz file or a directory containing
    the files that make up a scene.

    Args:
        bucket <str>: input bucket name
        prefixList <list>: list of prefixes (e.g. [L7, L8])

    Returns:
        List of the objects in the S3 bucket that start with
        one of the given prefixes.
    """

    s3 = boto3.resource('s3')
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        # If a client error is thrown, then check that it was a 404 error.
        # If it was a 404 error, then the bucket does not exist.
        error_code = e.response['Error']['Code']
        if error_code == '404':
            sys.stderr.write("Error: bucket '{}' does not exist\n".
                    format(bucket))
        else:
            sys.stderr.write("Error: head_bucket() failed\n")
        exit(1)
    s3_bucket = s3.Bucket(bucket)

    scene_list = []
    last_dir = ''
    if prefixList is not None:
        for prefix in prefixList:
            for s3_obj in s3_bucket.objects.filter(Prefix=prefix):
                if s3_obj.key.endswith('.h5'):
                    s3_dir = get_interval_from_dir_key(s3_obj.key)
                    s3_path = os.path.dirname(s3_obj.key)
                    if s3_dir != last_dir:
                        scene_list.append((s3_path, s3_dir))
                        last_dir = s3_dir
                elif s3_obj.key.endswith('.tar.gz'):
                    interval_id = get_interval_from_file_key(s3_obj.key)
                    scene_list.append((s3_obj.key, interval_id))
    else:
        for s3_obj in s3_bucket.objects.all():
            if s3_obj.key.endswith('.h5'):
                s3_dir = get_interval_from_dir_key(s3_obj.key)
                s3_path = os.path.dirname(s3_obj.key)
                if s3_dir != last_dir:
                    scene_list.append((s3_path, s3_dir))
                    last_dir = s3_dir
                elif s3_obj.key.endswith('.tar.gz'):
                    interval_id = get_interval_from_file_key(s3_obj.key)
                    scene_list.append((s3_obj.key, interval_id))

    return scene_list


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
    for line in file:
        # Strip comments starting with '#'
        s = line.split('#')
        # Strip trailing whitewpace (including newlines)
        url = s[0].strip()
        if len(url) == 0:
            continue
        objectList.append(url)

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


def job_prefix(uniq):
    """Return the job prefix associated with a random string.

    Args:
        A randomly-chosen string that assures uniqueness for the job prefix

    Returns:
        The job prefix (subdirectory name in the job bucket)
    """

    return 'subsetter-' + uniq


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
    cmd_array = ['sudo', '-E', '-u', 'subsetter']
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
        scene_list = get_list_from_file(args.input_job_file)
    else:
        sys.stdout.write("Gathering list of scenes ... ")
        sys.stdout.flush()
        scene_list = getS3ObjectList(args.input_bucket, prefixList)
        sys.stdout.write("done\n")

    # JDC Debug
    for (src_dir, interval) in scene_list:
        print("{} {}".format(src_dir, interval))
    exit(0)

    for (src_dir, interval) in scene_list:

        if job_file is None:
            job_file = create_job_file(uniq, batch_index)
            batch_index += 1

        url = 's3://' + args.input_bucket + '/' + src_dir
        job_file.write(url + ' ' + interval + '\n')
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
