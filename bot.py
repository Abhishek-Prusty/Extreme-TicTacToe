import random
import math
import time
 
class Player1:
 
    def __init__(self):
        self.TL = 14
        self.SCALAR = 1/math.sqrt(2.0)
 
    class Node:
        def __init__(self, move, fin, flag, combopos, parent=None):
            self.move = move
            self.visits = 1
            self.reward = 0
            self.children = []
            self.parent = parent   
            self.flag = flag
            self.combopos = combopos
            self.final = fin
        def __str__(self):
            return str(self.reward) + " from " + str(self.visits) + "\n"
 
    def move(self, board, old_move, flag):
 
        self.nmove = (-1,-1)
        self.depth = 1
        self.start_time = time.time()
        self.maxdepth = 0
 
        self.symb = flag
        if self.symb == 'x':
            self.unsymb = 'o'
        else:
            self.unsymb = 'x'
 
        root = None
        if board.board_status[old_move[0]][old_move[1]] == self.symb:
            root = self.Node(old_move, False, self.symb, False)
        else:
            root = self.Node(old_move, False, self.symb, True)
        return(self.MC_init(root, board).move)
 
 
    def MC_init(self, root, board):
        while time.time() - self.start_time < self.TL:
            front = self.MC_treepolicy(root, board)
            self.MC_backup(front, board)
        sm = 0
        for i in xrange(len(root.children)):
            sm += root.children[i].visits
        print sm
        return self.MC_bestchild(root, 0)
 
    def MC_treepolicy(self, node, board):
        #a hack to force 'exploitation' in a game where there are many options, and you may never/not want to fully expand first
        while node.final == False:
            prevnode = node
            if len(node.children) == 0:
                self.MC_expand(node, board)
            if random.uniform(0,1) < .5:
                node = self.MC_bestchild(node, self.SCALAR)
            else:
                node = self.MC_randchild(node)
            board.update(prevnode.move, node.move, prevnode.flag)
            # print node
        return node
 
    def MC_expand(self, node, board):
        # flag, combopos
        cells = board.find_valid_move_cells(node.move)
        for nmv in cells:
            temp, bw = board.update(node.move, nmv, node.flag)
            if len(board.find_valid_move_cells(nmv)) == 0:
                if bw == True and node.combopos == True:
                    node.children.append(self.Node(nmv, True, node.flag, False, node))
                else:
                    if node.flag == self.symb:
                        node.children.append(self.Node(nmv, True, self.unsymb, True, node))
                    else:
                        node.children.append(self.Node(nmv, True, self.symb, True, node))
            else:
                if bw == True and node.combopos == True:
                    node.children.append(self.Node(nmv, False, node.flag, False, node))
                else:
                    if node.flag == self.symb:
                        node.children.append(self.Node(nmv, False, self.unsymb, True, node))
                    else:
                        node.children.append(self.Node(nmv, False, self.symb, True, node))
 
            board.board_status[nmv[0]][nmv[1]] = '-'
            board.block_status[nmv[0] // 4][nmv[1] // 4] = '-'
 
    def MC_bestchild(self, node, scalar):
        bestscore = 0.0
        bestchildren = []
        for c in node.children:
            exploit = c.reward/c.visits
            explore = math.sqrt(2.0*math.log(node.visits)/float(c.visits)) 
            score = exploit + scalar*explore
            if score == bestscore:
                bestchildren.append(c)
            if score > bestscore:
                bestchildren=[c]
                bestscore=score
        return random.choice(bestchildren)
 
    def MC_randchild(self, node):
        return random.choice(node.children)
 
    def MC_backup(self, node, board):
        reward = self.whoWon(board)
        if reward == self.symb:
            reward = 2
        elif reward == self.unsymb:
            reward = 0
        else:
            reward = 1
        # board.print_board()
        # print reward
        while node.parent != None:
            node.visits += 1
            node.reward += reward
            board.board_status[node.move[0]][node.move[1]] = '-'
            board.block_status[node.move[0] // 4][node.move[1] // 4] = '-'
            node = node.parent
        node.visits += 1
        node.reward += reward
 
    def whoWon(self, board):
        for x in xrange(0, 4):
            if(
                board.block_status[x][0] == board.block_status[x][1]
                and board.block_status[x][2] == board.block_status[x][3]
                and board.block_status[x][1] == board.block_status[x][2]
                and board.block_status[x][0] != 'd' and board.block_status[x][1] != '-'
            ):
                return board.block_status[x][0]
 
        for x in xrange(0, 4):
            if(
                board.block_status[0][x] == board.block_status[1][x] and
                board.block_status[2][x] == board.block_status[3][x] and
                board.block_status[1][x] == board.block_status[2][x] and
                board.block_status[1][x] != 'd' and board.block_status[1][1] != '-'
            ):
                return board.block_status[0][x]
 
        possibilities = [
                [[2,0], [1,1], [2,2], [3,1]],
                [[2,1], [1,2], [3,2], [2,3]],
                [[0,2], [1,1], [2,2], [1,3]],
                [[0,1], [1,0], [2,1], [1,2]]
                ]
        for x in xrange(0,4):
            ch = board.block_status[possibilities[x][0][0]][possibilities[x][0][1]]
            bl = True
            for y in xrange(1,4):
                a, b = possibilities[x][y][0], possibilities[x][y][1]
                bl &= (ch == board.block_status[a][b])
            if bl == True and ch!='-' and ch!='d':
                return ch
        return 'd'
