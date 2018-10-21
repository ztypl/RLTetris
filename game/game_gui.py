import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPainter, QColor
from .core import BoardCore


class Drawing:
    color_table = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
                  0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
    @staticmethod
    def draw_square(painter, x, y, val, s):
        if val != 0:
            color = QColor(Drawing.color_table[val])
            painter.fillRect(x+1, y+1, s-2, s-2, color)
            painter.setPen(color.lighter())
            painter.drawLine(x, y + s - 1, x, y)
            painter.drawLine(x, y, x + s - 1, y)
            painter.setPen(color.darker())
            painter.drawLine(x + 1, y + s - 1, x + s - 1, y + s - 1)
            painter.drawLine(x + s - 1, y + s - 1, x + s - 1, y + 1)


class Board(QFrame):
    def __init__(self, parent, grid_size, width_blocks, height_blocks):
        self.grid_size = grid_size
        super().__init__(parent)
        self.core = BoardCore(width=width_blocks, height=height_blocks)
        self.setFixedSize(grid_size * width_blocks, grid_size * height_blocks)

    def paintEvent(self, event):
        painter = QPainter(self)
        for i in range(self.core.height):
            for j in range(self.core.width):
                val = self.core.get_value(i, j)
                Drawing.draw_square(painter, j * self.grid_size, i * self.grid_size, val, self.grid_size)

        for x, y in self.core.get_active_shape():
            val = self.core.active_shape.shape_id + 1
            Drawing.draw_square(painter, y * self.grid_size, x * self.grid_size, val, self.grid_size)


class NextBlockPanel(QFrame):
    def __init__(self, parent, grid_size):
        self.grid_size = grid_size
        super().__init__(parent)
        self.setFixedSize(grid_size * 4, grid_size * 2)

    def paintEvent(self, event):
        painter = QPainter(self)


class GameGUI(QMainWindow):
    BEFORE_START = 0
    RUNNING = 1
    PAUSED = 2
    OVER = 3

    sgn_game_over = pyqtSignal()

    def __init__(self, speed=1000):
        super().__init__()
        self.speed = speed
        self.is_next_shape = True

        # flag
        self.game_status = self.BEFORE_START    # 0：未开始 1：正在运行 2：暂停 3：游戏结束

        # signal
        self.sgn_game_over.connect(self.game_over)

        # gui
        self.board = None
        self.timer = None
        self.init_gui()
        self.start()


    def init_gui(self, width_block=10, height_block=22, grid_size=20):
        h_layout = QHBoxLayout()
        self.board = Board(self, grid_size, width_block, height_block)
        h_layout.addWidget(self.board)

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('Tetris')
        self.setFixedSize(self.board.width(), self.board.height())


        self.show()



    def start(self):
        self.board.core.generate_next_shape()
        self.is_next_shape = False
        self.game_status = self.RUNNING
        self.timer.start(self.speed, self)
        self.update()

    def update_window(self):
        self.board.update()
        self.update()

    def next_block(self):
        if self.board.core.merge_board():
            self.board.core.remove_lines()
            self.board.core.generate_next_shape()
            return True
        else:
            self.sgn_game_over.emit()
            return False

    def game_over(self):
        print('close')
        self.close()



    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.board.core.move_down():
                pass
            else:
                self.next_block()
            self.update_window()
        else:
            super().timerEvent(event)

    def keyPressEvent(self, event):
        if self.game_status == self.RUNNING:
            key = event.key()
            if key in {Qt.Key_Left, Qt.Key_A}:
                self.board.core.move_left()
                self.update_window()
                return
            elif key in {Qt.Key_Right, Qt.Key_D}:
                self.board.core.move_right()
                self.update_window()
                return
            elif key in {Qt.Key_Up, Qt.Key_W}:
                self.board.core.rotate_right()
                self.update_window()
                return
            elif key in {Qt.Key_Down, Qt.Key_S}:
                if not self.board.core.move_down():
                    self.next_block()
                self.update_window()
        super().keyPressEvent(event)
        return



