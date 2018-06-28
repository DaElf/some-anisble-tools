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
    cmdConstant = ['python',
            '/efs/daelf/espa-all/espa-processing/processing/espa_submit.py', \
            '--product-type', 'landsat', \
            '--output-format', 'gtiff', \
            '--bridge-mode',
            '--dist-method', 's3', \
            '--dist-s3-bucket', 'lsds-level2-data']
    cmdBasic = ['--include-top-of-atmosphere', \
            '--include-brightness-temperature', \
            '--include-surface-reflectance']
    cmdFull = [\
            '--include-surface-temperature', \
            '--include-surface-water-extent']

# this has not been ported to s3
#            '--include-statistics'

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

def getS3ObjectList(bucket, prefixList):
    """Get a list of objects in an S3 bucket

    Get a list of objects in an S3 bucket that have prefixes that
    match those in the given list.  It's actually faster to get a
    list of all the objects in the bucket by iterating through all
    the prefixes, so we just do that.

    Args:
        bucket <str>: input bucket name
        prefixList <list>: list of prefixes (e.g. [L7, L8])

    Returns:
        List of the objects in the S3 bucket that start with
        one of the given prefixes.
    """

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    objectList = []
    for prefix in prefixList:
        for object in my_bucket.objects.filter(Prefix=prefix):
            inputUrl = 's3://' + object.bucket_name + '/' + object.key
            inputProductId = object.key.split('/')[-1].split('.')[0]
            objectList.append([inputUrl, inputProductId])

    return objectList

def getPrefixListFromFile(prefixfile):
    try:
        with open(prefixfile) as file:
            prefixList = [line.rstrip() for line in file]
        return prefixList
    except IOError:
        return None

def getListFromFile(filename):
    try:
        file = open(filename)
    except IOError:
        sys.stderr.write("Error: Can't open input file {}\n".format(filename))
        exit(1)

    objectList = []
    for line in file:
        # Strip comments starting with '#'
        s = line.split('#')
        # Strip trailing whitewpace (including newlines)
        url = s[0].strip()
        if len(url) == 0:
            continue
        inputProductId = url.split('/')[-1].split('.')[0]
        objectList.append([url, inputProductId])

    file.close()
    return objectList
