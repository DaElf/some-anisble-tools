import boto3
import pprint


def parse_s3_url(url):
    """Parse an S3 URL

    Args:
        url <string>: A URL in the form s3://<bucket>/<key>

    Returns:
        (bucket, key) (<str>, <str>): A tuple with the S3 bucket and key
    """

    u_list = url.split('/')

    if len(u_list) < 4 or \
            u_list[0] != 's3:' or \
            u_list[1] != '':
        sys.stderr.write("Error: Badly formed URL: {}\n".format(url))
        exit(1)

    return(u_list[2], '/'.join(u_list[3:]))


def list_bucket(bucket, prefix, exclude=None):
    """List the files in a bucket that start with the given prefix.

    Args:
        bucket <str>: The bucket name
        prefix <str>: The prefix for the files to list
        exclude <str>: File name (not including prefix) to exclude

    Returns:
        file_list <list>: A list of the files in the bucket
    """

    client = boto3.client('s3')
    s3_files = client.list_objects(Bucket=bucket, Prefix=prefix)

    file_list = []
    for fobj in s3_files['Contents']:
        if exclude is not None and fobj['Key'].endswith(exclude):
            continue
        file_list.append(fobj['Key'])

    # JDC debug
#   pp = pprint.PrettyPrinter(indent=4)
#   pp.pprint(file_list)

    return file_list
