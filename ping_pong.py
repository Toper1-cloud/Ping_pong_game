from pygame import *
from random import randint, uniform, choice
import time as py_time

width = 1540   # длина окна
height = 800  # высота окна
window = display.set_mode((width, height))
display.set_caption('Пинг_понг')
font.init()
mixer.init()

restart_ready = False

font_size = 20
font_name = 'Arial'

game_over = False

game_font = font.SysFont('Arial', 48)

white_color = (255, 255, 255) #белый
green_color = (0, 255, 0) #зелёный
blue = (0, 0, 255) #синий
light_blue = (173, 216, 230) #светло синий
red_color = (255, 0, 0) #красный
light_red = (255, 71, 76) #светло красный
black_color = (0, 0, 0) #чёрный

clock = time.Clock()
FPS = 120

loser_text = ''
score_left = 0
score_right = 0

WIN_SCORE = 5
countdown_active = False
goal_scored = False
countdown_start = 0
winner_text = ''

class GameSprite(sprite.Sprite):
    def __init__(self, picture, x, y, speed=1, w=100, h=100):
        super().__init__()
        self.picture = picture
        self.speed = speed
        self.w = w
        self.h = h
        self.sprite = transform.scale(image.load(self.picture), (self.w, self.h))
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.sprite, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, x, y, up_key, down_key, f_t=1):
        if f_t == 1:
            pict = 'rocket1.png'
        else:
            pict = 'rocket2.png'
        super().__init__(pict, x, y, 1, 150, 200)
        #self.sprite = transform.scale(image.load('rocket.png'), (100, 500))
        self.up_key = up_key
        self.down_key = down_key
        self.rect = self.sprite.get_rect(topleft=(x, y))
        self.x_copy = x
        self.y_copy = y

    def goes(self):
        key_pressed = key.get_pressed()
        if key_pressed[self.up_key] and self.rect.y > 0: #вверх
            self.rect.y -= 15        
        if key_pressed[self.down_key] and self.rect.bottom < height: #вниз
            self.rect.y += 15

    def starts(self):
        self.rect.x = self.x_copy
        self.rect.y = self.y_copy

class Ball(GameSprite):
    def __init__(self):
        super().__init__('bal.png', width // 2 - 30, height // 2 - 30, 1, 60, 60)
        self.sprite = transform.scale(image.load('bal.png'), (60, 60))
        self.dx = 10 * choice([-1, 1])  #случайное направление влево или вправо
        self.dy = 5

    def update(self, players):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if self.rect.top <= 0 or self.rect.bottom >= height:    #отскок от верха и низа
            self.dy = -self.dy

        for player in players:  #отскок от ракеток
            if self.rect.colliderect(player.rect):
                if self.dx < 0 and self.rect.left <= player.rect.right:
                    self.dx = abs(self.dx)
                elif self.dx > 0 and self.rect.right >= player.rect.left:
                    self.dx = -abs(self.dx)

background = GameSprite('fone.jpg', 0, 0, 1, width, height)

player_left = Player(100, 540, K_w, K_s, f_t=1)
player_right = Player(1440, 540, K_UP, K_DOWN, f_t=2)
players = [player_left, player_right]

ball = Ball()

player_s = sprite.Group()
player_s.add(player_left)
player_s.add(player_right)

mixer.music.load('Main_Theme.mp3')
mixer.music.play()

restart_ready = False
game = True
while game:
    background.reset()
    for player in players:
        player.reset()
    ball.reset()

    score_text = game_font.render(f'{score_left} : {score_right}', True, black_color)
    window.blit(score_text, score_text.get_rect(center=(width // 2, 40)))

    if countdown_active:
        for player in players:      # двигаемся, пока ждём подачи
            player.goes()
        elapsed = time.get_ticks() - countdown_start
        if elapsed >= 3000:
            countdown_active = False
        else:
            seconds_left = (3000 - elapsed + 999) // 1000   #округление вверх: 3, 2, 1
            timer_text = game_font.render(str(seconds_left), True, black_color)
            window.blit(timer_text, timer_text.get_rect(center=(width // 2, height // 2)))

    elif not game_over:
        for player in players:
            player.goes()
        ball.update(players)

        if ball.rect.right < 0:
            score_right += 1
            goal_scored = True
        elif ball.rect.left > width:
            score_left += 1
            goal_scored = True

        if goal_scored:
            goal_scored = False
            for player in players:
                player.starts()
            if score_right >= WIN_SCORE:
                game_over = True
                winner_text = 'Правый игрок победил!'
                color_tag = red_color
            elif score_left >= WIN_SCORE:
                game_over = True
                winner_text = 'Левый игрок победил!'
                color_tag = blue
            else:
                ball = Ball()
                countdown_active = True
                countdown_start = time.get_ticks()

    if game_over:
        text = game_font.render(winner_text + '  Пробел — заново', True, color_tag)
        window.blit(text, text.get_rect(center=(width // 2, height // 2)))

    for e in event.get():
        if e.type == QUIT:
            game = False

        if e.type == KEYDOWN and e.key == K_SPACE and game_over:
            restart_ready = True

    if game_over and restart_ready:
        game_over = False
        restart_ready = False
        for player in players:
            player.starts()
        winner_text = ''
        score_left = 0
        score_right = 0
        ball = Ball()
        mixer.music.rewind()
        mixer.music.play()

    clock.tick(FPS)
    display.flip()
quit()