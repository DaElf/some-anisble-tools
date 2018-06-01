#!/bin/sh -x

# Ultimately, we want to have outputdir be something different, but for now this will let us test the job perf locally, and then copy back as a job-end task. 

# Generate unique identifier based on epoch (good for 1 per second)
export UNIQID=`date +%s`

# TEMPORARY - Move into job directory
cd /efs/DEMO

# Set up and run the job
/efs/DEMO/setup_processing_conf.sh
/efs/DEMO/run_cli_py.sh

# Generate landing directory for the run
mkdir -p /efs/testruns/$UNIQID

# Copy over specific files, currently just the one sandbox run
cp -r /home/espa/output-data/ /efs/testruns/$UNIQID/
