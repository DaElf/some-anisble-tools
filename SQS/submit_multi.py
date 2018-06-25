#!/usr/bin/env python

import sys
import os
import subprocess
import boto3
import random
import string
import json
import uuid
import argparse

from sqsPublisherHelpers import formMessage, formCmd, getS3ObjectList, getPrefixListFromFile

def parse_command_line():
    """Parse the command line

    Returns:
        args <Namespace>: the arguments from the command line
    """

    parser = argparse.ArgumentParser(
            description = "Submit ESPA jobs for processing")
    parser.add_argument('count',
            type=int,
            action = 'store',
            default = 1,
            help='Number of jobs to submit (default: 1)')
    parser.add_argument('--batch',
            dest = 'batch',
            action = 'store_true',
            default = False,
            help = "Submit jobs to batch queue (default: submit to SQS queue")
    parser.add_argument('--full',
            dest = 'full_job',
            action = 'store_true',
            default = False,
            help = "Submit jobs specifying all products")
    parser.add_argument('--queue',
            dest = 'queue',
            type=str,
            action = 'store',
            default = None,
            help = "SQS or batch queue to submit jobs in")

    args = parser.parse_args()

    return args


orderNo=random.randint(1000000, 9999999)

args = parse_command_line()
count = args.count

queue = args.queue
if queue is None and 'AWSQueue' in os.environ:
    queue = os.environ['AWSQueue']
if queue is None:
    sys.stderr.write("Error: queue not specified\n" +
                     "       Must set AWSQueue or use --queue\n")
    exit(1)

prefixListTestFile = './prefixlist.txt'
prefix = 'L7'

prefixList = getPrefixListFromFile(prefixListTestFile)
sentMessageCount = 0

print("Queuing {} {j}".format(count, j = "job" if count == 1 else "jobs"))
for s3Obj in getS3ObjectList('lsaa-level1-data', prefix, prefixlist=prefixList)[:count]:
    inputUrl = s3Obj[0]
    inputId = s3Obj[1]
    print(inputUrl + " : " + inputId)

    cmd = formCmd("jdc-test-" + str(orderNo), inputId, inputUrl,
            queue, args.full_job, args.batch)
    orderNo += 1
    print("Issuing command: " + " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("Fatal error: espa_submit.py returned " +
                str(e.returncode) + "\n")

    sentMessageCount += 1

print("{} {j} queued".format(sentMessageCount,
        j = "job" if sentMessageCount == 1 else "jobs"))
