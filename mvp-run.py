#!/usr/bin/env python
# Copyright 2016 Amazon.com, Inc. or its
# affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not
# use this file except in compliance with the License. A copy of the License is
# located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import print_function
import os
import sys
import json
import urllib
import boto3
import ntpath
from subprocess import call
from PIL.ExifTags import TAGS
from pprint import pprint


tmpdir = '/tmp/JDC-work'
try:
    sqsqueue_name = os.environ['SQSBatchQueue']
except KeyError as e:
    print("Error: environment variable SQSBatchQueue not defined")
    exit(1)

try:
    aws_region = os.environ['AWSRegion']
except KeyError:
    s3 = boto3.client('s3')
    sqs = boto3.resource('sqs')
else:
    s3 = boto3.client('s3', region_name=aws_region)
    sqs = boto3.resource('sqs', region_name=aws_region)


def process_scene():
    """Process a scene

    Read a JSON-encoded message from the SQS queue, create a command
    corresonding to the parameters in the message, and call cli.py.

    Requires the environment variable SQSBatchQueue to provide the
    name of the SQS queue to watch.

    In case of error we'll delete the message from the queue and continue.

    """
    for message in get_messages_from_sqs():
        try:
            message_content = json.loads(message.body)
            pprint(message_content)
            order_id = message_content['order-id']
            product_type = message_content['product-type']
            product = message_content['input-product-id']
            output_format = message_content['output-format']
            top_of_atmosphere = message_content['include-top-of-atmosphere']
            brightness_temperature = message_content \
                ['include-brightness-temperature']
            surface_reflectance = message_content \
                ['include-surface-reflectance']
            bridge_mode = message_content ['bridge-mode']
            input_url = urllib.unquote_plus(message_content
                ['input-url']).encode('utf-8')

            cmd = '/usr/bin/cli.py' + \
                    ' --order-id ' + order_id + \
                    ' --product-type ' + product_type + \
                    ' --input-product-id ' + product + \
                    ' --output-format ' + output_format + \
                    ' --input-url ' + input_url

            if top_of_atmosphere:
                cmd += ' --include-top-of-atmosphere'
            if brightness_temperature:
                cmd += ' --include-brightness-temperature'
            if surface_reflectance:
                cmd += ' --include-surface-reflectance'
            if bridge_mode:
                cmd += ' --bridge-mode'

            print("Issuing command: " + cmd)
            call(cmd, shell=True)
        except KeyError as e:
            print("Can't parse input message: missing " + str(e))
            message.delete()
            continue
        except Exception as e:
            print(e)
            message.delete()
            continue
        else:
            message.delete()


def get_messages_from_sqs():
    queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)
    message = queue.receive_messages(VisibilityTimeout=120,
            WaitTimeSeconds=20,
            MaxNumberOfMessages=1)
    return(message)


def create_dirs():
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)


def main():

    create_dirs()
    while True:
        process_scene()


if __name__ == "__main__":
    main()
