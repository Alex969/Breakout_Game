import pygame
from pygame.locals import *  # Ease of writing, kind of like using namespace std in C++

pygame.init()  # Initializes pygame so that we can run our code

screen_width = 600
screen_height = 600

# Screen and Game Icon
screen = pygame.display.set_mode((screen_width, screen_height))  # Creates screen
pygame.display.set_caption(
    "★Alex's Breakout Game★")  # pygame function which sets a title for the game window and displays it
# loads and displays the game icon
icon = pygame.image.load('AlexGameLogo2.png')  # pygame function that loads an image
pygame.display.set_icon(icon)  # pygame function which displays an image as a game's icon

# Start Button icon
# load and scales the start button image to best fit the game window
start_button = pygame.image.load('StartButton.png')
start_button = pygame.transform.scale(start_button, (350, 270))  # pygame function which scales a loaded image
# transforms the start button img into a rectangle so that it's easier to compute collision with it and the user's mouse
start_button_rect = start_button.get_rect()  # pygame function that gets the
                                             # rectangular area of the surface covered by the image
start_button_rect.x = (screen_width // 2 - 175)
start_button_rect.y = (screen_height // 2)

# Text font
font = pygame.font.Font("Pokemon X and Y.ttf", 18)  # loads downloaded font and sets its size
font_game_over = pygame.font.Font("Pokemon X and Y.ttf", 40)

# Ball colours
ball_col = (227, 246, 55)
ball_outline = (79, 70, 206)

# Background colour
bg_color = (228, 158, 211)

# Brick colours
bricks_color = (158, 228, 174)

# Paddle colour
paddle_col = (182, 55, 246)
paddle_outline = (79, 70, 206)

# Text colour
text_col = (0, 0, 0)
game_over_col = (236, 3, 3)

# Global variables
rows = 8
cols = 6
# how many images(frames) are drawn per second by the program, in this case 60 which is quite a common fps
frameRate = 60
Time = pygame.time.Clock()  # ensures our game doesn't run too fast
game_live = False  # initiates the game as in a not running state
game_over = 0  # if game_over = 0, the player hasn't won or lost yet so the game can run

# Score variables
score_value = 0
# coordinates of the Score text on the window
score_x = 530
score_y = 0

# Lives variable and icons
# how many lives the player starts with
hearts = 5
# coordinates of lives count on the window
hearts_x = 0
hearts_y = 0
# loads and displays the heart icon
hearts_logo = pygame.image.load('Hearts_Icons.png')
hearts_logo = pygame.transform.scale(hearts_logo, (30, 25))
hearts_logo_rect = hearts_logo.get_rect()
hearts_logo_rect_x = 0
hearts_logo_rect_y = 0


# Text output function
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True,
                      text_col)  # converts text and its colour to an img so that pygame can draw it on screen
    screen.blit(img, (x, y))  # pygame method which draws an image on the screen


# Bricks class
class Bricks:
    def __init__(self):
        self.width = screen_width // rows # use of // to make sure we work with integers for better code efficiency
        self.height = 35

    def create_bricks(self):
        self.brick = []  # contains every brick
        # define an  empty list for each individual brick
        single_brick = []
        for row in range(rows): # iterate through every row
            # resets the brick row list
            brick_row = []
            # iterates through each column in that row
            for col in range(cols):
                # generates x and y pos for each brick and creates a rectangle from that
                brick_x = row * self.width  # each time it creates a brick, creates new rectangle after the width of it
                brick_y = col * self.height + 20 # same but for height attribute, + 20 to leave space for lives & score
                # assigns generated values to the brick rectangle as well as width and height
                rect = pygame.Rect(brick_x, brick_y, self.width, self.height)

                # list to store rect and colour
                single_brick = [rect]

                # append (add values to the end of a list) that single brick to the brick row list
                brick_row.append(single_brick)

            # append the brick row to full list of bricks
            self.brick.append(brick_row)

    def draw_bricks(self):
        for row in self.brick:  # iterates through each row of bricks in that list
            for brick in row:  # within that list, move through each brick
                # pygame function that draws a rect to the screen, brick[0] refers to rect in single_brick
                pygame.draw.rect(screen, bricks_color, brick[0])
                # draws another brick wall behind it using bg color and line thickness to separate the clumped first
                # set of bricks
                pygame.draw.rect(screen, bg_color, brick[0], 6)



# Paddle Class
class Paddle:
    def __init__(self):
        self.reset()

    def moving(self):
        # resets movement direction
        self.direction = 0
        key = pygame.key.get_pressed()  # gets what key has been pressed by user and holds on to it
        if key[pygame.K_LEFT] and self.rect.left > 0:  # as long as left key is pressed and paddle is not off screen

            # gives the x coordinate a negative value relative to the speed of the paddle as well as changes its
            # direction to a negative value since it's going "down" the x axis of the window's coordinates graph
            # which translates to the paddle going left on the screen
            self.rect.x -= self.speed
            self.direction = -1

        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            # same but the inverse, so that the paddle goes to the right on the screen in that instance
            self.rect.x += self.speed
            self.direction = 1

    def draw_paddle(self):
        # draws the paddle to the screen according to self.rect's coordinates, which are dependant on what arrow key
        # the user is pressing between the left and right one
        pygame.draw.rect(screen, paddle_col, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 2)

    # use of a reset function that stores the initial data of the paddle, we call reset when we reset the game
    def reset(self):
        # size and position
        self.height = 20
        self.width = int(screen_width / cols) # use of int for similar reasons than use of " // " operator
        # since x is top left of the paddle, we have to take away the value of its own half to have it in middle
        self.x = int(screen_width / 2) - (self.width / 2)
        self.y = screen_height - (self.height * 2)
        # speed at which the paddle moves + creates rect and direction of movement tracker
        self.speed = 8
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0


# ball class
class Ball:
    def __init__(self, x, y):
        self.hearts_count = 5
        self.reset(x, y)

    def moving(self):
        # pixel threshold for collisions in between the ball and the bricks, paddle and walls
        threshold = 5

        # Wall of brick as in totallity of the bricks : is destroyed
        brickWall_destroyed = 1
        row_count = 0
        for row in Bricks.brick:  # iterating through every single row in the list containing all of our bricks
            item_count = 0
            for item in row:  # iterating through every single brick in each row
                # check for collision with every brick
                if self.rect.colliderect(item[0]):
                    # check if colliding with the top of the brick, if the bottom of the ball crosses the top of the
                    # brick rect and if the y speed is positive (since the ball is supposedly going down in that case)
                    if abs(self.rect.bottom - item[0].top) < threshold and self.speed_y > 0:
                        self.speed_y *= -1

                    # check if colliding with the bottom of the brick, if the top of the ball crosses the bottom of the
                    # brick rect and if the y speed is negative (since the ball is supposedly going up in that case)
                    if abs(self.rect.top - item[0].bottom) < threshold and self.speed_y < 0:
                        self.speed_y *= -1

                    # check if colliding with the left side of the brick, if the right side of the ball crosses the
                    # left side of the brick rect and if the x speed is positive
                    # (since the ball is supposedly going to the right in that case)
                    if abs(self.rect.left - item[0].right) < threshold and self.speed_y > 0:
                        self.speed_x *= -1

                    # check if colliding with the right side of the brick, if the left side of the ball crosses the
                    # right side of the brick rect and if the x speed is negative
                    # (since the ball is supposedly going to the left in that case)
                    if abs(self.rect.right - item[0].left) < threshold and self.speed_x < 0:
                        self.speed_x *= -1

                    # destroys a block when hit by the ball
                    else:
                        Bricks.brick[row_count][item_count][0] = (0, 0, 0, 0)
                        self.score_count += 1

                # check if all the bricks have been destroyed
                if Bricks.brick[row_count][item_count][0] != (0, 0, 0, 0):
                    brickWall_destroyed = 0

                item_count += 1
            row_count += 1

        if brickWall_destroyed == 1:
            self.game_over = 1 # means you have won the game

        # collision with paddle
        if self.rect.colliderect(Paddle):  # since both the ball & paddle are rect we can use colliderect
            if abs(self.rect.bottom - Paddle.rect.top) < threshold:
                self.speed_y *= -1
                self.speed_x += Paddle.direction
                # limiting the maximum speed the ball can go up to to avoid the ball getting stuck between frames
                if self.speed_x > self.speed_max:
                    self.speed_x = self.speed_max
                elif self.speed_x < 0 and self.speed_x < - self.speed_max:
                    self.speed_x = - self.speed_max

            else:  # if colliding from the sides of the paddle
                self.speed_x *= -1

        # when ball hit the walls, inverse its speed to make it change direction
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *= -1
        if self.rect.top < 0:
            self.speed_y *= -1
        # when ball hits the bottom, it falls and player loses a life and eventually gets a game over
        if self.rect.bottom > screen_height:
            self.game_over = -1 # loses a single game
            self.hearts_count -= 1
            if self.hearts_count == 0:
                self.game_over = -2 # complete game over

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over, self.score_count, self.hearts_count

    def draw_ball(self):
        pygame.draw.circle(screen, ball_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, ball_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad),
                           self.ball_rad, 2)

    def reset(self, x, y):
        self.ball_rad = 10
        self.x = x - self.ball_rad  # centralizes the ball like we did for the paddle
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = - 4  # negative so that the ball goes up first
        self.speed_max = 5
        self.game_over = 0
        self.score_count = 0
        if (self.hearts_count == 0) or (self.game_over == 1):
            self.hearts_count = 5


# create bricks
Bricks = Bricks()
Bricks.create_bricks()

# create paddle
Paddle = Paddle()

# create ball
Ball = Ball(Paddle.x + (Paddle.width // 2), Paddle.y - Paddle.height)

# Game loop that makes sure the game is running and exited only by clicking the exit button of the window
run = True
while run:

    Time.tick(frameRate)
    screen.fill(bg_color)  # first so that it doesn't fill on top of things

    # draw game objects
    Bricks.draw_bricks()
    Paddle.draw_paddle()
    Ball.draw_ball()

    if game_live:
        Paddle.moving()
        result = Ball.moving()
        game_over = result[0]
        score_value = result[1]
        hearts = result[2]
        draw_text("          : " + str(hearts), font, text_col, hearts_x, hearts_y)
        screen.blit(hearts_logo, hearts_logo_rect)
        draw_text("Score: " + str(score_value), font, text_col, score_x, score_y)
        if game_over != 0:
            game_live = False

    # Player instructions
    if not game_live:

        if game_over == 0:
            draw_text('(Press left and right key to control paddle)', font, text_col, 155, screen_height // 2 - 20 )
            draw_text('Click the start button to start your game', font, text_col, 162, screen_height // 2 - 50)
            screen.blit(start_button, start_button_rect)
        elif game_over == 1:
            draw_text("         : " + str(hearts), font, text_col, hearts_x, hearts_y)
            screen.blit(hearts_logo, hearts_logo_rect)
            draw_text("Score: " + str(score_value), font, text_col, score_x, score_y)
            draw_text("You won !   You're amazing !", font, text_col, 200, screen_height // 2)
            draw_text('Fancy another one ? Click anywhere to start a new game', font, text_col, 120,
                      screen_height // 2 + 40)
        elif game_over == -1:
            draw_text("          : " + str(hearts), font, text_col, hearts_x, hearts_y)
            screen.blit(hearts_logo, hearts_logo_rect)
            draw_text("Score: " + str(score_value), font, text_col, score_x, score_y)
            draw_text('You Lost...', font, text_col, 250, screen_height // 2)
            draw_text('Click anywhere to try again', font, text_col, 200, screen_height // 2 + 40)
        elif game_over == -2:
            draw_text("         : " + str(hearts), font, text_col, hearts_x, hearts_y)
            screen.blit(hearts_logo, hearts_logo_rect)
            draw_text("Score: " + str(score_value), font, text_col, score_x, score_y)
            draw_text('GAME OVER ', font_game_over, game_over_col, 220, screen_height // 2 - 30)
            draw_text('Click anywhere to start a new game', font, text_col, 180, screen_height // 2 + 40)

    for event in pygame.event.get():  # Look for all the pygame events
        if event.type == pygame.QUIT:  # if you quit the game by clicking the X button
            run = False
        # if mouse is pressed and the game isn't live yet
        if event.type == pygame.MOUSEBUTTONDOWN and game_live == False:
            # if mouse and start button rect collide at mouse coordinates (event being mousebuttondown)
            if start_button_rect.collidepoint(event.pos):
                game_live = True
                Ball.reset(Paddle.x + (Paddle.width // 2), Paddle.y - Paddle.height)
                Paddle.reset()
                # no reset function needed since the first line of code in create_bricks
                # creates an empty list that is then filled
                Bricks.create_bricks()

    pygame.display.update()

pygame.quit()
