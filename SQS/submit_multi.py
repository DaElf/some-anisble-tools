#!/usr/bin/env python

import sys
import os
import subprocess
import random
import string
import json
import boto3
import argparse

from sqsPublisherHelpers import formCmd, getS3ObjectList, getListFromFile
from submit_array import parse_command_line, validate_args


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


def main():
    orderPrefix = '' + \
            ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
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

    if args.job_file_name is not None:
        objectList = getListFromFile(args.job_file_name)
        if count == 0:
            count = len(objectList)
    else:
        print("Getting list of scenes from S3 bucket {} ...".format(
                args.input_bucket))
        objectList = getS3ObjectList(args.input_bucket, prefixList, blacklist)
        if count == 0:
            count = 1

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
    sentMessageCount = 0
    for s3Obj in objectList[:count]:
        inputUrl = s3Obj[0]
        inputId = s3Obj[1]

        orderId = orderPrefix + '-' + str(orderNo).zfill(5)
        print(orderId + ' : ' + inputUrl)

        cmd = formCmd(orderId, inputId, inputUrl, queue,
                orderPrefix, None, args)
        orderNo += 1
        # JDC Debug
        print("Issuing command: " + " ".join(cmd))
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            sys.stderr.write("Error: espa-submit returned {}\n".format(
                    e.returncode))
            exit(1)

        sentMessageCount += 1

    print("{} {j} queued".format(sentMessageCount,
            j = 'job' if sentMessageCount == 1 else 'jobs'))


batch_cmd = None
job_bucket = None
job_definition = None
queue = None

if __name__ == '__main__':
    main()
