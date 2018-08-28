#!/usr/bin/env python

import sys
import os
import boto3
import random
import string
import argparse
import subprocess
import tempfile


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
            default = 'dev-lsds-l8-test-l0rp',
            help = "Input S3 bucket (default: dev-lsds-l8-test-l0rp)")
    parser.add_argument('--job-definition',
            type = str,
            dest = 'job_definition',
            action = 'store',
            default = None,
            help = "Batch job definition")
    parser.add_argument('--package',
            dest = 'package',
            action = 'store_true',
            default = False,
            help = "Perform packaging (default: False)")
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


def validate_args(args):
    """Validate the command line arguments and check for
    environment variables where appropriate.  We make some of
    the values global because otherwise we'd have some long
    argument lists.

    Args:
        args <dict>: The parsed command line arguments
    """

    global batch_cmd
    global job_bucket
    global job_definition
    global queue

    if args.queue is not None:
        queue = args.queue
    elif 'ipsQueue' in os.environ:
        queue = os.environ['ipsQueue']
    else:
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

    if args.job_definition is not None:
        job_definition = args.job_definition
    elif 'ipsJobDefinition' in os.environ:
        job_definition = args.job_definition
    elif 'ipsJobDefinition' in os.environ:
        job_definition = os.environ['ipsJobDefinition']
    else:
        sys.stderr.write("Error: job definition not specified\n" +
                "       Must use --job-definition or set ipsJobDefinition\n")
        exit(1)
    defs = client.describe_job_definitions(jobDefinitionName=job_definition)
    if len(defs['jobDefinitions']) == 0:
        sys.stderr.write("Error: job definition {} not found\n".
                format(job_definition))
        exit(1)

    # Provide a default for the batch command
    if args.batch_cmd is not None:
        batch_cmd = args.batch_cmd
    else:
        batch_cmd = 'ips-worker.sh'


def parse_s3_object(bucket, s3_obj):
    """Parse an S3 object and return an S3 directory and product ID.

    Args:
        s3_obj <S3 object>: S3 object to be parsed

    Returns:
        (inputURL, inputProductId) (<str>, <str>):  an S3
                filename and product ID corresponding to the object
    """

    if not s3_obj.key.endswith('tar.gz'):
        return (None, None)
    inputURL = 's3://' + bucket + '/' + s3_obj.key
    inputProductId = s3_obj.key.split('/')[-1].split('.')[0]

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


def getListFromFile(filename):
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
        inputProductId = url.split('/')[-1].split('.')[0]
        objectList.append([url, inputProductId])

    file.close()
    return objectList


def formPWG(productId, inputURL, args):
    cmdConstant = ['PWG', \
            '-i', \
            '-scene', productId, \
            '-l0r_data_path', '/jobtmp/' + productId]
    cmdPackaging = ['-procedure', '"L1T with Quality Band"', \
            '-parm DFP:L1G_PACKAGE=1', \
            '-parm DFP:NAME_USING_PRODUCT_ID=1']
    cmdNoPackaging = ['-procedure', '"L1T Product"']

    cmd = cmdConstant[:]
    if args.package:
        cmd.extend(cmdPackaging)
    else:
        cmd.extend(cmdNoPackaging)

    scene_date = productId[9:16]

    # XXX Find the appropriate auxiliary data
    JDC_stuff = ['-parm DSW:CAL_PARM_FILENAME=' + 'XXX', \
            '-parm DSW:BIAS_PARM_FILENAME_OLI=' + 'XXX', \
            '-parm DSW:BIAS_PARM_FILENAME_TIRS=' + 'XXX', \
            '-parm DSW:RLUT_FILENAME=' + 'XXX']

    return cmd


def create_job_file(uniq, batch_index):

    dir = tempfile.gettempdir()
    fn = dir + '/ips-' + uniq + '-' +  str(batch_index).zfill(3) + '.jobctl'
    try:
        print("JDC: creating job file '{}'".format(fn))
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
    else:
        client = boto3.client('batch')

    job_prefix = job_file_name.split('/')[-1].split('.')[0]

    client.submit_job(
            jobName = job_prefix,
            jobQueue = queue,
            jobDefinition = job_definition,
#           parameters = {'order_url': s3_url},
            containerOverrides = {
#               'command': [batch_cmd, 'Ref::order_url']
                'command': [batch_cmd]
            },
            arrayProperties={
                'size': size
            }
    )


def main():
    """Submit an AWS batch array job.
    """

    args = parse_command_line()
    validate_args(args)

    uniq = ''.join(random.choice(string.ascii_lowercase)
            for _ in range(4))

    array_count = 0
    job_count = 0
    batch_index = 0
    job_file = None

    obj_list = getS3ObjectList(args.input_bucket, None)
    for (url, pid) in obj_list:
#       cmd = formPWG(pid, url, args)
#       try:
#           print("JDC: executing '{}'".format(' '.join(cmd)))
#           pwg_out = subprocess.check_output(cmd).strip()
#           print("JDC: PWG says '{}'".format(pwg_out))
#       except subprocess.CalledProcessError as e:
#           sys.stderr.write("Error: PWG returned {}\n".
#                   format(e.returncode))
#           exit(1)
#       work_order = XXX(pwg_out)

        if job_file is None:
            job_file = create_job_file(uniq, batch_index)
            batch_index += 1

        job_file.write(url + '\n')
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

    print("{} jobs submitted".format(job_count))


batch_cmd = None
job_definition = None
queue = None

if __name__ == '__main__':
        main()
