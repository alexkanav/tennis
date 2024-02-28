import tkinter as tk
from random import randint
import sys
import socket
from client_config import *


class Racket:
    def __init__(self):
        self.x = 780
        self.y = 300
        self.racket_id = canvas.create_line(self.x, self.y, self.x, self.y + rack_length, fill='black', width=7)
        self.fence_l_top = canvas.create_line(5, 0, 5, 200, width=8, fill='blue')
        self.fence_l_bottom = canvas.create_line(5, 400, 5, 600, width=8, fill='blue')
        self.fence_r_top = canvas.create_line(795, 0, 795, 200, width=8, fill='blue')
        self.fence_r_bottom = canvas.create_line(795, 400, 795, 600, width=8, fill='blue')

    def show(self, event):
        global send_koord_rack1
        self.y = event.y
        self.x = event.x if event.x > 500 else 500
        canvas.coords(self.racket_id, self.x, self.y, self.x, self.y + rack_length)
        send_koord_rack1 = str(self.x) + '/' + str(self.y)


def add_rackets():
    global racket, racket1_id
    racket = Racket()
    racket1_id = canvas.create_line(200, 200, 200, 250, fill='red', width=7)


def koord_rack_ball():
    global score1, score2
    sock.send(send_koord_rack1.encode())
    data = sock.recv(1024).decode()
    if 'score' in data:
        score1 = data[5]
        score2 = data[7]
        canvas.itemconfig(label_score, text='Score >>> ' + str(score1) + ' : ' + str(score2))
        return '50/50', []
    if 'end' in data:
        score1 = data[4]
        score2 = data[6]
        game_over()
        return '50/50', []
    else:
        racket_pos, ball_pos = data.split(sep=':')
        return racket_pos, eval(ball_pos)


def show_racket1(racket_pos):
    x, y = racket_pos.split(sep='/')
    x = int(x)
    y = int(y)
    canvas.coords(racket1_id, x, y, x, y + rack_length)


def show_balls(ball_pos):
    for i in ball_pos:
        ball_pos2.append(canvas.create_oval(i[1] - R, i[2] - R, i[1] + R, i[2] + R, fill=i[0]))


def delete_balls():
    for i in ball_pos2:
        canvas.delete(i)
    ball_pos.clear()


def game_over():
    global game_on, button1, button2, label_score2
    game_on = 0
    canvas.delete(racket.racket_id)
    canvas.delete(racket1_id)
    canvas.delete(racket.fence_r_top)
    canvas.delete(racket.fence_r_bottom)
    canvas.delete(racket.fence_l_top)
    canvas.delete(racket.fence_l_bottom)
    root.config(cursor='')
    canvas.itemconfig(label_score, text='')
    label_score2 = canvas.create_text(250, 110, font=('Helvetica', '30', 'bold'), text='')
    canvas.itemconfig(label_score2, text='Score ' + str(score1) + ' : ' + str(score2))
    button1 = tk.Button(master=root, text="Quit", bg="red")
    button1.bind('<Button-1>', quit_game)
    button1.place(x=300, y=500)
    button2 = tk.Button(master=root, text="New Game", bg="green")
    button2.bind('<Button-1>', new_game)
    button2.place(x=400, y=500)

def quit_game(x):
    sys.exit()

def new_game(x):
    global game_on, button1, button2
    game_on = 1
    if x != 5:
        canvas.delete(label_score2)
        button1.destroy()
        button2.destroy()
        del button1
        del button2
    root.config(cursor='none')
    add_rackets()


def tick():
    global ball_pos, dict_ball_pos
    if game_on == 1:
        delete_balls()
        canvas.bind('<Motion>', racket.show)
        racket_pos, ball_pos = koord_rack_ball()
        show_racket1(racket_pos)
        show_balls(ball_pos)
    root.after(30, tick)


def main():
    global interval, rand, root, score, canvas, label_score, sock, b1, ball_pos, ball_pos2, score1, score2
    interval = 0
    ball_pos = []
    ball_pos2 = []
    score1 = 0
    score2 = 0
    rand = randint(5, 30)
    root = tk.Tk()
    root.title('Tennis')
    root.iconbitmap('racket.ico')
    root.geometry(str(WIDTH) + 'x' + str(HIGHT))
    canvas = tk.Canvas(root, bg='yellow')
    canvas.pack(expand=1, fill='both')
    label_score = canvas.create_text(50, 10, text='')
    new_game(5)
    sock = socket.socket()
    sock.connect((host, port))
    tick()
    root.mainloop()

main()
