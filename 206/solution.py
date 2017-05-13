#!/usr/bin/env python
import sys


class Options:
    debug = False
    euler = False
    every = 10000
    string = "1_2_3_4_5_6_7_8_9_0"
    wildcard = "_"
    power = 2


def test_number(digits_, string):
    ''' test_number:
    Takes the string and replaces each wildcard with the digit in the `digits`
    list, then tests whether the resulting number is an nth power of an integer
    (finds the nth root and tests if it is an integer).
    '''
    digits = list(digits_)
    number = ''
    for c in string:
        number += c if c != Options.wildcard else str(digits.pop())

    number = int(number)
    root = pow(number, (1.0/Options.power))
    if Options.debug:
        print("Power: {} Root: {}".format(number, root))

    return pow(int(root), 2) == number, int(root)


def pull_digits(string, base):
    ''' pull_digits:
    Takes a full number string and the template (with wildcards) and pulls out
    the digits being iterated over (the ones that are filling in the wildcard)
    and returns them as a list.
    '''
    digits = []
    for i in range(len(string)):
        print base[i], string[i]
        if base[i] == Options.wildcard:
            digits.append(int(string[i]))

    digits.reverse()
    return digits


def find_number(base_string):
    ''' find_number:
    Takes the `base_string` and loops through all permutations of the wildcard
    numbers (counting up) until it finds a value where the nth root is an
    integer.
    '''
    digits = [0 for i in range(base_string.count(Options.wildcard))]
    while True:
        is_power, root = test_number(digits, base_string)
        if is_power:
            return root

        #digits = pull_digits(str(pow(root + 1, Options.power)), base_string)
        #print digits

        for i in range(len(digits)):
            digits[i] += 1
            if digits[i] < 10:
                break

            digits[i] = 0

        if digits.count(0) == len(digits):
            return -1


if __name__ == "__main__":
    nxt = None
    if len(sys.argv) > 1:
        def wildcard(x): Options.wildcard = x
        def power(x): Options.power = int(x)
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                nxt = None

                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
                elif arg in ['-w', '--wildcard']:
                    nxt = wildcard
                elif arg in ['-p', '--power']:
                    nxt = power
            else:
                if nxt:
                    nxt(arg)
                    nxt = None
                else:
                    Options.string = arg

    number = find_number(Options.string)
    if number == -1:
        print("String {} is not an {}th power of an integer".format(
            Options.string, Options.power))

    if Options.euler:
        print("euler answer: {}".format(number))
