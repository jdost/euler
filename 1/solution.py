#!/usr/bin/env python
import sys
numset = set()


class Options:
    debug = False
    euler = False
    limit = 1000
    multiples = [3, 5]


def find_multiples(num, collection):
    ''' find_multiples:
    Adds every multiple of `num` that is less than `MAX` to a `set()`.  Does
    this by counting by the `num` value until it is greater than `MAX`
    '''
    i = num
    cnt = 1
    while i < Options.limit:
        collection.add(i)
        i += num
        cnt += 1

    return cnt


def str_to_ints(int_string):
    ''' str_to_ints:
    Converts a string into a list of ints, string can be a comma separated list
    of ints or a single int, will return a list
    '''
    int_string = int_string.split(",")
    ints = []
    for num in int_string:
        ints.append(int(num))

    return ints


def calc():
    ''' calc:
    Performs the calculation based on the Options object, will output the
    result to stdout
    '''
    for multiple in Options.multiples:
        count = find_multiples(multiple, numset)
        if Options.debug:
            print("{} multiples for {}".format(count, multiple))

    print("Found {} unique multiples".format(len(numset)))
    total = 0
    for num in numset:
        total += num

    if Options.euler:
        print("euler answer: {}".format(total))

if __name__ == "__main__":
    nxt = None
    n_limits = False
    if len(sys.argv) > 1:
        def multiple(x): Options.multiples += str_to_ints(x)
        def limit(x): Options.limit = int(x)
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
                elif arg in ['-l', '--limit']:
                    nxt = limit
                elif arg in ['-m', '--multiple']:
                    if not n_limits:
                        Options.multiples = []
                        n_limits = True
                    nxt = multiple
                else:
                    nxt = None
            elif nxt:
                nxt(arg)
                nxt = None

    calc()
