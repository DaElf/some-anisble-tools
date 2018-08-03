#!/usr/bin/env python

import sys
import os
import subprocess
import random
import string
import json
import argparse
import boto3
import time

import config_utils as config
import cli
from submitHelpers import parse_s3_url, list_bucket
from sqsPublisherHelpers import formCmd, getS3ObjectList, getListFromFile


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
    parser.add_argument('--blacklist',
            dest = 'blacklist',
            action = 'store',
            default = None,
            help = "File with list of product IDs to avoid")
    parser.add_argument('--full',
            dest = 'full_job',
            action = 'store_true',
            default = False,
            help = "Submit jobs specifying all products")
    parser.add_argument('--input-bucket',
            type = str,
            dest = 'input_bucket',
            action = 'store',
            default = 'lsaa-level1-data',
            help = "Input S3 bucket (default: lsaa-level1-data)")
    parser.add_argument('--job-bucket',
            type = str,
            dest = 'job_bucket',
            action = 'store',
            default = None,
            help = "S3 bucket to hold job information")
    parser.add_argument('--job-definition',
            type = str,
            dest = 'job_definition',
            action = 'store',
            default = None,
            help = "Batch job definition")
    parser.add_argument('--input-job-file',
            type = str,
            dest = 'job_file_name',
            action = 'store',
            default = None,
            help = "File of input file names to submit")
    parser.add_argument('--list-only',
            dest = 'list_only',
            action = 'store_true',
            default = False,
            help = "Just create a list of scenes, don't submit a job")
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

    # We need to validate these variables at the
    # start because espa-submit will write files
    # to the job bucket and we want to be sure we'll
    # be able to submit the job.
    if not args.list_only:
        if args.queue is not None:
            queue = args.queue
        elif 'espaQueue' in os.environ:
            queue = os.environ['espaQueue']
        else:
            sys.stderr.write("Error: queue not specified\n" +
                             "       Must use --queue or set espaQueue\n")
            exit(1)
        client = boto3.client('batch')
        job_queues = client.describe_job_queues(jobQueues=[queue])
        if len(job_queues['jobQueues']) == 0:
            sys.stderr.write("Error: queue {} not found\n".format(queue))
            exit(1)

        if args.job_definition is not None:
            job_definition = args.job_definition
        elif 'espaJobDefinition' in os.environ:
            job_definition = os.environ['espaJobDefinition']
        else:
            sys.stderr.write("Error: job definition not specified\n" +
                             "       Must use --job-definition or set espaJobDefinition\n")
            exit(1)
        defs = client.describe_job_definitions(jobDefinitionName=job_definition)
        if len(defs['jobDefinitions']) == 0:
            sys.stderr.write("Error: job definition {} not found\n".
                    format(job_definition))
            exit(1)

        if args.job_bucket is not None:
            job_bucket = args.job_bucket
        elif 'espaJobBucket' in os.environ:
            job_bucket = os.environ['espaJobBucket']
        else:
            sys.stderr.write("Error: job bucket not specified\n" +
                             "       Must use --job-bucket or set espaJobBucket\n")
            exit(1)
        client = boto3.client('s3')
        try:
            acl = client.get_bucket_acl(Bucket=job_bucket)
        except Exception:
            sys.stderr.write("Error: job bucket {} not found\n".
                format(job_bucket))
            exit(1)

    # Provide a default for the batch command
    if args.batch_cmd is not None:
        batch_cmd = args.batch_cmd
    else:
        batch_cmd = 'espa-worker.sh'


def create_job_control_file(prefix, n):
    """Open a job control file for writing

    Args:
        n <int>: index for a suffix

    Returns:
        filename <str>: the name of the new file
        file <file>: the file object
    """

    fn = '/tmp/' + prefix + '-' + str(n).zfill(3) + '.jobctl'
    try:
        file = open(fn, 'w')
    except IOError as e:
        sys.stderr.write("Error: can't create batch array file {}: {}\n".format(
                fn, e))
        exit(1)

    return (fn, file)


def submit_job(job_prefix, job_file_name, size):
    """Submit an array job to the AWS batch queue

    Args:
        job_prefix <str>: The prefix of the job/order name
        job_file_name <str>: The name of the file with the job array
        size <int>:  The number of jobs in the array
    """

    s3_key = job_prefix + '/' + job_file_name.split('/')[-1]
    s3_client = boto3.client('s3')
    s3_client.upload_file(job_file_name, job_bucket, s3_key)
    s3_url = 's3://' + job_bucket + '/' + s3_key

    client = boto3.client('batch')

    client.submit_job(
            jobName = s3_key.split('/')[-1].split('.')[0],
            jobQueue = queue,
            jobDefinition = job_definition,
            parameters = {'order_url': s3_url},
            containerOverrides = {
                'command': [batch_cmd, 'Ref::order_url']
            },
            arrayProperties={
                'size': size
            })


def set_up_first_job(orderId, inputId, inputUrl, queue, orderPrefix, args):
    """Call espa-submit to set up the first job.  Espa-submit will
    create the JSON version of the order and write it to the job
    bucket.  It will also copy processing.conf to the job bucket.

    For the second and subsequent jobs, we'll modify the order
    dictionary and use it to create the JSON file.

    Args:
        orderId <str>: The order ID
        inputId <str>: The input product ID
        inputUrl <str>: The URL of the input file
        queue <str>: The queue for the job (not used)
        orderPrefix <str>: The prefix of the order
        args <dict>: A dictionary with the command-line arguments

    Returns:
        (order_file_url, order) (<str>, <dict>: A tuple with the
                URL returned by espa-submit and the JSON-encoded order
    """

    extra_switches = ['--no-submit',
            '--s3-job-prefix', orderPrefix,
            '--job-bucket', job_bucket]
    cmd = formCmd(orderId, inputId, inputUrl, queue,
            orderPrefix, extra_switches, args)
    # JDC Debug
#   print("Issuing command: " + " ".join(cmd))
    try:
        order_file_url = subprocess.check_output(cmd).strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Error: espa-submit returned {}\n".format(
                e.returncode))
        exit(1)

    (bucket, s3_key) = parse_s3_url(order_file_url)
    client = boto3.client('s3')
    waiter = client.get_waiter('object_exists')
    try:
        waiter.wait(Bucket=bucket, Key=s3_key)
    except Exception as e:
        sys.stderr.write("Error: Can't find S3 JSON object: {}\n".format(e))
        sys.exit(1)

    s3 = boto3.resource('s3').Bucket(job_bucket)
    try:
        json.load_s3 = lambda f: json.load(s3.Object(key=f).get()['Body'])
        order = json.load_s3(s3_key)
    except Exception as e:
        sys.stderr.write("Error: Can't load S3 JSON object: {}\n".format(e))
        sys.exit(1)

    return (order_file_url, order)


def main():
    """Submit an AWS batch array job.

    This code originally called espa-submit to create the JSON
    for each job.  But it takes espa-submit almost a second to
    get started, so that was too slow.  We call espa-submit for
    the first job to get the JSON file, then we modify the JSON
    for each subsequent job.
    """

    orderPrefix = ''.join(random.choice(string.ascii_lowercase)
            for _ in range(4))
    orderNo = 1

    args = parse_command_line()
    validate_args(args)

    count = args.count

    if args.blacklist is not None:
        try:
            f = open(args.blacklist, 'r')
        except Exception as e:
            sys.stderr.write("Error: can't open blacklist file {}: {}\n".format(
                    args.blacklist, e))
            exit(1)
        blacklist = f.read().split()
        f.close()
    else:
        blacklist = None

    if args.prefix is not None:
        prefixList = []
        prefixes = args.prefix.split(',')
        for prefix in prefixes:
            prefixList.append(prefix)
    else:
        prefixList = None

    if args.job_file_name is not None:
        objectList = getListFromFile(args.job_file_name)
        if count == 0:
            count = len(objectList)
    else:
        if not args.list_only:
            print("Getting list of scenes from S3 bucket {} ...".format(
                    args.input_bucket))
        objectList = getS3ObjectList(args.input_bucket, prefixList, blacklist)
        if count == 0:
            count = 1
    if count < 2:
        sys.stderr.write("Error: the minimum number of entries in an array job is 2\n")
        exit(1)


    if len(objectList) == 0:
        sys.stderr.write("Error: no input files selected\n")
        exit(1)

    if len(objectList) < count:
        count = len(objectList)
        print("Note: Only {} input {f} available".format(
                count, f = 'file' if count == 1 else 'files'))

    if args.list_only:
        for s3Obj in objectList[:count]:
            print(s3Obj[0])
        sys.exit(0)

    print("Queuing {} {j}".format(count, j = 'job' if count == 1 else 'jobs'))

    job_count = 0
    batch_index = 1
    (filename, file) = create_job_control_file(orderPrefix, batch_index)
    s3_client = boto3.client('s3')
    for s3Obj in objectList[:count]:
        inputUrl = s3Obj[0]
        inputId = s3Obj[1]

        orderId = orderPrefix + '-' + str(orderNo).zfill(5)
        print(orderId + ' : ' + inputUrl)

        # The first time through, use espa-submit to
        # set up the basic order
        if job_count == 0 and batch_index == 1:
            (order_file_url, order) = set_up_first_job(orderId,
                    inputId, inputUrl, queue, orderPrefix, args)
            (bucket, key) = parse_s3_url(order_file_url)
            key_prefix = '/'.join(key.split('/')[:-2])
            file_copy_list = list_bucket(bucket,
                    orderPrefix + '/' + orderId,
                    exclude=orderId + '.json')
            file.write(order_file_url + '\n')
            job_count += 1
            orderNo +=1
            continue

        # After the first time, modify the order we got
        # from expa-submit and write it to the job bucket.
        # Copy any files we need from the job espa-submit created
        order['orderid'] = orderId
        order['product_id'] = inputId
        order['download_url'] = inputUrl
        order['scene'] = inputId
        order['orderid'] = orderId
        order_key = key_prefix + '/' + orderId +  '/' + \
                orderId + '.json'
        s3_client.put_object(Bucket=job_bucket,
                Body=json.dumps(order),
                Key=order_key)

        # Copy any necessary files from espa-submit's bucket
        for s3_obj in file_copy_list:
            obj_split = s3_obj.split('/')
            dest_key = key_prefix + '/' + orderId + '/' + obj_split[-1]
            s3_client.copy_object(Bucket=job_bucket,
                    CopySource={'Bucket': job_bucket, 'Key': s3_obj},
                    Key=dest_key)

        # Write the URL to the job control file
        order_file_url = 's3://' + job_bucket + '/' + order_key
        file.write(order_file_url + '\n')
        job_count += 1
        orderNo +=1

        if (job_count == 10000):
            file.close()
            submit_job(orderPrefix, filename, job_count)
            os.unlink(filename)
            job_count = 0
            batch_index += 1
            (filename, file) = create_job_control_file(orderPrefix, batch_index)

    if (job_count > 0):
        file.close()
        submit_job(orderPrefix, filename, job_count)
        os.unlink(filename)

    print("{} {j} queued".format(job_count,
            j = 'job' if job_count == 1 else 'jobs'))


batch_cmd = None
job_bucket = None
job_definition = None
queue = None

if __name__ == '__main__':
    main()

