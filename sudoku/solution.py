PREFIX = "Grid"


class CollisionError(BaseException):
    pass


class NoPossibilityError(BaseException):
    pass


class NumSet:
    ''' class NumSet:
    Wrapper class for a "number set" which is defined as either a 3x3 square,
    a row, or a column in the Sudoku board.  This means that the nodes that
    belong to it should each have one of each number between 1 and 9.
    '''
    def __init__(self):
        self.nodes = []
        self.answers = set()

    def exclusives(self):
        ''' (public) exclusives:
        Loops through the unanswered nodes for this NumSet, tracking the number
        of occurances of each possibility, if any possibility has only one
        occurance, the Node with that possibility must be the one with that
        answer.
        '''
        possibility_count = {}
        for i in range(1, 10):
            if i not in self.answers:
                possibility_count[i] = 0

        for node in self.nodes:
            if node.is_solved():
                continue
            for possibility in node.possibilities:
                possibility_count[possibility] += 1

        found = 0
        for (number, count) in possibility_count.items():
            if count == 1:
                for node in self.nodes:
                    if number in node.possibilities:
                        found += 1
                        node.set_answer(number)
                        break

        return found


class Node:
    ''' class Node:
    Represents a single number square on the board, has a single answer, it
    keeps references to the 3x3 square, row, and column NumSet it belongs to.
    It either has an `answer` which is defined as the proper solution for the
    Node or a set of `possibilities` that is a group of potential solutions for
    the square.
    '''
    def __init__(self, answer, row, column):
        self.answer = answer
        self.row_index = row
        self.column_index = column
        self.square_index = (column / 3 + 3 * (row / 3))
        self.numsets = []
        self.possibilities = set()

        if answer == 0:
            self.possibilities = set(range(1, 10))

    def attach_numset(self, numset):
        ''' (public) attach_numset:
        Attaches a NumSet
        '''
        self.numsets.append(numset)
        if self.is_solved:
            numset.answers.add(self.answer)

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
        '''
        if not verbose:
            return str(self.answer) if self.is_solved() else " "
        else:
            return {
                "answer": self.answer,
                "possibilities": self.possibilities
            }.__str__()


class Board:
    ''' class Board:
    Large wrapper class to encapsulate the basics of a board.  Using an object
    approach to gather the various operators on the board into a common
    namespace.
    '''
    def __init__(self):
        self.squares = []
        self.columns = []
        self.rows = []
        self.nodes = []
        self.numsets = []
        self.solved = 0

        for i in range(9):
            self.squares.append(self.__make_numset())
            self.columns.append(self.__make_numset())
            self.rows.append(self.__make_numset())

    def __make_numset(self):
        ''' (private) __make_numset:
        Simple function to generate a NumSet object, wrapped as a private
        method in case of possible future actions that may need to be done.
        '''
        numset = NumSet()
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
            elif num > '0':
                self.solved += 1
            self.build_node(int(num), row, column)
            column += 1

    def build_node(self, val, row, col):
        ''' (public) build_node:
        Takes a value of a node, a row index and a column index and creates a
        solution node at that location, with references to the respective
        numsets.
        '''
        node = Node(val, row, col)
        node.attach_numset(self.squares[node.square_index])
        node.attach_numset(self.rows[row])
        node.attach_numset(self.columns[col])
        self.nodes.append(node)

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
            if solved:
                self.solved += 1

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
        clone.solved = self.solved
        for node in self.nodes:
            node_ = clone.build_node(node.answer, node.row_index,
                                     node.column_index)
            node_.possibilities = node.possibilities.copy()

        return clone

    def __str__(self):
        ''' (magic) __str__:
        Prints a representation of the Board, useful for debugging purposes.
        '''
        output = ""
        index = 0
        for i in range(9):
            if i > 0 and i % 3 == 0:
                output += "------+-------+------\n"
            output += ""
            for j in range(9):
                if j > 0 and j % 3 == 0:
                    output += "| "
                output += str(self.nodes[index]) + " "
                index += 1

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
    while line:
        line = f.readline()
        if line.startswith(PREFIX):
            cnt = load_board(f)
            if cnt == 81:
                print "solved"
                solved_cnt += 1
            else:
                print "unsolved - " + str(cnt)

    print "solved " + str(solved_cnt) + " puzzles"


def load_board(fp):
    ''' takes the file pointer and loads in a board set
    '''
    board = Board()
    for i in range(9):
        line = fp.readline()
        board.load_row(line, i)

    return solve(board)


def solve(board):
    board.full_clip()
    found = 1
    while found:
        found = board.exclusives()

    while board.solved < 81:
        poss_total = 0
        for node in board.nodes:
            poss_total += len(node.possibilities)
        break
        board_ = board.clone()
        try:
            res, value = simulate_guess(board_)
        except:
            break

        if not res:
            print value
            board.nodes[value[0]].possibilities.remove(value[1])
        else:
            board = value

        poss_total_ = 0
        for node in board.nodes:
            poss_total_ += len(node.possibilities)

        if poss_total_ == 0:
            break

        print poss_total, poss_total_, board.solved

    print board
    return board.solved


def simulate_guess(board):
    ''' simulate_guess:
    Finds an unsolved node with the lowest number of possibilities, picks the
    first one and attempts to solve with that as an answer, if the result is
    unsolvable, returns False, otherwise returns a solved board
    '''
    guess_node = None
    node_index = 0
    i = 0
    possibility_count = 10
    for node in board.nodes:
        if not node.is_solved() \
                and len(node.possibilities) < possibility_count:
            guess_node = node
            node_index = i
            possibility_count = len(node.possibilities)
            if possibility_count == 0:
                raise NoPossibilityError
        i += 1

    if not guess_node:
        return True, board

    guess = guess_node.possibilities.pop()
    guess_node.set_answer(guess)

    try:
        board.full_clip()
        found = 1
        while found:
            found = board.exclusives()
    except:
        return False, (node_index, guess)

    return True, board

if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "sudoku.txt"
    load_file(filename)
