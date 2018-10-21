# ref: https://github.com/LoveDaisy/tetris_game/blob/master/tetris_model.py

import random


class Shape:
    I = 0
    L = 1
    J = 2
    T = 3
    O = 4
    S = 5
    Z = 6

    shapeCoord = (
        ((0, -2), (0, -1), (0, 0), (0, 1)),      # I
        ((0, -1), (0, 0), (0, 1), (1, -1)),      # J
        ((0, -1), (0, 0), (0, 1), (1, 1)),     # L
        ((0, -1), (0, 0), (0, 1), (1, 0)),      # T
        ((0, 0), (0, -1), (1, 0), (1, -1)),     # O
        ((0, 0), (1, 0), (0, 1), (1, -1)),    # S
        ((0, 0), (1, 0), (1, -1), (0, 1))     # Z
    )

    def __init__(self, shape_id, direction_id, cx=-1, cy=-1):
        """顺时针旋转+1， 逆时针旋转-1"""
        self.shape_id = shape_id
        self.direction_id = direction_id
        self.cx = cx
        self.cy = cy

    def get_local_coord(self, dd=0):
        coords = self.shapeCoord[self.shape_id]
        direction_id = (self.direction_id + dd) % 4
        if direction_id == 1 and self.shape_id != self.O:
            return tuple((-y, x) for x, y in coords)
        elif direction_id == 2 and self.shape_id in {self.L, self.J, self.T}:
            return tuple((-x, -y) for x, y in coords)
        elif direction_id == 3:
            if self.shape_id in {self.I, self.Z, self.S}:
                return tuple((-y, x) for x, y in coords)
            elif self.shape_id != self.O:
                return tuple((y, -x) for x, y in coords)
        return coords

    def set_center(self, x, y):
        self.cx = x
        self.cy = y

    def get_global_coord(self, dd=0):
        return tuple((self.cx + x, self.cy + y) for x, y in self.get_local_coord(dd))

    def get_global_coord_offset(self, dx, dy, dd=0):
        return tuple((x + dx, y + dy) for x, y in self.get_global_coord(dd))


class BoardCore:
    score_map = [0, 40, 100, 300, 1200]

    def __init__(self, width=10, height=22, method="normal"):
        self.width = width
        self.height = height

        self.data = [[0 for x in range(self.width)] for y in range(self.height)]
        self.score = 0
        if method == 'random':
            self.random_init()
        self.active_shape = None
        self.next_shape = self.generate_shape()

    def get_value(self, i, j):
        return self.data[self.height - i - 1][j]

    def get_row(self, i):
        return self.data[self.height - i - 1]

    def get_active_shape(self):
        if self.active_shape:
            return [(self.height - x - 1, y) for x, y in self.active_shape.get_global_coord()]
        else:
            return []

    def get_next_shape(self):
        return self.next_shape.get_local_coord()

    def random_init(self):
        for i in range(self.height // 2):
            for j in range(self.width):
                self.data[i][j] = random.randint(0, 1)

    @staticmethod
    def generate_shape():
        return Shape(random.randint(0, 6), 0)

    # 下一个形状
    def generate_next_shape(self):
        self.active_shape = self.next_shape
        self.active_shape.set_center(self.height - 1, self.width // 2)
        self.next_shape = self.generate_shape()

    # 检测是否越界或碰撞
    def is_collapse(self, coords):
        for x, y in coords:
            if x < 0 or y < 0 or y >= self.width or \
                    (x < self.height and self.data[x][y] != 0):
                return True
        return False

    # 左移
    def move_left(self):
        coords = self.active_shape.get_global_coord_offset(0, -1)
        if not self.is_collapse(coords):
            self.active_shape.cy -= 1
            return True
        return False

    # 右移
    def move_right(self):
        coords = self.active_shape.get_global_coord_offset(0, 1)
        if not self.is_collapse(coords):
            self.active_shape.cy += 1
            return True
        return False

    # 下移
    def move_down(self):
        coords = self.active_shape.get_global_coord_offset(-1, 0)
        if not self.is_collapse(coords):
            self.active_shape.cx -= 1
            return True
        return False

    # 顺时针旋转
    def rotate_right(self):
        coords = self.active_shape.get_global_coord_offset(0, 0, 1)
        if not self.is_collapse(coords):
            self.active_shape.direction_id += 1
            self.active_shape.direction_id %= 4
            return True
        return False

    # 逆时针旋转
    def rotate_left(self):
        coords = self.active_shape.get_global_coord_offset(0, 0, -1)
        if not self.is_collapse(coords):
            self.active_shape.direction_id += 3
            self.active_shape.direction_id %= 4
            return True
        return False

    # 合并
    def merge_board(self):
        for x, y in self.active_shape.get_global_coord():
            if x < self.height and self.data[x][y] == 0:
                self.data[x][y] = self.active_shape.shape_id + 1
            else:
                return False
        return True

    # 删除整行
    def remove_lines(self):
        removed_line_id = []
        for i in range(self.height-1, -1, -1):
            if all(self.data[i]):
                self.data.pop(i)
                self.data.append([0 for _ in range(self.width)])
                removed_line_id.append(i)
        self.score += self.score_map[min(len(removed_line_id), 4)]
        return removed_line_id

