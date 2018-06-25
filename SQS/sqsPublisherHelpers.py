import boto3, random, string, json


def load_template():
    filename = './order_template.json'

    with open(filename, 'r') as template_fd:
        contents = template_fd.read()

        if not contents:
            raise BadTemplateError(filename)

    template = json.loads(contents)
    return template


def formMessage(orderNo, inputproduictid, inputurl, messagegroupid):
    messageDict = load_template()

    orderId = 'Test' + str(orderNo)
    inputProductId = inputproduictid
    inputUrl = inputurl
    messageGroupId = messagegroupid
    messageDict['orderid'] = orderId
    messageDict['product_type'] = 'landsat'
    messageDict['product_id'] = inputProductId
    messageDict['download_url'] = inputurl
    messageDict['messageGroupId'] = messageGroupId
    messageDict['dist_method'] = 's3'
    messageDict['options']['dist_s3_bucket'] = 'lsds-level2-data'
    messageDict['bridge_mode'] = True
    messageDict['scene'] = inputProductId
    messageDict['include_sr_toa'] = True
    messageDict['include_sr_thermal'] = True
    messageDict['include_sr'] = True
    jsonMessage = json.dumps(messageDict)

    return jsonMessage


def formCmd(orderNo, productId, inputURL, queue, full, batch):
    cmdConstant = ['espa-submit',
            '--product-type', 'landsat', \
            '--output-format', 'gtiff', \
            '--bridge-mode',
            '--dist-method', 's3', \
            '--dist-s3-bucket', 'lsds-level2-data']
    cmdBasic = ['--include-top-of-atmosphere', \
            '--include-brightness-temperature', \
            '--include-surface-reflectance']
    cmdFull = ['--include-pixel-qa', \
            '--include-customized-source-data', \
            '--include-surface-temperature', \
            '--include-sr-evi', \
            '--include-sr-msavi', \
            '--include-sr-nbr', \
            '--include-sr-nbr2', \
            '--include-sr-ndmi', \
            '--include-sr-ndvi', \
            '--include-sr-savi', \
            '--include-surface-water-extent', \
            '--include-statistics']

    cmd = cmdConstant[:]
    cmd.extend(cmdBasic)
    if full:
        cmd.extend(cmdFull)
    cmd.extend(['--order-id', orderNo])
    cmd.extend(['--input-url', inputURL])
    cmd.extend(['--input-product-id', productId])
    cmd.extend(['--queue', queue])
    if batch:
        cmd.append('--batch')

    return cmd

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
