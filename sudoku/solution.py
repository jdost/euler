import copy
PREFIX = "Grid"


def load_file(filename):
    ''' loads the puzzles from the file
    '''
    f = open(filename, 'r')
    line = f.readline()
    while line:
        if line.startswith(PREFIX):
            load_board(f)
        line = f.readline()


def load_board(fp):
    ''' takes the file pointer and loads in a board set
    '''
    board = {
        "squares": [],
        "columns": [],
        "rows": [],
        "nodes": []
    }
    for i in range(9):
        board['rows'].append({
            'nodes': [],
            'answers': []
        })
        board['columns'].append({
            'nodes': [],
            'answers': []
        })
        board['squares'].append({
            'nodes': [],
            'answers': []
        })
    for i in range(9):
        line = fp.readline()
        j = 0
        for num in line:
            if num >= '0' and num <= '9':
                board['nodes'].append(build_node(int(num), i, j, board))
            j += 1

    solve_board(board)


def build_node(number, row, column, board):
    ''' ???
    '''
    node = {
        "answer": number,
        "row": board['rows'][row],
        "column": board['columns'][column],
        "square": board['squares'][(column / 3 + 3 * (row / 3))]
    }

    if number > 0:
        node['possibilities'] = []
        node['column']['answers'].append(number)
        node['row']['answers'].append(number)
        node['square']['answers'].append(number)
    else:
        node['possibilities'] = range(1, 10)

    node['column']['nodes'].append(node)
    node['row']['nodes'].append(node)
    node['square']['nodes'].append(node)

    return node


def solve_board(board):
    ''' loops through nodes trying to eliminate possiblities
    '''
    answered = -1
    board, answered = logic_board(board)
    while answered < 81:
        i = 0
        board_ = copy.copy(board)
        for node in board_['nodes']:
            if node['answer'] == 0:
                node['answer'] = node['possibilities'][0]
                try:
                    board, answered = logic_board(board_)
                except BaseException:
                    del board['nodes'][i]['possibilities'][0]
                break
            i += 1

    if answered == 81:
        print "solved"
    else:
        print "unsolved - " + str(answered)


def logic_board(board):
    clips = 1
    solved = 1
    while clips > 0 and solved > 0:
        board, clips, answered = clip_possibilities(board)
        while clips > 0:
            board, clips, answered = clip_possibilities(board)
        board, solved = find_exclusives(board)
        while solved > 0:
            board, solved = find_exclusives(board)

    return board, answered


def clip_possibilities(board):
    clips = 0
    answered = 0
    for node in board['nodes']:
        if node['answer'] > 0:
            answered += 1
            continue

        for answer in node['column']['answers']:
            if answer in node['possibilities']:
                clips += 1
                node['possibilities'].remove(answer)
        for answer in node['row']['answers']:
            if answer in node['possibilities']:
                clips += 1
                node['possibilities'].remove(answer)
        for answer in node['square']['answers']:
            if answer in node['possibilities']:
                clips += 1
                node['possibilities'].remove(answer)

        if len(node['possibilities']) == 1:
            node['answer'] = node['possibilities'][0]
            if node['answer'] in node['column']['answers']:
                raise
            if node['answer'] in node['row']['answers']:
                raise
            if node['answer'] in node['square']['answers']:
                raise
            node['column']['answers'].append(node['answer'])
            node['row']['answers'].append(node['answer'])
            node['square']['answers'].append(node['answer'])
            node['possibilities'] = []

    return board, clips, answered


def find_exclusives(board):
    solved = 0
    index = 0
    for row in board['rows']:
        board['rows'][index], s = find_exc(row)
        index += 1
    solved += s

    index = 0
    for column in board['columns']:
        board['columns'][index], s = find_exc(column)
        index += 1
    solved += s

    index = 0
    for square in board['squares']:
        board['squares'][index], s = find_exc(square)
        index += 1
    solved += s

    return board, solved


def find_exc(numset):
    poss_count = {}
    for i in range(1, 10):
        poss_count[i] = 0

    for node in numset['nodes']:
        if node['answer'] > 0:
            continue
        for poss in node['possibilities']:
            poss_count[poss] += 1

    solved = 0
    for (num, cnt) in poss_count.items():
        if cnt == 1:
            solved += 1
            for node in numset['nodes']:
                if node['answer'] > 0:
                    continue
                if num in node['possibilities']:
                    if node['answer'] in node['column']['answers']:
                        print "column", node['answer']
                        raise BaseException
                    if node['answer'] in node['row']['answers']:
                        print "row", node['answer']
                        raise BaseException
                    if node['answer'] in node['square']['answers']:
                        print "square", node['answer']
                        raise BaseException
                    node['answer'] = num
                    node['column']['answers'].append(node['answer'])
                    node['row']['answers'].append(node['answer'])
                    node['square']['answers'].append(node['answer'])
                    node['possibilities'] = []
                    break

    return numset, solved

load_file("sudoku.txt")
