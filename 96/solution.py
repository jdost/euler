#!/usr/bin/env python
# -*- coding: latin-1 -*-
import sys
PREFIX = "Grid"


class CollisionError(BaseException):
    pass


class NoPossibilityError(BaseException):
    pass


class Options:
    debug = False
    euler = False
    fancy = False
    filename = "sudoku.txt"


class NUMSET:
    ROW = 1
    COLUMN = 2
    SQUARE = 3


class NumSet:
    ''' class NumSet:
    Wrapper class for a "number set" which is defined as either a 3x3 square,
    a row, or a column in the Sudoku board.  This means that the nodes that
    belong to it should each have one of each number between 1 and 9.
    '''
    def __init__(self, set_type):
        self.nodes = []
        self.answers = set()
        self.set_type = set_type

    def exclusives(self):
        ''' (public) exclusives:
        Loops through the unanswered nodes for this NumSet, tracking the number
        of occurances of each possibility, if any possibility has only one
        occurance, the Node with that possibility must be the one with that
        answer.
        '''
        # Find nodes that have the only occurance of the number
        possibility_count = {}
        for i in range(1, 10):
            if i not in self.answers:
                possibility_count[i] = []

        for node in self.nodes:
            if node.is_solved():
                continue
            prune = []
            for possibility in node.possibilities:
                if possibility not in possibility_count.keys():
                    prune.append(possibility)
                    continue
                possibility_count[possibility].append(node)
            for number in prune:
                node.possibilities.remove(number)
        # Loop over possibility counts
        found = 0
        for (number, nodes) in possibility_count.items():
            if len(nodes) == 1:  # numbers with only 1 get solved
                node = nodes[0]
                if number in node.possibilities:
                    found += 1
                    node.set_answer(number)
                    break
            # Look for nodes in both a square and row/column that exclusively
            # share a possibility clean out of other NumSet
            elif self.set_type == NUMSET.SQUARE and \
                    (len(nodes) == 2 or len(nodes) == 3):
                # Row cleaning
                rows = set([node.row_index for node in nodes])
                if len(rows) == 1:
                    row = [numset for numset in nodes[0].numsets
                            if numset.set_type == NUMSET.ROW][0]
                    for node in row.nodes:
                        if node not in nodes:
                            node.possibilities.discard(number)
                # Column cleaning
                columns = set([node.column_index for node in nodes])
                if len(columns) == 1:
                    column = [numset for numset in nodes[0].numsets
                            if numset.set_type == NUMSET.COLUMN][0]
                    for node in column.nodes:
                        if node not in nodes:
                            node.possibilities.discard(number)
            # TODO: this **really** could be cleaned up

        # Find nodes that share identical possibility sets, if the length of
        # the shared set equals the length of the nodes, those possibilities
        # are exclusive to the set of nodes
        shares = []
        for i in range(9):
            base_node = self.nodes[i]
            match_set = []
            for j in range(i + 1, 9):
                if base_node.possibilities == self.nodes[j].possibilities:
                    match_set.append(self.nodes[j])

            if len(match_set):
                match_set.append(base_node)
                shares.append(match_set)

        for share_set in shares:
            if len(share_set) != len(share_set[0].possibilities):
                continue

            for node in self.nodes:
                if node not in share_set and not node.is_solved():
                    node.possibilities -= share_set[0].possibilities

        return found


class Node:
    ''' class Node:
    Represents a single number square on the board, has a single answer, it
    keeps references to the 3x3 square, row, and column NumSet it belongs to.
    It either has an `answer` which is defined as the proper solution for the
    Node or a set of `possibilities` that is a group of potential solutions for
    the square.
    '''
    def __init__(self, answer, row, column, board):
        self.answer = answer
        self.row_index = row
        self.column_index = column
        self.square_index = (column / 3 + 3 * (row / 3))
        self.numsets = []
        self.possibilities = set()
        self.possibilities = set(range(1, 10))
        self.board = board

    def attach_numset(self, numset):
        ''' (public) attach_numset:
        Attaches a NumSet
        '''
        self.numsets.append(numset)
        numset.nodes.append(self)

    def is_solved(self):
        ''' (public) is_solved
        Returns True/False whether this is a solved node
        '''
        return self.answer != 0

    def set_answer(self, answer):
        ''' (public) set_answer:
        Sets the answer to the Node, should clear the possibilities and should
        add its answer to the answer set in each of it's NumSets
        '''
        self.answer = answer
        self.possibilities = set()
        self.board.solved += 1
        for numset in self.numsets:
            if self.answer in numset.answers:
                raise CollisionError(self.answer)
            numset.answers.add(self.answer)

    def clip(self):
        ''' (public) clip:
        Goes through the already answered values for each of this Node's
        NumSets and eliminates those from its possibilities pool.  If the set
        is only 1 item, this should be the answer for the square.  This then
        gets set as the answer.

        Returns whether this clip call solved the Node and the number of
        possibilities clipped
        '''
        orig_len = len(self.possibilities)
        for numset in self.numsets:
            self.possibilities = self.possibilities - numset.answers

        if len(self.possibilities) == 1:
            self.set_answer(self.possibilities.pop())
        elif len(self.possibilities) == 0:
            raise NoPossibilityError

        return self.is_solved(), orig_len - len(self.possibilities)

    def __str__(self, verbose=False):
        ''' (magic) __str__:
        Print output of the node, if the method is called with a verbose
        option, will output a debugging string, otherwise just prints an empty
        node or the answer
        '''
        if not verbose:
            return str(self.answer) if self.is_solved() else " "
        else:
            return "Answer: {answer} ({possibilities})".format(**self)


class Board:
    ''' class Board:
    Large wrapper class to encapsulate the basics of a board.  Using an object
    approach to gather the various operators on the board into a common
    namespace.
    '''
    normal_lines = [
        " {} {} {} | {} {} {} | {} {} {} \n",
        " ------+-------+------ \n",
        ""
            ]
    fancy_lines = [
        " {}│{}│{}┃{}│{}│{}┃{}│{}│{} \n",
        " ━┿━┿━╋━┿━┿━╋━┿━┿━ \n",
        " ─┼─┼─╂─┼─┼─╂─┼─┼─ \n"
            ]
    def __init__(self):
        self.squares = []
        self.columns = []
        self.rows = []
        self.nodes = []
        self.numsets = []
        self.solved = 0

        for i in range(9):
            self.squares.append(self.__make_numset(NUMSET.SQUARE))
            self.columns.append(self.__make_numset(NUMSET.COLUMN))
            self.rows.append(self.__make_numset(NUMSET.ROW))

    def __make_numset(self, set_type):
        ''' (private) __make_numset:
        Simple function to generate a NumSet object, wrapped as a private
        method in case of possible future actions that may need to be done.
        '''
        numset = NumSet(set_type)
        self.numsets.append(numset)
        return numset

    def load_row(self, row_text, row):
        ''' (public) load_row:
        Takes a string of text that represents a row of the board, creating
        the nodes and referencing the nodes to their respective numsets (row,
        column, and square).
        '''
        column = 0
        for num in row_text:
            if num < '0' or num > '9':
                continue
            self.build_node(int(num), row, column)
            column += 1

    def build_node(self, val, row, col):
        ''' (public) build_node:
        Takes a value of a node, a row index and a column index and creates a
        solution node at that location, with references to the respective
        numsets.
        '''
        node = Node(val, row, col, self)
        node.attach_numset(self.squares[node.square_index])
        node.attach_numset(self.rows[row])
        node.attach_numset(self.columns[col])
        self.nodes.append(node)
        if node.answer:
            node.set_answer(node.answer)

        return node

    def clip(self):
        ''' (public) clip:
        Method that loops over each node and trims or clips down the
        possibility list for each node (the possibility list is a list of all
        of the potential values the node can have).  Returns the number of
        nodes that had possibilities that could be clipped.
        '''
        solved_orig = self.solved
        for node in self.nodes:
            if node.is_solved():
                continue
            solved, changed = node.clip()

        return self.solved - solved_orig

    def full_clip(self):
        ''' (public) full_clip:
        Runs the `clip` optimization method until the node possiblities sets
        can no longer be optimized/clipped.  This means finding every Node
        that, by process of elimination, only has one possibility and answering
        it, then looping through again to update other, related, nodes against
        this new elimination.
        '''
        clip = 1
        while clip:
            clip = self.clip()

    def exclusives(self):
        ''' (public) exclusives:
        Runs the `exclusives` optimization method, then `clip`s the Nodes if
        any optimizations were found.  The optimization runs on the idea that
        if a Node has a possibility that is unique to the unanswered Nodes in
        a NumSet, it, by process of elimination, must be the answer (otherwise
        the NumSet would not ever have that as an answer).  A `full_clip` is
        run after if an exclusive was found to optimize the possibilities for
        all of the other squares.
        '''
        exc = 0
        for numset in self.numsets:
            exc += numset.exclusives()
        if exc:
            self.full_clip()

        return exc

    def clone(self):
        ''' (public) clone:
        Performs an optimized deep copy of the Board.  It needs to be optimized
        because the Nodes hold circular references with their NumSets.
        '''
        clone = Board()
        for node in self.nodes:
            node_ = clone.build_node(node.answer, node.row_index,
                                     node.column_index)
            node_.possibilities = node.possibilities.copy()

        return clone

    def get_euler(self):
        ''' (public) get_euler:
        Returns the value used in the euler problem, this is the 3 digit number
        made up of the first 3 nodes, so node[0] is the hundreds, node[1] is
        the tens, and node[2] is the ones
        '''
        return self.nodes[0].answer * 100 + \
                self.nodes[1].answer * 10 + self.nodes[2].answer

    def __str__(self):
        ''' (magic) __str__:
        Prints a representation of the Board, useful for debugging purposes.
        '''
        lines = self.fancy_lines if Options.fancy else self.normal_lines
        output = ""
        for i in range(9):
            output += lines[0].format(*self.nodes[(i * 9):(i * 9 + 9)])
            if i < 8 and i % 3 == 2:
                output += lines[1]
            elif i < 8:
                output += lines[2]

        output += "\n"

        return output


def load_file(filename):
    ''' load_file:
    The given filename is read in against the standard used in the puzzle file.
    Looping over each board in the file, the board is loaded and then attempted
    to be solved.

    file format example:
        Grid X
        01000200003
        90000070000
        etc...
    '''
    f = open(filename, 'r')
    line = "~~"
    solved_cnt = 0
    euler = 0
    while line:
        line = f.readline()
        if line.startswith(PREFIX):
            board = load_board(f)
            board = solve(board)
            if board.solved == 81:
                solved_cnt += 1
                euler += board.get_euler()

            if Options.debug:
                print line
                print board
            else:
                sys.stdout.write('%s' % '.' if board.solved == 81 else 'E')
                sys.stdout.flush()

    if not Options.debug:
        sys.stdout.write('\n')
        sys.stdout.flush()

    print "solved " + str(solved_cnt) + " puzzles"
    if Options.euler:
        print "euler answer: " + str(euler)


def load_board(fp):
    ''' load_board:
    Loads the board from the file, this assumes there are 9 lines of 9 numbers
    each, each number represents a place on the board.  Returns the built
    Board object.
    '''
    board = Board()
    for i in range(9):
        line = fp.readline()
        board.load_row(line, i)

    return board


def solve(board):
    ''' solve:
    Goes through the various steps used in attempting to solve the board.  The
    steps taken (in order) are:
    - Go through each node and trim (or clip) the possibility list based on
      the other nodes in the row/column/square that are already answered,
      will go through this until all of the possibility sets are fully
      clipped
    - Goes through each row/column/square and finds trends to eliminate
      possibilities for other nodes, this includes nodes that hold the only
      occurence of the number in that set, nodes that hold an exclusive
      overlap between two sets (i.e. only 2 2's in a square AND row), and two
      (or more) squares that share the same possibility set, making it
      exclusive for them (i.e. 2 nodes with (1, 2) means they HAVE to have
      either)
    - If still not solved, will begin simulating boards based on a guess using
      the `simulate_guess` function
    '''
    board.full_clip()
    found = 1
    while found:
        found = board.exclusives()

    while board.solved < 81:
        board = simulate_guess(board)

    return board


def simulate_guess(board):
    ''' simulate_guess:
    Clones the passed in board.  Locates the node with the smallest possibility
    pool, takes the first of those and sets the answer to be that.  Then
    attempts to solve the board with this answer, if it fails, removes that
    answer from the node's possibility set and returns the board.
    '''
    board_ = board.clone()

    guess_node = None
    node_index = 0
    i = 0
    possibility_count = 10
    for node in board_.nodes:
        if not node.is_solved() \
                and len(node.possibilities) < possibility_count:
            # This node is a better choice than previious
            guess_node = node
            node_index = i
            possibility_count = len(node.possibilities)
            if possibility_count == 0:
                raise NoPossibilityError
        i += 1

    if not guess_node:
        return None

    # Grab the guess being made and set it on the node being used
    guess = guess_node.possibilities.pop()
    guess_node.set_answer(guess)

    try:  # Attempt to solve the board with this guess
        board_.full_clip()
        found = 1
        while found:
            found = board_.exclusives()
    except:  # if the board is in an unsolvable state, remove the guess from
        # the target node in the original board, return it
        board.nodes[node_index].possibilities.remove(guess)
        return board

    if board_.solved < 81:  # If the board didn't get unsolvable and didn't
            # get solved, simulate again
        return simulate_guess(board_)

    return board_

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
                elif arg in ['-f', '--fancy']:
                    Options.fancy = True
            else:
                Options.filename = arg
    load_file(Options.filename)
