import boto3, random, string, json, uuid
from sqsPublisherHelpers import formMessage, getS3ObjectList, getPrefixListFromFile

prefixListTestFile = './prefixlist.txt'
prefix = 'L7'
queueUrl = 'https://sqs.us-west-2.amazonaws.com/707566951618/mvp-test-SQSBatchQueue-3GDM5V1SE6SS.fifo'
functionName = 'sqs_level1_processing_message'
sqsClient = boto3.client("sqs")
lambdaClient = boto3.client("lambda")

prefixList = getPrefixListFromFile(prefixListTestFile)
if len(prefixList) == 0:
    prefixList = [prefix]
sentMessageCount = 0
print("Sending messages...")
for s3Obj in getS3ObjectList('lsaa-level1-data', prefixList, None)[:5500]:
    inputUrl = s3Obj[0]
    inputId = s3Obj[1]
    messageGroupId = str(random.getrandbits(128))
    print(inputUrl + " : " + inputId)
    response = lambdaClient.invoke(
        FunctionName=functionName,
        InvocationType='Event',
        ClientContext='json',
        Payload=formMessage(inputId, inputUrl, queueUrl, messageGroupId)
    )
    sentMessageCount = sentMessageCount + 1
    
print("All messages sent.")
