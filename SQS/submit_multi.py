#!/usr/bin/env python

import sys
import os
import subprocess
import random
import string
import json
import argparse

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
    parser.add_argument('--batch',
            dest = 'batch',
            action = 'store_true',
            default = False,
            help = "Submit jobs to batch queue (default: submit to SQS queue)")
    parser.add_argument('--bucket',
            type = str,
            dest = 'bucket',
            action = 'store',
            default = 'lsaa-level1-data',
            help = "Input S3 bucket (default: lsaa-level1-data)")
    parser.add_argument('--job-file',
            type = str,
            dest = 'job_file_name',
            action = 'store',
            default = None,
            help = "File of input file names to submit")
    parser.add_argument('--full',
            dest = 'full_job',
            action = 'store_true',
            default = False,
            help = "Submit jobs specifying all products")
    parser.add_argument('--prefix',
            type = str,
            dest = 'prefix',
            action = 'store',
            default = None,
            help = "Prefix of S3 input files (default: L7)")
    parser.add_argument('--queue',
            dest = 'queue',
            type = str,
            action = 'store',
            default = None,
            help = "SQS or batch queue to submit jobs in")

    args = parser.parse_args()

    return args


def validate_args(args):
    if args.prefix is None and \
            args.job_file_name is None:
        sys.stderr.write("Error: must specify either " +
                "--prefix or --job-file\n")
        sys.exit(1)
    if args.prefix is not None and \
            args.job_file_name is not None:
        sys.stderr.write("Error: cannot specify both " +
                "--prefix and --job-file\n")
        sys.exit(1)


def main():
    orderPrefix = 'espa-' + \
            ''.join(random.choice(string.ascii_lowercase) for _ in range(4)) + \
            '-'
    orderNo = 1

    args = parse_command_line()
    validate_args(args)

    count = args.count
    queue = args.queue
    if queue is None and 'AWSQueue' in os.environ:
        queue = os.environ['AWSQueue']
    if queue is None:
        sys.stderr.write("Error: queue not specified\n" +
                         "       Must set AWSQueue or use --queue\n")
        exit(1)

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
        objectList = getS3ObjectList(args.bucket, prefixList)
        if count == 0:
            count = 1

    if len(objectList) == 0:
        sys.stderr.write("Error: no input files selected\n")
        exit(1)

    if len(objectList) < count:
        count = len(objectList)
        print("Note: Only {} input {f} available".format(
                count, f = 'file' if count == 1 else 'files'))

    print("Queuing {} {j}".format(count, j = 'job' if count == 1 else 'jobs'))
    sentMessageCount = 0
    for s3Obj in objectList[:count]:
        inputUrl = s3Obj[0]
        inputId = s3Obj[1]
        print(inputUrl + ' : ' + inputId)

        cmd = formCmd(orderPrefix + str(orderNo).zfill(5), inputId, inputUrl,
                queue, args.full_job, args.batch)
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


if __name__ == '__main__':
    main()

