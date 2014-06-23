#! /bin/bash

# $1 is the job id

output="job_$1_stats"

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
