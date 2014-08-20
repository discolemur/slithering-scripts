#! /bin/env python

## This function performs an action on a list of things and prints the progress as it goes.
# Arguments:
# list === a bunch of items
# action === a function to perform on the items (the first argument in the function must be an item in the list)
# *args === optional arguments to pass into the action function
def do_progress_update(list, action, *args) :
	total = len(list)
	if total == 0 :
		print('Progress cannot be shown for a list with no entries.')
		return False
	checkpoint = int(total / 10)
	if checkpoint == 0 :
		checkpoint = 1
	counter = 0
	for item in list :
		if (counter % checkpoint == 0) :
			print('Progress: %d/%d (%.2f%%)' %(counter, total, (counter * 100.0 / total)))
		action(item, *args)
		counter += 1
	return True
