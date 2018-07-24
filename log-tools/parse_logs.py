#! /usr/bin/env python

#
# Parse a set of AWS Cloud Watch log files, looking for strings
# that indicate errors.  I implemented two different searches.
# One goes through the events in the logs, looking at each event
# for an error string.  The other uses the AWS API to filter the
# logs for events.  The value of use_AWS_search, near the end of
# this  file, controls which algorithm is used.  On a test of
# 5500 log files, using the AWS search was slower (20m28s vs
# 16m5s).  A disadvantage of AWS filtering is that you can't use
# the prefix to narrow the scope of the search.

import sys
import boto3
import datetime
import dateutil.parser
import calendar
import argparse


def parse_command_line():
    """Parse the command line arguments
    """

    parser = argparse.ArgumentParser(
            description = "Search AWS logs for ESPA processing errors")
#   parser.add_argument('log_group',
#           type = str,
#           nargs = '?',
#           default = None,
#           help = 'AWS log group name')
    if not use_AWS_search:
        parser.add_argument('--prefix',
                type = str,
                dest = 'prefix',
                action = 'store',
                default = None,
                help = 'Job prefix for stream')
    parser.add_argument('--include-batch',
            dest = 'include_batch',
            action = 'store_true',
            default = False,
            help = 'Check output of script that runs batch job')
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

    args = parser.parse_args()

    return args


def classify_failure(message):
    """Look for a reason for a failure by looking for a string
    in the message.  Return a string with the reason, or None
    if we don't know what it was.
    """

    failure_types = [
            ("Non-zero exit code", "Exit now"),
            ("Not implemented", "has not been implemented"),
            ("SR zenith angle", "Solar zenith angle is out of range"),
            ("SR zenith angle", "solar zenith angle out of range"),
            ("SR unavailable", \
                    "include_sr is an unavailable product option"),
            ("Missing auxiliary data", \
                    "Could not find auxnm data file"),
            ("Missing TOMS data", \
                    "Could not find TOMS auxiliary data"),
            ("Surface temperature failed", \
                    "surface_temperature failed:"),
            ("Exception", "type 'exceptions.Exception'")
    ]

    for (reason, err_string) in failure_types:
        if message.find(err_string) != -1:
            return reason

    return None


def search_log(client, group, log_stream, err_string,
        startTime=None, endTime=None):
    """Search a log stream for an occurrence of the given error string.
    Print a message for each error we find.
    """

    done = False
    next_token = ''
    exit_code = 0
    stream = log_stream['logStreamName']
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
            if msg.find(err_string) != -1:
                # Special check if we're searching the job run lob
                if err_string == 'Exit now':
                    exit_code = int(event['message'].split(' ')[-1])
                    if exit_code != 0:
                        print("Invalid exit code {}:".format(exit_code))
                        print("    " + stream)
                    return exit_code
                else:
                    reason = classify_failure(msg)
                    if reason is not None:
                        print("Error detected ({}):".format(reason))
                    else:
                        print("Error detected:")
                    print("    " + stream)
                    return 1

        if 'nextToken' in events:
            next_token = events['nextToken']
        else:
            done = True

    return exit_code


def search_log_streams(group, prefix, err_string, startTime=None, endTime=None):
    """Search the streams in a log group for occurrences of
    the given error string.
    """

    done = False
    stream_count = 0
    error_exit_count = 0
    next_token = ''
    client = boto3.client('logs')
    while not done:
        if next_token != '':
            streams = client.describe_log_streams(
                    logGroupName=group,
                    logStreamNamePrefix=prefix,
                    nextToken=next_token)
        else:
            streams = client.describe_log_streams(
                    logGroupName=group,
                    logStreamNamePrefix=prefix)

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
            exit_code = search_log(client, group, log_stream, err_string)
            if exit_code != 0:
                error_exit_count += 1

        if 'nextToken' in streams:
            next_token = streams['nextToken']
        else:
            done = True

    print("{} log streams found, {} with error(s)".format(
            stream_count, error_exit_count))


def search_log_group(group, err_string, startTime=None, endTime=None):
    """Use AWS's filter to look for the given error string in
    the given log group.  Print a message for each error we find.
    In this case, we can't use a prefix to narrow the search.
    """

    done = False
    error_count = 0
    next_token = ''
    client = boto3.client('logs')
    while not done:
        if next_token != '':
            if startTime is not None:
                events = client.filter_log_events(
                        logGroupName=group,
                        filterPattern=err_string,
                        startTime=startTime,
                        endTime=endTime,
                        nextToken=next_token)
            else:
                events = client.filter_log_events(
                        logGroupName=group,
                        filterPattern=err_string,
                        nextToken=next_token)
        else:
            if startTime is not None:
                events = client.filter_log_events(
                        logGroupName=group,
                        filterPattern=err_string,
                        startTime=startTime,
                        endTime=endTime)
            else:
                events = client.filter_log_events(
                        logGroupName=group,
                        filterPattern=err_string)

        for event in events['events']:
            stream = event['logStreamName']
            msg = event['message']
            reason = classify_failure(msg)
            if reason is not None:
                print("Error detected ({}):".format(reason))
            else:
                print("Error detected:")
            print("    " + stream)
            error_count += 1

        if 'nextToken' in events:
            next_token = events['nextToken']
        else:
            done = True

    return error_count


def get_stream_names(group, prefix):
    """Get the log stream names in the given log group
    that start with the given prefix.
    """

    client = boto3.client('logs')
    done = False
    next_token = ''
    error_count = 0
    while not done:
        names = []
        if next_token != '':
            streams = client.describe_log_streams(
                    logGroupName=group,
                    logStreamNamePrefix=prefix,
                    nextToken=next_token)
        else:
            streams = client.describe_log_streams(
                    logGroupName=group,
                    logStreamNamePrefix=prefix)

        for stream in streams['logStreams']:
            if 'logStreamName' in stream:
                names.append(stream['logStreamName'])

        if 'nextToken' in streams:
            next_token = streams['nextToken']
        else:
            done = True

    return names


def main():
    """Scan AWS logs for errors in ESPA processing.  We look for
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

    if use_AWS_search:
        error_count = 0
        if args.include_batch:
            error_count = search_log_group('/aws/batch/job',
                    'Exit now -0',
                    startTime=start_timestamp, endTime=end_timestamp)

        error_count += search_log_group('espa-process',
                "Errors during processing",
                startTime=start_timestamp, endTime=end_timestamp)
#       error_count += search_log_group('espa-process',
#               "exceptions.Exception",
#               startTime=start_timestamp, endTime=end_timestamp)
        print("{} Errors found".format(error_count))
    else:
        if args.include_batch:
            search_log_streams('/aws/batch/job', 'espa-process-batch',
                    'Exit now',
                    startTime=start_timestamp, endTime=end_timestamp)
        job_stream = 'process-'
        if args.prefix is not None:
            job_stream = args.prefix
        search_log_streams('espa-process', job_stream,
                "Errors during processing",
                startTime=start_timestamp, endTime=end_timestamp)

# Set this to false if you want to use a --prefix
use_AWS_search = False
if __name__ == '__main__':
    main()
