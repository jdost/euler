#!/usr/bin/env python
import sys
SEPERATOR = ' '


class Options:
    debug = False
    euler = False
    filename = "triangle.txt"


class Node:
    ''' Node:
    A node in the triangle tree, has links to the child node to either the left
    or right on the next level
    '''
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

    def __str__(self):
        ''' (magic) __str__:
        String representation of the Node
        '''
        return str(self.value)


class Triangle:
    ''' Triangle:
    The triangle tree to be solved.  Is a list of each level (being a list
    of the Nodes in that level).  Handles creating each Node and linking with
    the nodes on the prior level.
    '''
    def __init__(self):
        self.levels = []

    def add_level(self, values):
        ''' (public) add_level:
        Takes a list of strings representing the value for each node in the
        level and creates the nodes for that level, linking with the parent
        level.
        '''
        parent = self.levels[-1] if len(self.levels) else None
        index = 0
        level = []
        for value in values:
            node = Node(int(value))
            if parent:
                if index > 0:
                    parent[index - 1].right = node
                if index < len(parent):
                    parent[index].left = node

            level.append(node)
            index += 1

        self.levels.append(level)

    def get_values(self, level, position):
        ''' (public) get_values:
        Goes down the left most and right most legs based on the level/position
        provided and gives the total "potential" for each leg of the sub
        triangle this represents.
        '''
        pos = position
        left = 0
        right = 0
        for level in self.levels[(level + 1):]:
            pos += 1
            left += level[position].value
            right += level[pos].value

        return left, right

    def find_path(self):
        ''' (public) find_path:
        Goes down the levels of the triangle, looking to find the path with
        the maximum value.
        '''
        path = []
        position = 0
        for i in range(len(self.levels)):
            path.append(position)
            left, right = self.get_values(i, position)
            position += 1 if right > left else 0
            if Options.debug:
                print "{}{}{}".format(left, " \\" if right > left else "/ ",
                        right)

        return path

    def find_euler(self, path):
        ''' (public) find_euler:
        Finds the sum of the numbers on that path, used for solving the problem
        on the euler page.
        '''
        path_sum = 0
        for i in range(len(path)):
            path_sum += self.levels[i][path[i]].value

        return path_sum

    def __str__(self):
        ''' (magic) __str__:
        Returns a string representation of the triangle.
        '''
        last = self.levels[-1]
        node_size = len(str(max(last)))
        line_length = (2 * len(last) - 1) * node_size
        space = ' ' * node_size
        output = ""
        for level in self.levels:
            temp = [str(node) for node in level]
            level_str = space.join(temp)
            while len(level_str) < line_length:
                level_str = ' ' + level_str + ' '
            output += level_str + '\n'

        return output


def load_triangle(filename):
    ''' load_triangle:
    '''
    f = open(filename, 'r')
    triangle = Triangle()
    for line in f:
        triangle.add_level(line.split(SEPERATOR))
    if Options.debug:
        print str(triangle)
        print "Loaded {} levels".format(len(triangle.levels))

    path = triangle.find_path()

    if Options.euler:
        print "euler answer: {}".format(triangle.find_euler(path))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                if arg in ['-d', '--debug']:
                    Options.debug = True
                elif arg in ['-e', '--euler']:
                    Options.euler = True
            else:
                Options.filename = arg
    load_triangle(Options.filename)
