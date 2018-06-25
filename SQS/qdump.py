#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import json
import boto3
import argparse


def parse_command_line():

    parser = argparse.ArgumentParser(
            description = "Read messages from an SQS queue")
    parser.add_argument('--count',
            dest = 'count',
            action = 'store',
            type = int,
            default = 1,
            help = 'Number of messages to read (default: 1)')
    parser.add_argument('--msg-timeout',
            dest = 'timeout',
            action = 'store',
            type = int,
            default = 20,
            help = 'Timeout for reading SQS queue (default: 20)')
    parser.add_argument('--no-wait',
            dest = 'no_wait',
            action = 'store_true',
            default = False,
            help = 'Quit if no messages are on the queue')
    parser.add_argument('--peek',
            dest = 'peek_flag',
            action = 'store_true',
            default = False,
            help = "Don't delete messages from the queue after they're read (default: delete messages)")
    parser.add_argument('--queue',
            dest = 'queue_name',
            action = 'store',
            default = None,
            help = 'Name of the SQS queue to read (default: look for environment variable SQSQueue')

    args = parser.parse_args()

    return args


def get_message_from_sqs(queue_name, timeout, count):

    if aws_region is None:
        sqs = boto3.resource('sqs')
    else:
        sqs = boto3.resource('sqs', region_name=aws_region)

    queue = sqs.get_queue_by_name(QueueName=queue_name)
    message = queue.receive_messages(WaitTimeSeconds=timeout,
            MaxNumberOfMessages=count)

    return(message)


def main():

    args = parse_command_line()

    if args.queue_name is None:
        try:
            queue_name = os.environ['SQSQueue']
        except KeyError as e:
            sys.stderr.write("Error: environment variable SQSQueue not defined\n")
            sys.exit(1)
    else:
        queue_name = args.queue_name

    messages = get_message_from_sqs(queue_name,
            0 if args.no_wait else int(args.timeout),
            int(args.count))
    for message in messages:
        try:
            message_content = json.loads(message.body)
            print(json.dumps(message_content, sort_keys=True,
                    indent=4, separators=(',', ': ')))
        except Exception as e:
            sys.stderr.write("Error: " + str(e))
        if not args.peek_flag:
            message.delete()


try:
    aws_region = os.environ['AWSRegion']
except KeyError:
    aws_region = None

if __name__ == "__main__":
    main()
