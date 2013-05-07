#!/usr/bin/env python
import sys
SEPARATOR = ','


class Options:
    debug = False
    euler = False
    filename = 'cipher1.txt'
    length = 3
    target = ' '


class Cipher:
    ''' Cipher:
    Wrapper object for a cipher text.  Keeps an array of each character that
    correlates to a character in an XOR passphrase.  After the cipher text is
    loaded, will find the most common characters for each and (assume) they are
    spaces.
    '''
    def __init__(self, phrase_length):
        self.length = phrase_length
        self.chars = []
        self.base = []
        self.pos = 0

        for i in range(self.length):
            self.chars.append({})

    def __add(self, num):
        ''' (private) __add
        Adds the character to the current position in the cipher passphrase,
        cycling the position and incrementing the count for each character.
        '''
        self.base.append(num)
        if num in self.chars[self.pos]:
            self.chars[self.pos][num] += 1
        else:
            self.chars[self.pos][num] = 1

        self.pos += 1
        if self.pos >= self.length:
            self.pos = 0

    def load_line(self, line):
        ''' (public) load_line:
        Loads a line of characters from a file, will break apart the line and
        increment the value count for the corresponding passphrase character.
        '''
        nums = line.split(SEPARATOR)
        for num in nums:
            self.__add(int(num))

    def __words(self, phrase, cnt=5):
        ''' (private) __words:
        Finds the first `cnt` "words" (space separated strings) using the
        provided phrase as the decoder.  Returns as a single string.
        '''
        word = []
        pos = 0
        space_cnt = 0
        for i in range(len(self.base)):
            char = self.base[pos] ^ phrase[pos % self.length]
            if char == ord(' '):
                space_cnt += 1
                if space_cnt > cnt:
                    break

            word.append(char)
            pos += 1

        return ''.join(map(unichr, word))

    def test(self):
        ''' (public) test:
        Begins a user interaction based test for a passphrase, will cycle
        through combinations of the most common character for each phrase
        charcter and tests against the target character.  Outputs the first
        set of words and ask for the user to confirm (or deny) that they are
        correct.  If so, returns the created phrase.
        '''
        index = [0 for i in range(self.length)]
        base = 0
        bin_cnt = 0
        word_cnt = 10 if Options.debug else 3
        while True:
            phrase = []
            i = 0
            for char in self.chars:
                char_set = sorted(char, key=char.get, reverse=True)
                phrase.append(char_set[index[i]] ^ ord(Options.target))
                i += 1

            words = self.__words(phrase, word_cnt)

            print("First {} words: {}".format(word_cnt, words))
            inp = raw_input("Use? [Yn] ")

            if len(inp) == 0 or inp.lower() == 'y':
                return phrase
            else:
                if index.count(base) == 0:
                    base += 1
                    bin_cnt = 1
                else:
                    bin_cnt += 1

                c = bin_cnt
                for i in range(len(index)):
                    index[i] = base + (c % 2)
                    c = c / 2

    def get_euler(self, phrase):
        ''' (public) get_euler:
        Calculates the sum of the unciphered character for the provided phrase
        and returns it.
        '''
        char_sum = 0
        for i in range(len(self.base)):
            char_sum += self.base[i] ^ phrase[i % len(phrase)]

        return char_sum


def load_file(filename):
    ''' load_file:
    Loads the provided file and runs it through the cipher system.
    '''
    f = open(filename, 'r')
    cipher = Cipher(Options.length)

    for line in f:
        cipher.load_line(line)

    phrase = cipher.test()
    if Options.euler:
        print("euler answer: {}".format(cipher.get_euler(phrase)))


if __name__ == "__main__":
    nxt = None
    if len(sys.argv) > 1:
        def plength(x): Options.length = int(x)
        def ctarget(x): Options.target = x
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                nxt = None
                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
                elif arg in ['-l', '--length']:
                    nxt = plength
                elif arg in ['-t', '--target']:
                    nxt = ctarget
            else:
                if nxt:
                    nxt(arg)
                    nxt = None
                else:
                    Options.filename = arg

    load_file(Options.filename)
