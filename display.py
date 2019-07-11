# from chessboard import ChessBoard
# from ai import searcher

from game import Board
from human_play import Human
from mcts_pure import MCTSPlayer
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QPainter

WIDTH = 800
HEIGHT = 800
MARGIN = 50
GRID = (WIDTH - 2 * MARGIN) / (8 - 1)
PIECE = 50
EMPTY = 0
# BLACK = 1
# WHITE = 2
BLACK = -1
WHITE = 1

#from PyQt5.QtMultimedia import QSound


# ----------------------------------------------------------------------
# 定义线程类执行AI的算法
# ----------------------------------------------------------------------
class AI(QtCore.QThread):
    finishSignal = QtCore.pyqtSignal(int, int, int, int)

    # 构造函数里增加形参
    def __init__(self, board, parent=None):
        super(AI, self).__init__(parent)
        self.board = board

    # 重写 run() 函数
    def run(self):
        self.ai = MCTSPlayer(c_puct=5, n_playout=20)
        # self.ai.board = self.board
        move = self.ai.get_action(self.board)
        self.board.do_move(move)
        print(move)
        self.finishSignal.emit(int(move[0]), int(move[1]), int(move[2]), int(move[3]))


# ----------------------------------------------------------------------
# 重新定义Label类
# ----------------------------------------------------------------------
class LaBel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        e.ignore()


class GoBang(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tup = (None,None)
        self.board = Board()  # 棋盘类
        self.board.init_board(1)
        palette1 = QPalette()  # 设置棋盘背景
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('img/linesofaction.png')))
        self.setPalette(palette1)
        # self.setStyleSheet("board-image:url(img/chessboard.jpg)")  # 不知道这为什么不行
        self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状
        # self.sound_piece = QSound("sound/luozi.wav")  # 加载落子音效
        # self.sound_win = QSound("sound/win.wav")  # 加载胜利音效
        # self.sound_defeated = QSound("sound/defeated.wav")  # 加载失败音效

        self.resize(WIDTH, HEIGHT)  # 固定大小 540*540
        self.setMinimumSize(QtCore.QSize(WIDTH, HEIGHT))
        self.setMaximumSize(QtCore.QSize(WIDTH, HEIGHT))

        self.setWindowTitle("Lines-Of-Action")  # 窗口名称
        self.setWindowIcon(QIcon('img/black.png'))  # 窗口图标

        # self.lb1 = QLabel('            ', self)
        # self.lb1.move(20, 10)

        self.black = QPixmap('img/black.png')
        self.white = QPixmap('img/white.png')

        self.piece_now = BLACK  # 黑棋先行
        self.my_turn = True  # 玩家先行
        self.step = 0  # 步数
        self.x, self.y = 1000, 1000

        #self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
        # self.mouse_point.setScaledContents(True)
        # self.mouse_point.setPixmap(self.black)  # 加载黑棋
        # self.mouse_point.setGeometry(270, 270, PIECE, PIECE)
        self.pieces = [[LaBel(self),LaBel(self),LaBel(self),LaBel(self),LaBel(self),LaBel(self),LaBel(self),LaBel(self)] for _ in range(8)] # 新建棋子标签，准备在棋盘上绘制棋子
        # for piece in self.pieces:
        #     piece.setVisible(True)  # 图片可视
        #     piece.setScaledContents(True)  # 图片大小根据标签大小可变
        for i in range(8):
            for j in range(8):
                self.pieces[i][j].setVisible(True)
                self.pieces[i][j].setScaledContents(True)
        #self.mouse_point.raise_()  # 鼠标始终在最上层
        self.ai_down = True  # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效，要忽略掉 mousePressEvent

        self.setMouseTracking(True)

        self.DrawPieces()

        self.show()

    def DrawPieces(self):
        for i in range(8):
            for j in range(8):
                if self.board.map[i][j] == -1:
                    x, y = self.coordinate_transform_map2pixel(i, j)
                    self.pieces[i][j].setPixmap(self.black)
                    self.pieces[i][j].setGeometry(x, y, PIECE, PIECE)
                if self.board.map[i][j] == 1:
                    x, y = self.coordinate_transform_map2pixel(i, j)
                    self.pieces[i][j].setPixmap(self.white)
                    self.pieces[i][j].setGeometry(x, y, PIECE, PIECE)
                if self.board.map[i][j] == 0:
                    x, y = self.coordinate_transform_map2pixel(i, j)
                    self.pieces[i][j].setPixmap(QPixmap(""))
                    self.pieces[i][j].setGeometry(x, y, PIECE, PIECE)
    def paintEvent(self, event):  # 画出指示箭头
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def mouseMoveEvent(self, e):  # 黑色棋子随鼠标移动
        # self.lb1.setText(str(e.x()) + ' ' + str(e.y()))
        # self.mouse_point.move(e.x() - 16, e.y() - 16)
        e.accept()

    def mousePressEvent(self, e):  # 玩家下棋
        if e.button() == Qt.LeftButton and self.ai_down == True:
            x, y = e.x(), e.y()  # 鼠标坐标
            i, j = self.coordinate_transform_pixel2map(x, y)# 对应棋盘坐标
            new_x,new_y = self.coordinate_transform_map2pixel(i,j)
            if not i is None and not j is None:# 棋子落在棋盘上，排除边缘
                if self.board.map[i][j] == -1:# 人类玩家执黑子
                    self.board.current_player = 1
                    # self.draw(i, j)
                    print(self.tup)
                    self.tup = (i,j)
                else:
                    (old_i,old_j) = self.tup
                    if old_i is None or old_j is None:
                        return
                    moves = self.board.get_available(1)
                    my_move = str(old_i)+str(old_j)+str(i)+str(j)
                    print("人类当前走法")
                    print(moves)
                    print("人类当前棋盘")
                    print(self.board.map)
                    if my_move in moves:
                        self.board.do_move(my_move)
                        self.pieces[old_i][old_j].setPixmap(QPixmap(""))
                        self.pieces[i][j].setPixmap(self.black)
                        self.pieces[i][j].setGeometry(new_x, new_y, PIECE, PIECE)
                        end, winner = self.board.game_end()
                        if end:
                            self.gameover(winner)
                        if self.board.current_player == 2:
                            self.ai_down = False
                            board = self.board
                            self.AI = AI(board)  # 新建线程对象，传入棋盘参数
                            self.AI.finishSignal.connect(self.AI_draw)  # 结束线程，传出参数
                            self.AI.start()
                    else:
                        print("error move")
                      # run

    def AI_draw(self, i, j,nxt_i,nxt_j):
        print(i,j,nxt_i,nxt_j)
        self.pieces[i][j].setPixmap(QPixmap(""))
        self.pieces[nxt_i][nxt_j].setPixmap(self.white) # AI
        x,y = self.coordinate_transform_map2pixel(nxt_i, nxt_j)
        self.pieces[nxt_i][nxt_j].setGeometry(x, y, PIECE, PIECE)
        end, winner = self.board.game_end()
        if end:
            self.gameover(winner)
        self.ai_down = True
        self.update()


    def drawLines(self, qp):  # 指示AI当前下的棋子
        if self.step != 0:
            pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
            qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
            qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)

    def coordinate_transform_map2pixel(self, i, j):
        # 从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换
        return MARGIN + j * GRID - PIECE / 2, MARGIN + i * GRID - PIECE / 2

    def coordinate_transform_pixel2map(self, x, y):
        # 从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换
        i, j = int(round((y - MARGIN) / GRID)), int(round((x - MARGIN) / GRID))
        # 有MAGIN, 排除边缘位置导致 i,j 越界
        if i < 0 or i >= 15 or j < 0 or j >= 15:
            return None, None
        else:
            return i, j

    def gameover(self, winner):
        if winner == 1:
            #self.sound_win.play()
            reply = QMessageBox.question(self, 'You Win!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        else:
            if winner == 2:
                #self.sound_defeated.play()
                reply = QMessageBox.question(self, 'You Lost!', 'Continue?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            else:
                reply = QMessageBox.question(self, 'Tie', 'Continue?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:  # 复位
            # self.piece_now = BLACK
            # self.mouse_point.setPixmap(self.black)
            # self.step = 0
            # for piece in self.pieces:
            #     piece.clear()
            # self.chessboard.reset()
            self.board.init_board(1)
            self.ai_down = True
            self.board.current_player = 1
            self.DrawPieces()
            self.update()
        else:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GoBang()
    sys.exit(app.exec_())
