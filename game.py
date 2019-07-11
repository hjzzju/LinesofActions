
from __future__ import print_function
import numpy as np



class Board(object):
    """board for the game"""

    def __init__(self, **kwargs):
        self.width = int(kwargs.get('width', 8))
        self.height = int(kwargs.get('height', 8))
        # board states stored as a dict,
        # key: move as location on the board,
        # value: player as pieces type
        self.states = {}
        self.map = [[0,0,0,0,0,0,0,0] for _ in range(8)]
        # need how many pieces in a row to win
        # self.white = 12 #黑白双方各有12个
        # self.black = 12
        self.players = [1, 2]  # player1 and player2 1为黑棋，2为白棋

    def init_board(self, start_player=0):
        #change
        # if self.width < self.n_in_row or self.height < self.n_in_row:
        #     raise Exception('board width and height can not be '
        #                     'less than {}'.format(self.n_in_row))
        #
        self.current_player = self.players[start_player]  # start player
        self.black = 12
        self.white = 12
        #初始化棋盘棋子为空
        self.map = [[0,0,0,0,0,0,0,0] for _ in range(8)]
        #初始化黑白棋子位置
        for i in range(1,7):
            self.map[0][i] = -1  #黑棋为-1
            self.map[7][i] = -1
            self.map[i][0] = 1   #白棋为1
            self.map[i][7] = 1

        # keep available moves in a list
        #change
        #self.availables = list(range(self.width * self.height))
        self.legal_moves = []
        self.row = ['0','1','2','3','4','5','6','7'] #row of the board
        self.col = ['0','1','2','3','4','5','6','7'] #col of the board
        for i in range(8):
            for j in range(8):
                des = [(i+t,j) for t in range(-8,9)] + [(i,j+t) for t in range(-8,9)] + [(i+t,j+t) for t in range(-8,9)]+[(i-t,j+t) for t in range(-8,9)]
                for (nex_i,nex_j) in des:
                    if nex_i in range(0,8) and nex_j in range(0,8) and (i!=nex_i or j!=nex_j):
                        self.legal_moves.append(self.row[i] + self.col[j] + self.row[nex_i] + self.col[nex_j])
        self.availables = self.legal_moves
        #走法类定义
        self.states = {}
        self.last_move = -1

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w

        if move not in range(self.width * self.height):
            return -1
        return move
    #
    def current_state(self):
        """return the board state from the perspective of the current player.
        state shape: 4*width*height
        """
        #state 反映了棋盘上所有棋子的位置 state[move] = player
        square_state = np.zeros((4, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width,
                            move_curr % self.height] = 1.0
            square_state[1][move_oppo // self.width,
                            move_oppo % self.height] = 1.0
            # indicate the last move location
            square_state[2][self.last_move // self.width,
                            self.last_move % self.height] = 1.0
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # indicate the colour to play
        return square_state[:, ::-1, :]

    def do_move(self, move):
        #do_move 前已经假设move是可执行的
        self.states[move] = self.current_player
        if self.current_player == 1: #黑方轮次
            i,j,nex_i,nex_j = int(move[0]),int(move[1]),int(move[2]),int(move[3])
            self.map[i][j] = 0
            if(self.map[nex_i][nex_j]!=0):
                self.white = self.white - 1
            self.map[nex_i][nex_j] = -1
        else: #白方轮次
            i, j, nex_i, nex_j = int(move[0]), int(move[1]), int(move[2]), int(move[3])
            self.map[i][j] = 0
            if (self.map[nex_i][nex_j] != 0):
                self.black = self.black - 1
            self.map[nex_i][nex_j] = 1
        #策略修正
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )
        self.last_move = move
    #change
    def has_a_winner(self):
        #黑子胜
        if self.white <= 1:
            return True, 1
        #白子胜
        if self.black <= 1:
            return True, 2
        move1 = self.get_available(1)
        move2 = self.get_available(2)
        if len(move1)==0 and len(move2)==0:
            return True, -1
        if len(move1)==0:
            return True, 2
        if len(move2)==0:
            return True, 1
        start1 = self.get_first(1)
        visited1 = [start1]
        self.recur_find(start1,visited1,-1)
        if len(visited1) == self.black:
            return True,1
        start2 = self.get_first(2)
        visited2 = [start2]
        self.recur_find(start2 ,visited2, 1)
        if len(visited2) == self.white:
            return True,2
        return False, -1
    #
    def get_available(self,player):
        moves = []
        if player == 1:   #查看黑子的可行走法
            for i in range(8):
                for j in range(8):
                    if self.map[i][j] == -1:
                        for kinds in self.legal_moves:
                            if int(kinds[0])==i and int(kinds[1])==j:
                                if self.map[int(kinds[2])][int(kinds[3])] != -1 and self.check_oppo(i,j,int(kinds[2]),int(kinds[3]),1):
                                    moves.append(kinds)
        if player == 2:    #查看白子的可行走法
            for i in range(8):
                for j in range(8):
                    if self.map[i][j] == 1:
                        for kinds in self.legal_moves:
                            if int(kinds[0])==i and int(kinds[1])==j:
                                if self.map[int(kinds[2])][int(kinds[3])] != 1 and self.check_oppo(i,j,int(kinds[2]),int(kinds[3]),-1):
                                    moves.append(kinds)
        return moves

    def check_oppo(self, r1, c1, r2, c2, piece):

        if r1 == r2:
            pieces_count = 0
            for i in range(8):
                if self.map[r1][i] != 0:
                    pieces_count = pieces_count+1
            if abs(c2-c1) != pieces_count:
                return False

        if c1 == c2:
            pieces_count = 0
            for i in range(8):
                if self.map[i][c1] != 0:
                    pieces_count = pieces_count+1
            if abs(r2-r1) != pieces_count:
                return False

        if (r1-r2)*(c1-c2)>0:
            pieces_count = 0

            t = 0
            s = 1
            while r1 - t >= 0 and c1 - t >= 0:
                if self.map[r1 - t][c1 - t] != 0:
                    pieces_count = pieces_count + 1
                t = t + 1
            while r1 + s <= 7 and c1 + s <= 7:
                if self.map[r1 + s][c1 + s] != 0:
                    pieces_count = pieces_count + 1
                s = s + 1
            if abs(r1 - r2) != pieces_count:
                return False

        if (r1-r2)*(c1-c2)<0:
            pieces_count = 0

            t = 0
            s = 1
            while r1-t>=0 and c1+t<=7:
                if self.map[r1-t][c1+t] !=0:
                    pieces_count = pieces_count +1
                t = t +1
            while r1+s<=7 and c1-s>=0:
                if self.map[r1+s][c1-s] !=0:
                    pieces_count = pieces_count + 1
                s = s + 1
            if abs(r1-r2) != pieces_count:
                return False

        if r1 == r2:
            if c1 > c2:
                c_start = c2 + 1
                c_end = c1
            else:
                c_start = c1 + 1
                c_end = c2
            for c in range(c_start, c_end):
                if self.map[r1][c] == piece:
                    return False
        elif c1 == c2:
            if r1 > r2:
                r_start = r2 + 1
                r_end = r1
            else:
                r_start = r1 + 1
                r_end = r2
            for r in range(r_start, r_end):
                if self.map[r][c1] == piece:
                    return False
        else:
            slope = (r1 - r2) // (c1 - c2)
            if slope > 0:
                if r1 > r2:
                    r_start = r2 + 1
                    c_start = c2 + 1
                    r_end = r1 - 1
                    c_end = c1 - 1
                else:
                    r_start = r1 + 1
                    c_start = c1 + 1
                    r_end = r2 - 1
                    c_end = c2 - 1
                r = r_start
                c = c_start
                while r <= r_end and c <= c_end:
                    if self.map[r][c] == piece:
                        return False
                    r += 1
                    c += 1
            else:
                if r1 > r2:
                    r_start = r1 - 1
                    c_start = c1 + 1
                    r_end = r2 + 1
                    c_end = c2 - 1
                else:
                    r_start = r2 - 1
                    c_start = c2 + 1
                    r_end = r1 + 1
                    c_end = c1 - 1
                r = r_start
                c = c_start
                while r >= r_end and c <= c_end:
                    if self.map[r][c] == piece:
                        return False
                    r -= 1
                    c += 1
        return True

    def get_first(self,player):
        if player == 1:  #找到一个黑子
            for i in range(8):
                for j in range(8):
                    if self.map[i][j] == -1:
                        return (i,j)
        if player == 2:  #找到一个白子
            for i in range(8):
                for j in range(8):
                    if self.map[i][j] == 1:
                        return (i,j)

    def recur_find(self, tup, visited, piece):
        """
        """
        row = tup[0]
        col = tup[1]
        if row - 1 > -1:
            tup_n = (row - 1, col)
            if self.map[row - 1][col] == piece and not tup_n in visited:
                visited.append(tup_n)
                self.recur_find(tup_n, visited, piece)
            if col - 1 > -1:
                tup_nw = (row - 1, col - 1)
                if self.map[row - 1][col - 1] == piece and not tup_nw in visited:
                    visited.append(tup_nw)
                    self.recur_find(tup_nw, visited, piece)
            if col + 1 < 8:
                tup_ne = (row - 1, col + 1)
                if self.map[row - 1][col + 1] == piece and not tup_ne in visited:
                    visited.append(tup_ne)
                    self.recur_find(tup_ne, visited, piece)
        if row + 1 < 8:
            tup_s = (row + 1, col)
            if self.map[row + 1][col] == piece and not tup_s in visited:
                visited.append(tup_s)
                self.recur_find(tup_s, visited, piece)
            if col - 1 > -1:
                tup_sw = (row + 1, col - 1)
                if self.map[row + 1][col - 1] == piece and not tup_sw in visited:
                    visited.append(tup_sw)
                    self.recur_find(tup_sw, visited, piece)
            if col + 1 < 8:
                tup_se = (row + 1, col + 1)
                if self.map[row + 1][col + 1] == piece and not tup_se in visited:
                    visited.append(tup_se)
                    self.recur_find(tup_se, visited, piece)
        if col - 1 > -1:
            tup_w = (row, col - 1)
            if self.map[row][col - 1] == piece and not tup_w in visited:
                visited.append(tup_w)
                self.recur_find(tup_w, visited, piece)
        if col + 1 < 8:
            tup_e = (row, col + 1)
            if self.map[row][col + 1] == piece and not tup_e in visited:
                visited.append(tup_e)
                self.recur_find(tup_e, visited, piece)
        return visited

    #change
    def game_end(self):
        """Check whether the game is ended or not"""
        #平局时winner = -1
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        return False, -1
    #
    def get_current_player(self):
        return self.current_player


class Game(object):
    """game server"""

    def __init__(self, board, **kwargs):
        self.board = board
    #change
    def start_play(self, player1, player2, start_player=0, is_shown=0):
        """start a game between two players"""
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        #if is_shown:
            #self.graphic(self.board, player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)
            # if is_shown:
            #     self.graphic(self.board, player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner
    def start_self_play(self, player, is_shown=0, temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []
        while True:
            #构成训练数据
            move, move_probs = player.get_action(self.board,
                                                 temp=temp,
                                                 return_prob=1)
            # store the data
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)
            # perform a move
            self.board.do_move(move)
            end, winner = self.board.game_end()
            if end:
                # winner from the perspective of the current player of each state
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                # reset MCTS root node
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)
