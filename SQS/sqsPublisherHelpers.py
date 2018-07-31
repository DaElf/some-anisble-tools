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


def formCmd(orderNo, productId, inputURL, queue, prefix, args):
    cmdConstant = ['espa_submit.py', \
            '--product-type', 'landsat', \
            '--output-format', 'gtiff', \
            '--bridge-mode',
            '--dist-method', 's3', \
            '--dist-s3-bucket', 'lsds-level2-data', \
            '--no-submit', \
            '--s3-job-prefix', prefix]
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
    if args.full_job:
        cmd.extend(cmdFull)
    cmd.extend(['--order-id', orderNo])
    cmd.extend(['--input-url', inputURL])
    cmd.extend(['--input-product-id', productId])
    cmd.extend(['--queue', queue])
    if args.batch_cmd:
        cmd.extend(['--batch-command', args.batch_cmd])

    return cmd


def parse_s3_object(s3_obj, blacklist):
    """Parse an S3 object and return an S3 URL and product ID.

    Args:
        s3_obj <S3 object>: S3 object to be parsed
        blacklist <list>: List of product IDs to skip

    Returns:
        (inputURL, inputProductId) (<str>, <str>):  an S3
                URL and product ID corresponding to the object
    """

    inputUrl = 's3://' + s3_obj.bucket_name + '/' + s3_obj.key
    inputProductId = s3_obj.key.split('/')[-1].split('.')[0]

    # Get the path/row and check the value of the row.
    # Ascending (nighttime) scenes have rows greater
    # than 120.  We can't generate surface reflectance
    # for them, so we don't add them to the list.
    prod_split = inputProductId.split('_')
    if len(prod_split) < 3:
        return (None, None)
    path_row = prod_split[2]
    row = int(path_row[3:6])
    if row > 120:
        return (None, None)
    if prod_split[1] == 'L1GT':
        return (None, None)

    if blacklist is not None:
        if inputProductId in blacklist:
            return (None, None)

    return (inputUrl, inputProductId)


def getS3ObjectList(bucket, prefixList, blacklist):
    """Get a list of objects in an S3 bucket

    Get a list of objects in an S3 bucket, either by using a
    list of prefixes, or listing all the objects in the bucket.

    Args:
        bucket <str>: input bucket name
        prefixList <list>: list of prefixes (e.g. [L7, L8])
        blacklist <list>: list of product IDs to skip

    Returns:
        List of the objects in the S3 bucket that start with
        one of the given prefixes.
    """

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    objectList = []
    if prefixList is not None:
        for prefix in prefixList:
            for s3_obj in my_bucket.objects.filter(Prefix=prefix):
                (inputUrl, inputProductId) = parse_s3_object(s3_obj, blacklist)
                if inputUrl is not None:
                    objectList.append([inputUrl, inputProductId])
    else:
        for s3_obj in my_bucket.objects.all():
            (inputUrl, inputProductId) = parse_s3_object(s3_obj, blacklist)
            if inputUrl is not None:
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
