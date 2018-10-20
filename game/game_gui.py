import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
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


class GameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_gui()

    def init_gui(self, width_block=10, height_block=22, grid_size=40):
        h_layout = QHBoxLayout()
        self.board = Board(self, grid_size, width_block, height_block)
        h_layout.addWidget(self.board)

        self.setWindowTitle('Tetris')
        self.show()

        self.setFixedSize(self.board.width(), self.board.height())

    def start(self):
        pass



