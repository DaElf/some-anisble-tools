#! /usr/bin/env python


import sys
import boto3
import datetime
import dateutil.parser
import calendar
import argparse
import time


def parse_command_line():
    """Parse the command line arguments
    """

    parser = argparse.ArgumentParser(
            description = "Search AWS logs for IPS processing errors")
    parser.add_argument('--start-time',
            type = str,
            dest = 'start_time',
            action = 'store',
            default = None,
            help = "Start time for search")
    parser.add_argument('--end-time',
            type = str,
            dest = 'end_time',
            action = 'store',
            default = None,
            help = "End time for search")
    parser.add_argument('--log-stream-prefix',
            type = str,
            dest = 'log_stream_prefix',
            action = 'store',
            default = 'ips-devel-batch-IPS_ProcessJob',
            help = "Prefix of log stream to search (default: ips-devel-batch-IPS_ProcessJob)")

    args = parser.parse_args()

    return args


def classify_failure(message):
    """Look for a reason for a failure by looking for a string
    in the message.  Return a string with the reason, or None
    if we don't know what it was.
    """

    failure_types = [
            ("Missing OLI BPF file", "Error: can't find BPF_OLI"),
            ("Missing TIRS BPF file", "Error: can't find BPF_TIRS"),
            ("Missing CPF file", "Error: can't find CPF"),
            ("Missing RLUT file", "Error: can't find RLUT"),
            ("Invalid tar file", "tar: Unexpected EOF in archive"),
            ("Tar file download failed", "download failed"),
            ("S3 slow down", "error occurred (SlowDown)"),
            ("S3 time-out", "The read operation timed out"),
            ("S3 client error", "botocore.exceptions.ClientError"),
            ("Incompelete S3 read", "IncompleteRead(0 bytes read)"),
            ("Error exit", "exit 1"),
            ("Exception", "Exception")
    ]

    for (reason, err_string) in failure_types:
        if message.find(err_string) != -1:
            return reason

    return None


def search_log(client, group, log_stream, startTime=None, endTime=None):
    """Search a log stream for an occurrence of the given error string.
    Print a message for each error we find.
    """

    done = False
    next_token = ''
    exit_code = 0
    productId = None
    stream = log_stream['logStreamName']

    err_strings = ['Error:', 
            'tar: Unexpected EOF in archive',
            'botocore.exceptions.ClientError',
            'download failed',
            'The read operation timed out',
            'IncompleteRead(0 bytes read)']
    exit_string = '+ exit '

    while not done:
        if next_token != '':
            events = client.get_log_events(
                    logGroupName=group,
                    logStreamName=stream,
                    nextToken=next_token)
        else:
            events = client.get_log_events(
                    logGroupName=group,
                    logStreamName=stream)

        for event in events['events']:
            msg = event['message']
            if msg.find('product=') >= 0:
                productId = msg.split('=')[-1]
            for err_string in err_strings:
                if msg.find(err_string) != -1:
                    reason = classify_failure(msg)
                    if reason is not None:
                        print("Error detected ({}):".format(reason))
                    else:
                        print("Error detected:")
                    if productId is not None:
                        print("    " + productId)
                    print("    " + stream)
                    return 1

                if msg.find(exit_string) != -1:
                    exit_code = int(msg.split(' ')[-1])
                    if exit_code != 0:
                        print("Error exit code {}:".format(exit_code))
                        if productId is not None:
                            print("    " + productId)
                        print("    " + stream)
                    return exit_code

        if 'nextToken' in events:
            next_token = events['nextToken']
        else:
            done = True

        print("Error detected (job did not complete):")
        if productId is not None:
            print("    " + productId)
        print("    " + stream)
        return 1

    return exit_code


def search_log_streams(group, prefix, startTime=None, endTime=None):
    """Search the streams in a log group for occurrences of
    the given error string.
    """

    done = False
    stream_count = 0
    error_exit_count = 0
    next_token = ''
    client = boto3.client('logs')
    while not done:
        try:
            if next_token != '':
                streams = client.describe_log_streams(
                        logGroupName=group,
                        logStreamNamePrefix=prefix,
                        nextToken=next_token)
            else:
                streams = client.describe_log_streams(
                        logGroupName=group,
                        logStreamNamePrefix=prefix)
        except Exception as e:
            sys.stderr.write("Got CloudWatch exception {}\n".format(e))
            time.sleep(.1)
            continue

        for log_stream in streams['logStreams']:

            # Check for empty log file
            try:
                stream = log_stream['logStreamName']
                log_start_time = log_stream['firstEventTimestamp']
                log_end_time = log_stream['lastEventTimestamp']
            except KeyError:
                continue

            if startTime is not None and log_end_time < startTime:
                continue
            if endTime is not None and log_start_time > endTime:
                continue
            stream_count += 1
            exit_code = search_log(client, group, log_stream)
            if exit_code != 0:
                error_exit_count += 1

        if 'nextToken' in streams:
            next_token = streams['nextToken']
        else:
            done = True

    print("{} log streams found, {} with error(s)".format(
            stream_count, error_exit_count))


def main():
    """Scan AWS logs for errors in IPS processing.  We look for
    strings that we know are printed when errors occur.
    """

    args = parse_command_line()

    start_timestamp = None
    end_timestamp = None
    if args.start_time is not None:
        try:
            start = dateutil.parser.parse(args.start_time)
            ts = start.timetuple()
            start_timestamp = calendar.timegm(ts) * 1000
        except ValueError as e:
            sys.stderr.write("Error: start time invalid ({})\n".format(e))
            sys.exit(1)
    if args.end_time is not None:
        try:
            end = dateutil.parser.parse(args.end_time)
            ts = end.timetuple()
            end_timestamp = calendar.timegm(ts) * 1000
        except ValueError as e:
            sys.stderr.write("Error: end time invalid ({})\n".format(e))
            sys.exit(1)
    if start_timestamp is not None and end_timestamp is None:
        # End time was not specified.  Set it to now.
        end = datetime.datetime.utcnow()
        ts = end.timetuple()
        end_timestamp = calendar.timegm(ts) * 1000
    if start_timestamp is not None and end_timestamp is not None and \
            end_timestamp <= start_timestamp:
        sys.stderr.write("Error: end time earlier than start time\n")
        sys.exit(1)

    search_log_streams('/aws/batch/job', args.log_stream_prefix,
            startTime=start_timestamp, endTime=end_timestamp)

# Set this to false if you want to use --prefix
if __name__ == '__main__':
    main()
