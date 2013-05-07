#!/usr/bin/env python
import sys


class Options:
    euler = False
    debug = False
    multiples = [2, 3, 4, 5, 6]


def is_permutation(src, dst):
    ''' is_permutation:
    Tests that the two values passed in are permutations of the same string.

    TODO: make this less sucky and confusing
    '''
    src = str(src)
    dst = str(dst)
    if len(src) != len(dst):
        return False

    for c in src:
        if src.count(c) != dst.count(c):
            return False

    return True


def find_permutations():
    ''' find_permutations:
    Loops through numbers, counting up until finding a number that is a
    permutation of itself as a multiple of all the numbers required.
    '''
    target = 1
    while True:
        cnt = 0
        for multiple in Options.multiples:
            m = target * multiple
            if not is_permutation(m, target):
                break
            if Options.debug:
                print("Permutation found for {}: {} & {}".format(
                    multiple, target, m))
            cnt += 1
        if cnt == len(Options.multiples):
            return target

        target += 1


def str_to_int(int_string):
    ''' str_to_int:
    Converts a string into a list of ints, string can be a comma separated list
    of ints or a single int, will return a list
    '''
    int_string = int_string.split(",")
    ints = []
    for num in int_string:
        ints.append(int(num))

    return ints

if __name__ == '__main__':
    nxt = None
    multiples_set = False
    if len(sys.argv) > 1:
        def multiple(x): Options.multiples += str_to_int(x)
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                nxt = None
                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
                elif arg in ['-m', '--multiple']:
                    if not multiples_set:
                        Options.multiples = []
                        multiples_set = True

                    nxt = multiple
            else:
                nxt(arg)
                nxt = None

    total = find_permutations()
    if Options.euler:
        print("euler answer: {}".format(total))
