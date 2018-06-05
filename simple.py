#!/usr/bin/env python

import os
import json
from pprint import pprint
import processor
import config_utils as config
import socket
import sys
from logging_tools import EspaLogging
import settings
#from argparse import ArgumentParser


def cli_log_filename():
    """Specifies the log filename to use for the cli

    Args:
        args <args>: Command line arguments
    """

    return 'cli-{}-{}.log'.format("Bobs","Burgers")

def export_environment_variables(cfg):
    """Export the configuration to environment variables

    Supporting applications require them to be in the environmant

    Args:
        cfg <ConfigParser>: Configuration
    """

    for key, value in cfg.items('processing'):
        os.environ[key.upper()] = value




PROC_CFG_FILENAME = 'processing.conf'

def main():
    """Configures an order from the command line input and calls the
       processing code using the order
    """

    proc_cfg = config.retrieve_cfg(PROC_CFG_FILENAME)

    # Configure the base logger for this request
    EspaLogging.configure_base_logger(filename=cli_log_filename())
    # Configure the processing logger for this request
    EspaLogging.configure(settings.PROCESSING_LOGGER, debug=True,
                              order="Toast",
                              product="LC08_L1TP_047027_20131014_20170308_01_T1")


    with open('data.json') as f:
        order = json.load(f)
    pprint(order)

    print('*** Begin ESPA Processing on host [{}] ***' .format(socket.gethostname()))

    # Set to error condition
    proc_status = False

    export_environment_variables(proc_cfg)
    
    try:

        # Change to the processing directory
        current_directory = os.getcwd()
        os.chdir(proc_cfg.get('processing', 'espa_work_dir'))
        print ("Me")
        try:
            # All processors are implemented in the processor module
            print ("MeMe")
            pp = processor.get_instance(proc_cfg, order)
            print ("MeMeMe", pp)
            (destination_product_file, destination_cksum_file) = pp.process()

            # Set to success condition
            proc_status = True

        finally:
            # Change back to the previous directory
            os.chdir(current_directory)

    except Exception:
        print('*** Errors during processing ***')
        sys.exit(1)

    finally:
        print('*** ESPA Processing Completed ***')


if __name__ == '__main__':
    main()
