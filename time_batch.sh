#! /bin/bash

# This script polls slurm every two seconds to get the status of a job and its most recent output.
# It writes this output to a file called job_[job ID]_stats.txt

# $1 is the job id

echo 'Usage: time_batch.sh job_id'
echo 'The job id is a big number.'

output="job_$1_stats.txt"

# $1 is the job id
# $2 is the time information from squeue
function get_status () {
	echo "----------------------------------------" >> $output
	echo "$2" >> $output
	echo "" >> $output
	rjobstat $1 >> $output
	echo "" >> $output
	echo "Recent output:" >> $output
	tail -1 slurm-$1.out >> $output
	echo "----------------------------------------" >> $output
	sleep 2
}

on_queue="$(squeue | grep $1)"

while [ "$on_queue" != '' ]
do
	get_status $1 "$on_queue"
	on_queue="$(squeue | grep $1)"
done
