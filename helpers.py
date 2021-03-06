#! /usr/bin/env python

# This script contains functions that are intended to help you do cool things in simple ways.
# Just include this file in the python path, and you're good to go.
# Import the functions and use them as your heart desires.


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


## This function performs a simple action on a list using multithreading
def parallelize(values, action, num_threads) :
    '''
    Values are a list of items to act upon.
    Action is the function that takes a batch of values.
    num_threads is obvious.
    Action will accept two arguments: a subset of values, and the value of the first index in the full array.
    Sometimes I want to know the counter ID for each value. That's why I give that index as an argument.
    '''
    import threading
    if num_threads > len(values) :
        num_threads = len(values)
    threads = []
    div = int(len(values) / num_threads)
    diff = len(values) % num_threads
    begin = 0
    end = div
    if diff > 0 :
        end += 1
        diff -= 1
    for i in range(num_threads) :
        counter = begin
        thread = threading.Thread(target=action, args=(values[begin:end], counter))
        threads.append(thread)
        thread.start()
        begin = end
        end += div
        if diff > 0 :
            end += 1
            diff -= 1
    for thread in threads :
        thread.join()
