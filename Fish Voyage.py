import pygame
from pygame.locals import *
import random

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("sound1.mp3")
pygame.mixer.music.play()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 630
x = 0
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Fish Voyage')

# define font of score
font = pygame.font.SysFont('Bauhaus 93', 100)

# define colours of fonts
white = (0, 0, 0)

# define game variables
ground_scroll = 0
scroll_speed = 5
swimming = False
game_over = False
shark_gap = 150
shark_frequency = 1500  # milliseconds
last_shark = pygame.time.get_ticks() - shark_frequency
score = 0
pass_shark = False

# load images
bg = pygame.image.load('img/bg.png')  # background image
ground_img = pygame.image.load('img/ground.png')  # ground image
button_img = pygame.image.load('img/restart.png')  # restart button image


# function for outputting text on the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    shark_group.empty()
    voyaje.rect.x = 100
    voyaje.rect.y = int(screen_height / 2)
    score = 0
    return score


class Fish(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/fish{num}.png")
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if swimming == True:
            # apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            flap_cooldown = 10
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate the fish
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # point the fish at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)


class Shark(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/shark.png")
        self.rect = self.image.get_rect()
        # position variable determines if the shark is coming from the bottom or top
        # position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(shark_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(shark_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


shark_group = pygame.sprite.Group()
fish_group = pygame.sprite.Group()

voyaje = Fish(100, int(screen_height / 2))

fish_group.add(voyaje)

# create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:

    clock.tick(fps)

    # draw background
    screen.blit(bg, (0, 0))

    # draw and scroll the ground
    screen.blit(ground_img, (ground_scroll, 500))

    # draw sharks
    shark_group.draw(screen)

    # draw fish
    fish_group.draw(screen)

    fish_group.update()

    # check the score
    if len(shark_group) > 0:
        if fish_group.sprites()[0].rect.left > shark_group.sprites()[0].rect.left \
                and fish_group.sprites()[0].rect.right < shark_group.sprites()[0].rect.right \
                and pass_shark == False:
            pass_shark = True
        if pass_shark == True:
            if fish_group.sprites()[0].rect.left > shark_group.sprites()[0].rect.right:
                score += 1
                pass_shark = False
    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # look for collision
    if pygame.sprite.groupcollide(fish_group, shark_group, False, False) or voyaje.rect.top < 0:
        game_over = True
    # once the fish has hit the ground it's game over and no longer swimming
    if voyaje.rect.bottom >= 630:
        game_over = True
        swimming = False

    if swimming == True and game_over == False:
        # generate new sharks
        time_now = pygame.time.get_ticks()
        if time_now - last_shark > shark_frequency:
            shark_height = random.randint(-100, 100)
            btm_shark = Shark(screen_width, int(screen_height / 2) + shark_height, -1)
            top_shark = Shark(screen_width, int(screen_height / 2) + shark_height, 1)
            shark_group.add(btm_shark)
            shark_group.add(top_shark)
            last_shark = time_now

        shark_group.update()

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 863:
            ground_scroll = 0

    # check for game over and reset
    if game_over == True:
        if button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and swimming == False and game_over == False:
            swimming = True

    pygame.display.update()

pygame.quit()
