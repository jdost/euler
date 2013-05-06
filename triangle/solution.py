#!/usr/bin/env python2
import sys
SEPERATOR = ' '


class Options:
    debug = False
    euler = False
    filename = "67.txt"


class Node:
    ''' Node:
    A node in the triangle tree, has links to the child node to either the left
    or right on the next level
    '''
    def __init__(self, value):
        self.value = value
        self.weight = 0
        self.path = None
        self.left = None
        self.right = None

    def calc_weight(self):
        ''' (public) calc_weight:
        '''
        self.weight = self.value
        if self.left and self.right:
            if self.left.weight > self.right.weight:
                self.path = self.left
                self.weight += self.left.weight
            else:
                self.path = self.right
                self.weight += self.right.weight

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

    def get_values(self):
        ''' (public) get_values:
        Goes down the left most and right most legs based on the level/position
        provided and gives the total "potential" for each leg of the sub
        triangle this represents.
        '''
        for level in reversed(self.levels):
            for node in level:
                node.calc_weight()

    def find_path(self):
        ''' (public) find_path:
        Goes down the levels of the triangle, looking to find the path with
        the maximum value.
        '''
        self.get_values()
        node = self.levels[0][0]
        path = [node]
        while node.left:
            if node.left.weight > node.right.weight:
                node = node.left
            elif node.left.weight < node.right.weight:
                node = node.right
            else:
                node = node.left if node.left.value > node.right.value \
                        else node.right
            path.append(node)

        return path

    def find_euler(self, path):
        ''' (public) find_euler:
        Finds the sum of the numbers on that path, used for solving the problem
        on the euler page.
        '''
        path_sum = 0
        for node in path:
            path_sum += node.value

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
        print("Loaded {} levels".format(len(triangle.levels)))

    path = triangle.find_path()

    if Options.euler:
        print("euler answer: {}".format(triangle.find_euler(path)))


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
