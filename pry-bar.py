#!/usr/bin/env python

import boto3
#import random 
import random as stdlib_random
import string 
import json
#from random import choice

def formMessage():
   #orderId = ''.join(stdlib_random.choices(string.ascii_uppercase + string.digits, k=21))
   orderId = 'Toast'
   inputProductId = 'LE07_L1GT_043036_20030217_20160927_01_T2.tar.gz'
   inputUrl = 's3://lsaa-level1-data/L7/2003/043/036/LE07_L1GT_043036_20030217_20160927_01_T2.tar.gz'
   queueUrl = 'https://sqs.us-west-2.amazonaws.com/707566951618/SQSBatchQueuedaelf'
   
   messageDict = {}
   messageDict["orderId"] = orderId
   messageDict["inputProductId"] = inputProductId
   messageDict["inputUrl"] = inputUrl
   messageDict["queueUrl"] = queueUrl
   jsonMessage = json.dumps(messageDict)

   return jsonMessage

sqsClient = boto3.client("sqs")

lambdaClient = boto3.client("lambda")
for i in range(1):
   response = lambdaClient.invoke(
       FunctionName='sqs_level1_processing_message',
       InvocationType='Event',
       ClientContext='json',
       Payload=formMessage()
   )
