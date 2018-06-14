import boto3, random, string, json

def formMessage(inputproduictid, inputurl, queueurl, messagegroupid):
    orderId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=21))
    inputProductId = inputproduictid
    inputUrl = inputurl
    queueUrl = queueurl
    messageGroupId = messagegroupid
    messageDict = {}
    messageDict["orderId"] = orderId
    messageDict["inputProductId"] = inputProductId
    messageDict["inputUrl"] = inputUrl
    messageDict["queueUrl"] = queueUrl
    messageDict["messageGroupId"] = messageGroupId
    jsonMessage = json.dumps(messageDict)

    return jsonMessage

def getS3ObjectList(bucket, prefix, prefixlist=None):
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    objectList = []
    if prefixlist:      
        for object in my_bucket.objects.all():
            for item in prefixlist:
                inputProductId = object.key.split('/')[-1].split('.')[0]
                if inputProductId == item:
                    inputUrl = 's3://' + object.bucket_name + '/' + object.key
                    objectList.append([inputUrl, inputProductId])
    else:
        for object in my_bucket.objects.filter(Prefix=prefix):
            inputUrl = 's3://' + object.bucket_name + '/' + object.key
            inputProductId = object.key.split('/')[-1].split('.')[0]
            objectList.append([inputUrl, inputProductId])
    
    return objectList

def getPrefixListFromFile(prefixfile):
    file = open(prefixfile)
    prefixList = file.readlines()
    return prefixList
