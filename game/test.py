from tkinter import *

root = Tk()
w1 = Frame(height=200, width=500)
w2 = Frame(height=50, width=500)
w3 = Frame(height=30, width=500)

w4 = Frame(w3, height=30, width=65)
w5 = Frame(w3, height=30, width=370)
w6 = Frame(w3, height=30, width=65)

w1.grid_propagate(0)
w2.grid_propagate(0)
w1.grid(row=0, column=0, padx=2, pady=5)
w2.grid(row=1, column=0, padx=2, pady=5)
w3.grid(row=2)

w4.pack(side='left')
w5.pack(side='left')
w6.pack(side='right')
t1 = Text(w1)
t2 = Text(w2)
send_button = Button(w4, text="发送")
file_button = Button(w6, text="发送文件")

t1.grid()
t2.grid()
send_button.pack(side='left')
file_button.pack(side='right')
root.mainloop()