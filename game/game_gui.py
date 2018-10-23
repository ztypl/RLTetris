import sys
from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication, \
    QHBoxLayout, QVBoxLayout, QLabel, QWidget, QLCDNumber
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
    def __init__(self, parent, grid_size, width_blocks, height_blocks, border_width=5):
        self.grid_size = grid_size
        self.border_width = border_width
        super().__init__(parent)
        self.core = BoardCore(width=width_blocks, height=height_blocks)
        self.setFixedSize(grid_size * width_blocks + 2 * self.border_width,
                          grid_size * height_blocks + 2 * self.border_width)


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.setStyleSheet("border:%dpx solid red;" % self.border_width)
        for i in range(self.core.height):
            for j in range(self.core.width):
                val = self.core.get_value(i, j)
                Drawing.draw_square(painter,
                                    j * self.grid_size + self.border_width,
                                    i * self.grid_size + self.border_width,
                                    val, self.grid_size)

        for x, y in self.core.get_active_shape():
            if x >= 0 and y >= 0:
                val = self.core.active_shape.shape_id + 1
                Drawing.draw_square(painter,
                                    y * self.grid_size + self.border_width,
                                    x * self.grid_size + self.border_width,
                                    val, self.grid_size)


class NextBlockPanel(QFrame):
    def __init__(self, parent, grid_size, shape, border_width=5):
        self.grid_size = grid_size
        self.width_block = 4
        self.height_block = 4
        self.shape = shape
        self.border_width = border_width
        super().__init__(parent)
        self.setFixedSize(grid_size * self.width_block + 2 * self.border_width,
                          grid_size * self.height_block + 2 * self.border_width)


    def set_shape(self, shape):
        self.shape = shape

    def paintEvent(self, event):
        self.setStyleSheet("border:%dpx solid red;" % self.border_width)
        painter = QPainter(self)
        val = self.shape.shape_id + 1
        for x, y in self.shape.get_local_coord():
            Drawing.draw_square(painter,
                                (y + 2) * self.grid_size + self.border_width,
                                (3 - x) * self.grid_size + self.border_width,
                                val, self.grid_size)


class GameGUI(QMainWindow):
    BEFORE_START = 0
    RUNNING = 1
    PAUSED = 2
    OVER = 3

    sgn_game_over = pyqtSignal()
    sgn_update_score = pyqtSignal(int)

    def __init__(self, speed=1000):
        super().__init__()
        self.speed = speed

        # flag
        self.game_status = self.BEFORE_START    # 0：未开始 1：正在运行 2：暂停 3：游戏结束

        # signal
        self.sgn_game_over.connect(self.game_over)
        self.sgn_update_score.connect(self.update_score)

        # gui
        self.board = None
        self.next_panel = None
        self.score_ui = None
        self.timer = None
        self.init_gui()
        self.start()

    def init_gui(self, width_block=10, height_block=22, grid_size=20):
        center_widget = QWidget()

        h_layout = QHBoxLayout()
        self.board = Board(None, grid_size, width_block, height_block)
        self.next_panel = NextBlockPanel(None, grid_size, self.board.core.next_shape)

        self.score_ui = QLCDNumber(self)
        self.score_ui.setDigitCount(6)
        self.score_ui.setSegmentStyle(QLCDNumber.Flat)
        self.score_ui.setFixedHeight(50)
        self.score_ui.display(0)

        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.next_panel, 0, Qt.AlignCenter | Qt.AlignTop)
        right_layout.addWidget(QLabel("<h3>Score</h3>"), 0, Qt.AlignLeft | Qt.AlignTop)
        right_layout.addWidget(self.score_ui, 1, Qt.AlignCenter | Qt.AlignTop)
        right_layout.setSpacing(0)
        right_widget.setLayout(right_layout)

        h_layout.addWidget(self.board)
        h_layout.addWidget(right_widget)
        h_layout.setSpacing(0)

        self.timer = QBasicTimer()
        self.setFocusPolicy(Qt.StrongFocus)

        self.setWindowTitle('Tetris')
        center_widget.setFixedSize(self.board.width() + self.next_panel.width() + 30, self.board.height()+15)
        self.setFixedSize(center_widget.width(), center_widget.height())
        center_widget.setLayout(h_layout)

        self.setCentralWidget(center_widget)

        print(self.dockOptions())

        self.show()

    def start(self):
        self.board.core.remove_lines()
        self.board.core.generate_next_shape()
        self.next_panel.set_shape(self.board.core.next_shape)
        self.game_status = self.RUNNING
        self.timer.start(self.speed, self)
        self.update()

    def update_window(self):
        self.board.update()
        self.next_panel.update()
        # self.score_ui.update()
        self.update()

    def next_block(self):
        if self.board.core.merge_board():
            self.board.core.remove_lines()
            self.sgn_update_score.emit(self.board.core.score)
            self.board.core.generate_next_shape()
            self.next_panel.set_shape(self.board.core.next_shape)
            return True
        else:
            self.sgn_game_over.emit()
            return False

    def game_over(self):
        print('close')
        self.close()

    def update_score(self, score):
        self.score_ui.display(score)

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



