import tkinter as tk
from random import randint, choice
import time
import sys
import socket
import threading
from server_config import *


def create_socket():
    global data_client, conn, stop_t1, connected, game_on
    stop_t1 = 1
    connected = 0
    sock = socket.socket()
    sock.bind(('', 9090))
    sock.listen(1)
    conn, addr = sock.accept()
    print('connected:', addr)
    connected = 1
    while True:
        if event_stop.is_set():
            break
        if game_on == 2:  # goal
            conn.send(('score' + str(score1) + ':' + str(score2)).encode())
            time.sleep(1)
        elif game_on == 1:
            balls_send = []
            for key in balls:
                balls_send.append((balls[key].color, balls[key].x, balls[key].y))
            data_client = conn.recv(1024).decode()
            conn.send((rack_client + ':' + str(balls_send)).encode())
        elif game_on == 0:  # game over
            conn.send(('end-' + str(score1) + ':' + str(score2)).encode())
            game_on = 3
    stop_t1 = 0


def connection_to_client():
    global event_stop
    t1 = threading.Thread(target=create_socket)
    event_stop = threading.Event()
    t1.start()


class GameMenu(tk.Frame):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("Tennis")
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar)
        file_menu.add_command(label="Quit", command=self.on_exit)
        menubar.add_cascade(label="Game", menu=file_menu)

    def on_exit(self):
        quit_game('x')


class Ball:
    def __init__(self, dx, dy, x, y):
        self.color = choice(['blue', 'green', 'red', 'brown', 'yellow'])
        self.x = x
        self.y = y
        self.r = 10
        self.z = 0
        self.dx = dx
        self.dy = dy
        self.ball_id = canvas.create_oval(self.x - self.r, self.y - self.r,
                                          self.x + self.r, self.y + self.r, fill=self.color
                                          )
        self.live_ball = time.time()
        self.t_t = time.time()

    def move(self):
        def move_ball(self, rx, ry, rx1, ry1):
            # rz = 0 if rx > rx1 else 1
            if self.dx > 0:  # the ball moves to the right
                if rx <= rx1:  # the racket moves to the left
                    if self.x <= rx:  # the ball is to the left of the racket
                        self.z = 1
                    else:
                        if self.z == 1 and (ry < self.y < ry + rack_length):
                            self.dx = self.dx + (rx1 - rx) if (rx1 - rx) < 10 else self.dx + 10
                            self.dx = -self.dx
                            self.z = 0
                        else:
                            self.z = 0
                        if self.x + self.r + self.dx >= WIDTH and not 200 < self.y < 400:
                            self.dx = -self.dx
                else:  # the racket moves to the right
                    if self.x >= rx:
                        self.z = 0
                    else:
                        if self.z == 0 and (ry < self.y < ry + rack_length):
                            self.dx = self.dx + (rx - rx1) if (rx - rx1) < 10 else self.dx + 10
                            self.z = 1
                        else:
                            self.z = 1
                        if self.x + self.r + self.dx >= WIDTH and not 200 < self.y < 400:
                            self.dx = -self.dx
            else:  # the ball moves to the left
                if rx >= rx1:  # the racket moves to the right
                    if self.x >= rx:  # the ball is to the right of the racket
                        self.z = 1
                    else:
                        if self.z == 1 and (ry < self.y < ry + rack_length):
                            self.dx = self.dx - (rx - rx1) if (rx - rx1) < 10 else self.dx - 10
                            self.dx = -self.dx
                            self.z = 0
                        else:
                            self.z = 0
                        if self.x - self.r + self.dx <= 0 and not 200 < self.y < 400:
                            self.dx = -self.dx
                else:  # the racket moves to the right
                    if self.x >= rx:
                        self.z = 0
                    else:
                        if self.z == 0 and (ry < self.y < ry + rack_length):
                            self.dx = self.dx + (rx1 - rx) if (rx1 - rx) < 10 else self.dx + 10
                            self.z = 1
                        else:
                            self.z = 1
                        if self.x + self.r + self.dx >= WIDTH and not 200 < self.y < 400:
                            self.dx = -self.dx
            if self.y + self.r - self.dy >= HEIGHT or self.y - self.r - self.dy <= 0:
                self.dy = -self.dy
            self.x = round(self.x + self.dx)
            self.y = round(self.y - self.dy)
            for rebound in balls:  # rebound_from_ball
                if self.ball_id != balls[rebound].ball_id:
                    if ((balls[rebound].x - self.r < self.x < balls[rebound].x + self.r)
                            and (balls[rebound].y - self.r < self.y < balls[rebound].y + self.r)
                    ):
                        if time.time() - self.t_t > 0.5:
                            self.dx = -self.dx
                            self.dy = -self.dy
                        self.t_t = time.time()
                self.dy -= 0.2

        if self.x < WIDTH / 2:
            move_ball(self, rx, ry, rx1, ry1)
        else:
            move_ball(self, r2x, r2y, r2x1, r2y)

    def show(self):
        canvas.coords(self.ball_id, self.x - self.r, self.y - self.r,
                      self.x + self.r, self.y + self.r
                      )
        if self.dx != 0 and self.dy != 0:
            self.dx -= 0.03 * self.dx / abs(self.dx)
            self.dy -= 0.05 * self.dy / abs(self.dy)

    def hitting(self):
        global score1, score2
        if self.x + self.r >= WIDTH and 200 < self.y < 400 and not (r2y <= self.y <= r2y + rack_length):
            score2 += 1
            hit = 1
            if score2 == limit_score:
                hit = 2
                end_game()
            return hit
        elif self.x - self.r <= 0 and 200 < self.y < 400 and not (ry <= self.y <= ry + rack_length):
            score1 += 1
            hit = 1
            if score1 == limit_score:
                hit = 2
                end_game()
            return hit
        return False


class Racket:
    def __init__(self):
        self.x = 300
        self.y = 300
        self.fence_l_top = canvas.create_line(5, 0, 5, 200, width=8, fill='blue')
        self.fence_l_bottom = canvas.create_line(5, 400, 5, 600, width=8, fill='blue')
        self.fence_r_top = canvas.create_line(795, 0, 795, 200, width=8, fill='blue')
        self.fence_r_bottom = canvas.create_line(795, 400, 795, 600, width=8, fill='blue')
        self.racket_id = canvas.create_line(self.x, self.y, self.x, self.y + rack_length, fill='black', width=5)

    def show(self, event):
        global rack_client, rx, ry, rx1, ry1
        rx1 = rx
        ry1 = ry
        canvas.coords(self.racket_id, rx, ry, rx, ry + rack_length)
        rack_client = str(rx) + '/' + str(ry)
        rx = event.x if event.x < 300 else 300
        ry = event.y


def start_new_game():
    global shot_number, game_on, balls, root, racket2_id, score1, score2
    score1 = 0
    score2 = 0
    root.config(cursor='none')
    balls = {}
    shot_number = 0
    add_racket()
    racket2_id = canvas.create_line(50, 50, 50, 50 + rack_length, fill='red', width=7)
    game_on = 1


def new_game(event):
    global button1, button2
    button1.destroy()
    button2.destroy()
    canvas.delete(label_score2)
    del button1
    del button2
    start_new_game()


def add_racket():
    global racket
    racket = Racket()


def racket2(x, y):
    global r2x, r2y, r2x1, r2y1
    r2x1 = r2x
    r2y1 = r2y
    canvas.coords(racket2_id, r2x, r2y, r2x, r2y + rack_length)
    r2x = int(x)
    r2y = int(y)


def ball_throw():
    global shot_number
    shot_number += 1
    add_ball()


def add_ball():
    dx = randint(-10, 10)*4
    dy = randint(-10, 10)
    balls['ball_%d' % shot_number] = Ball(dx, dy, WIDTH/2, HEIGHT/2)


def end_game():
    global button1, button2, game_on, score1, score2, root, label_score2
    canvas.delete(racket.racket_id)
    canvas.delete(racket2_id)
    canvas.delete(racket.fence_r_top)
    canvas.delete(racket.fence_r_bottom)
    canvas.delete(racket.fence_l_top)
    canvas.delete(racket.fence_l_bottom)
    canvas.itemconfig(label_score, text='')
    label_score2 = canvas.create_text(250, 110, font=('Helvetica','30','bold'), text='')
    canvas.itemconfig(label_score2, text='Score ' + str(score1) + ' : ' + str(score2))
    root.config(cursor='')
    button1 = tk.Button(master=root, text="Quit", bg="red")
    button1.bind('<Button-1>', quit_game)
    button1.place(x=300, y=500)
    button2 = tk.Button(master=root, text="New Game", bg="green")
    button2.bind('<Button-1>', new_game)
    button2.place(x=400, y=500)
    delete_objects()


def delete_objects():
    global racket
    for i in balls:
        canvas.delete(balls[i].ball_id)
    del racket


def quit_game(x):
    event_stop.set()
    while True:
        if stop_t1 == 0:
            sys.exit()


st = 0
def tick():
    global interval, rand, d_c, racket2_id, connected, game_on, st
    if st == 5:
        time.sleep(1.5)
        game_on = 1
        st = 0
    if connected:
        d_c = (str(data_client)).split(sep='/')
        r2x = d_c[0]
        r2y = d_c[1]
        if game_on == 1:
            canvas.bind('<Motion>', racket.show)
            racket2(r2x, r2y)
            interval += 0.1
            if interval >= rand:
                ball_throw()
                interval = 0
                rand = randint(10, 30)
            for key in balls:
                balls[key].move()
                balls[key].show()

                if time.time() - balls[key].live_ball > 10:
                    canvas.delete(balls[key].ball_id)
                    del balls[key]
                    break
                hit_state = balls[key].hitting()
                if hit_state == 1:
                    game_on = 2
                    canvas.delete(balls[key].ball_id)
                    del balls[key]
                    canvas.itemconfig(label_score, text='Score >>> ' + str(score1) + ' : ' + str(score2))
                    st = 5
                    break
                if hit_state == 2:
                    game_on = 0
                    break
    root.after(30, tick)


def main():
    global interval, rand, root, canvas, label_score, conn
    interval = 0
    rand = randint(5, 30)
    root = tk.Tk()
    root.iconbitmap('racket.ico')
    root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
    canvas = tk.Canvas(root, bg='yellow')
    canvas.pack(expand=1, fill='both')
    GameMenu()
    label_score = canvas.create_text(50, 10, text='')
    canvas.itemconfig(label_score, text='')
    connection_to_client()
    start_new_game()
    tick()
    root.mainloop()


main()
