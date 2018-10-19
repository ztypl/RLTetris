import tkinter as tk

class MainFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.draw_board()
        self.pack()

    def draw_board(self, width_size=10, height_size=22, block_size=10, border_width=3, offset=2):
        width = width_size * block_size + 2 * (border_width + offset)
        height = height_size * block_size + 2 * (border_width + offset)
        self.board_frame = tk.Frame(
            self,
            width=width,
            height=height,
        )
        self.canvas_board = tk.Canvas(
            self.board_frame,
            width=width,
            height=height,
        )
        self.canvas_board.create_rectangle(offset, offset, 30, 50)
        self.canvas_board.pack(side='top')
        self.board_frame.pack()


root = tk.Tk()
app = MainFrame(master=root)
app.mainloop()