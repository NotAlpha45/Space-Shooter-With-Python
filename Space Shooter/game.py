import os
import random
import pygame
from pygame import mixer

pygame.init()
# Initializing mixer for sound effects
mixer.init()
# Initializing the font of our game's score and such.
pygame.font.init()
# importing the icon
ICON = pygame.image.load(os.path.join("assets", "icon.jpg"))
# Making window and setting the icon
w = 750
h = 600
WINDOW = pygame.display.set_mode((w, h))
pygame.display.set_caption("Space Shooters")
pygame.display.set_icon(ICON)
# Loading the game assets
MAIN_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ship2.png")), (60, 60))
ENEMY1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy1.png")), (50, 50))
ENEMY2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy3.png")), (50, 50))
ENEMY3 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "enemy2.png")), (50, 50))
# To make sure our image is upto scale with the window resolution, we need to transform it accordingly.
# The first parameter of pygame.transform.scale() is the loaded image and the second one is the resolution
# tuple (width, height)
BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background2.gif")), (w, h))
LASER1 = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
LASER2 = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
LASER3 = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
LASER_Player = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))


# To make a generalized structure of a ship in the game, passing their x and y position
# and health value.
class Ship_maker:
    def __init__(self, x, y):
        # Setting up class attributes so that the ships can store their position and such.
        # Without using self variables, you can't use the given arguments like x and y in
        # other places.
        self.x = x
        self.y = y
        # Default health is 100 which will be decremented later on if necessary.
        self.health = 100
        # For now, the ship img and laser image is None. We will change it later.
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        # firing_delay so that we can't spam the laser.
        self.firing_delay = 0

    # Drawing the ships accordingly. window parameter is going to indicate on which window
    # we will draw on. We can cal this class method anywhere to draw the ship.
    def draw(self, window):
        # blit the image into the given window with the given coordinates.
        window.blit(self.ship_img, (self.x, self.y))

        for laser in self.lasers:
            laser.draw(window)

    # To move the laser and check for any collisions. delay determines the frame
    # delay between 2 shots. Higher the delay, the more fast the shot is.
    def move_laser(self, vel, Player_obj, delay):

        self.firing_delay_counter(delay)
        for laser in self.lasers:

            laser.move(vel)
            if laser.is_off_screen(h):
                self.lasers.remove(laser)
            elif laser.collision(Player_obj):
                exp_sound = mixer.Sound(os.path.join("assets", "exp2.wav"))
                exp_sound.play()
                Player_obj.health -= 10
                self.lasers.remove(laser)

    # Functions to get the width and height of the image to use later on
    def get_height(self):
        return self.ship_img.get_height()

    def get_width(self):
        return self.ship_img.get_width()

    def firing_delay_counter(self, delay):
        # If the firing delay is greater than the given delay, set it back to 0.
        # Otherwise, increment it if it is not 0.
        if self.firing_delay >= delay:
            self.firing_delay = 0
        elif self.firing_delay > 0:
            self.firing_delay += 1

    # This method is only applicable if the enemy ships want to shoot. The
    # Player ship will fire on keypress. Note that shoot_laser method
    # automatically fills up the player's laser count.
    def shoot_laser(self):
        if self.firing_delay == 0:
            new_laser = Laser_maker(self.x - 20, self.y - 10, self.laser_img)
            self.lasers.append(new_laser)
            # After each shot, the firing_delay will be set to 1. Then this
            # will pass through firing_delay_counter() and be incremented until
            # it has reached the delay period, to be set again to 0 and again shot.
            self.firing_delay = 1



# Class for making the laser and it's properties.
class Laser_maker:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.collision_mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    # To move the laser according to the given velocity.
    def move(self, velocity):
        self.y += velocity

    # To check if the laser is out of screen or not. We will get
    # True if it is off the screen.
    def is_off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    # A method for checking object's collision.
    def collision(self, obj):
        return collide(obj, self)


# The Player class will make the Player ship. And to do that,
# Player class will take the things of Ship_maker class and use it.
# Player class will take all the methods as the Ship_maker method.
class Player(Ship_maker):
    def __init__(self, x, y):
        # To keep track of the score.
        self.score = 0
        # To grab all the variables and methods in the Ship_maker class to use
        # it here. super() helps us to do so.
        super().__init__(x, y)
        self.ship_img = MAIN_SHIP
        self.laser_img = LASER_Player
        # A mask will help to determine pixel perfect collision according from the
        # surface of the ship image.
        self.collision_mask = pygame.mask.from_surface(self.ship_img)

    # The move_laser method in Player class is a little different. This will check if
    # the laser have hit the enemies in the enemy list. The enemies will instantly
    # vanish and score will be incremented by 1.
    def move_laser(self, vel, enemies, delay):
        self.firing_delay_counter(delay)
        # The laser list is automatically filled as Player class inherits from the
        # Ship_maker class.
        for laser in self.lasers:
            laser.move(vel)
            if laser.is_off_screen(h):
                self.lasers.remove(laser)
            else:
                for enemy in enemies:
                    if laser.collision(enemy):
                        exp_sound = mixer.Sound(os.path.join("assets", "exp2.wav"))
                        exp_sound.play()
                        enemies.remove(enemy)
                        self.score += 1
                        try:
                            self.lasers.remove(laser)
                        except:
                            pass

    # This method will return the score
    def score_val(self):
        return self.score

    # Making a health bar. A health bar is just two overlapping rectangle
    # one of which decreases in size as the health decreases.
    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10, abs(self.ship_img.get_width() * (self.health / 100)), 10))


# Create the class for enemy ship im the same way.
class enemy_ship(Ship_maker):
    # This dictionary holds the ship image and laser image according to the
    # color that we will assign.
    color_map = {"red": (ENEMY3, LASER3), "blue": (ENEMY1, LASER1), "green": (ENEMY2, LASER2)}

    def __init__(self, x, y, color):
        super().__init__(x, y)
        # To determine the ship image and laser image from the color_map.
        # Note that you will need to include self keyword to access the
        # constant dictionary declared in the class.
        self.ship_img, self.laser_img = self.color_map[color]
        # Create collision mask to detect collision.
        self.collision_mask = pygame.mask.from_surface(self.ship_img)

    # This function will determine the movement of the enemy by the given parameter
    # of ship.
    def move(self, speed):
        # The ship will move down.
        self.y += speed


# Create a collide function with mask. Mask works via determining the offset of the
# objects along with it's surfaces.
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    # If the collision mask of obj1 (created in it's class) is overlapping with the mask of obj 2 according to their offset.
    # If it is true, it will return the tuple of the collision or overlapping position (x,y).
    # Otherwise it will return None.
    return obj1.collision_mask.overlap(obj2.collision_mask, (offset_x, offset_y)) != None


# This will pause the game upon pressing esc and resume it on pressing enter.
def pause_game():
    # Making the pause menu items
    game_font = pygame.font.SysFont("consolas", 70)
    game_font2 = pygame.font.SysFont("consolas", 40)
    text = game_font.render("Paused", 1, (255, 255, 255))
    text2 = game_font2.render("Press Enter to resume", 1, (255, 255, 255))
    paused = True
    while paused:
        # When in the pause loop, show these
        WINDOW.blit(BACKGROUND, (0, 0))
        WINDOW.blit(text, (w // 2 - text.get_width() // 2, h // 2 - text.get_height() // 2))
        WINDOW.blit(text2, (w // 2 - text2.get_width() // 2, h // 2 - text.get_height() // 2 + 70))
        pygame.display.update()
        # Detecting press on the quit button of the window.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # Detecting keypress for enter. If enter is pressed, it will return
        # to the game loop.
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_RETURN]:
            paused = False


def game_main():
    # Adding a background music
    mixer.music.load(os.path.join("assets", "bgsound.wav"))
    mixer.music.play(-1)
    # Create the ship object with the help of Ship_maker lass. Then we can use
    # all the methods in that class on our ship.

    Player_ship = Player(w // 2 - MAIN_SHIP.get_width() // 2, 500)
    lost = False
    lost_timer = 0
    level = 0
    lives = 5

    FPS = 60
    GAME_IS_RUNNING = True
    # To keep track of the enemies on the screen.
    enemies = []
    wave_length = 5
    enemy_speed = 1
    # Create the font type of the game with font name and size
    game_font = pygame.font.SysFont("consolas", 20)
    lost_font = pygame.font.SysFont("comicsans", 50)
    clock = pygame.time.Clock()  # To keep track of time

    # Function to draw the assets. Whenever game_main() runs
    # This will run and can use the parameters of game_main()
    def draw_on_window():
        # To show level and lives of the game, we need to render those according
        # to the font and then blit them in the screen. render() takes 3 arguments.
        # The first one is the text, the second is antialias amount and the last is the
        # color value that has to be in the RGB coordinate value.
        level_label = game_font.render(f'level: {level}', 1, (255, 255, 0))
        lives_label = game_font.render(f'lives: {lives}', 1, (255, 255, 0))
        lost_label = lost_font.render(f'You lost :(', 1, (255, 255, 255))
        score_label = game_font.render(f'Score: {score}', 1, (255, 255, 0))
        health_label = game_font.render(f'Health: {Player_health}', 1, (255, 255, 0))

        # blit() method puts the image on the window that we made.
        # We first loaded the background on the (0,0) coordinate of the window
        WINDOW.blit(BACKGROUND, (0, 0))
        WINDOW.blit(level_label, (10, 10))
        WINDOW.blit(lives_label, (10, 30))
        # get_width() returns the width of the layer (over here, the layer is a text label)
        WINDOW.blit(health_label, (w - health_label.get_width() - 10, 10))
        WINDOW.blit(score_label, (w - score_label.get_width() - 10, 30))
        for i in enemies:
            # you can use draw() on enemy class as well as it inherits from the
            # Ship_maker class.
            i.draw(WINDOW)
        # Drawing the Player ship with the help of the draw() method that we defined
        # in the Ship_maker class. Along with it drawing the health bar.
        Player_ship.draw(WINDOW)
        Player_ship.health_bar(WINDOW)
        # If Player is lost, show the lost label.
        if lost:
            WINDOW.blit(lost_label, (300, 300))
        # Update the window each time with the drawings.
        pygame.display.update()

    while GAME_IS_RUNNING:

        # Tick the clock according to the set refresh rate or FPS
        # Makes sure that frame rate is consistent throughout devices
        clock.tick(FPS)

        # Counting the Player health via extracting the variable from the class
        # With each cycle of the loop, the health will be updated accordingly.
        # Since it is updated upon calling the class, you'll need to include it
        # in the loop, before the draw_on_window() function.
        Player_health = Player_ship.health
        # Counting the score. Make sure that this variable is inside the game loop
        # and is before the draw_on_window() method. Otherwise, you won't get consistent
        # score count or have error showing the score.
        score = Player_ship.score_val()
        # Call the draw_on_window function to draw the things on the window when the game
        # is running. This should be second to the clock tick in the game loop to make sure
        # everything is running accordingly. Otherwise, there may be delay in showing the
        # game over or lost message.
        draw_on_window()
        # To check if the Player is lost or not. Make sure to add this right after draw_on_window(),
        # so that as soon as game over is detected, it doesn't do any of the spawning and such.
        # Then lost_timer will be incremented by 1 for each passing frame.
        if lives <= 0 or Player_health <= 0:
            lost = True
            lost_timer += 1

        # To show the lost message in the screen for 3 seconds.
        # You need to multiply 3 with FPS as they count moments
        # according to the frames.
        if lost:
            mixer.music.load(os.path.join("assets", "game over.wav"))
            mixer.music.play()
            if lost_timer > FPS * 3:

                GAME_IS_RUNNING = False

            else:
                continue

        # To check every event a.k.a keypress from the user. Note that this procedure
        # doesn't detect multiple keypress at once.
        for event in pygame.event.get():
            # If the user quits the game by pressing the cross. The
            # type of the event then must be pressing quit.
            if event.type == pygame.QUIT:
                GAME_IS_RUNNING = False
                quit()
        # Detecting keypress by the user. This will return a dictionary of all the
        # keys that was pressed at once at the current frame.
        keypress = pygame.key.get_pressed()
        # If a keypress is detected, change the coordinates of the Player_ship object
        # make sure that the ship doesn't go out of bounds.
        if keypress[pygame.K_LEFT] and Player_ship.x >= 1:
            Player_ship.x -= 3
        if keypress[pygame.K_RIGHT] and Player_ship.x <= w - 65:
            Player_ship.x += 3
        if keypress[pygame.K_UP] and Player_ship.y >= 1:
            Player_ship.y -= 3
        if keypress[pygame.K_DOWN] and Player_ship.y <= h - 50:
            Player_ship.y += 3
        if keypress[pygame.K_SPACE]:
            # Playing the laser sound effect. Since this is only a sound effect,
            # we will use the Sound() function to make a effect variable and play it
            laser_sound = mixer.Sound(os.path.join("assets", "laser.wav"))
            laser_sound.play()
            Player_ship.shoot_laser()
        if keypress[pygame.K_ESCAPE]:
            pause_game()

        # If there are no more enemies, increase the enemy wave length.
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                # Selecting a random spawning spot in such a way that the enemies
                # span outside of the screen. So the y coordinate is in negative
                spawn_x = random.randrange(100, w - 100)
                spawn_y = random.randrange(-1500, -100)
                color = random.choice(["red", "green", "blue"])
                enemy = enemy_ship(spawn_x, spawn_y, color)
                enemies.append(enemy)

        # Move the enemies along the screen.
        enemy_track = enemies[:]
        for j in enemy_track:

            # To bring a random shooting pattern. We want to shoot on every 2
            # seconds. So, our range would be 0-60*2 as 60 is our refresh rate.
            if random.randrange(0, 120) == 1:
                #The enemies doesn't have a trigger to shoot. So this process is
                # handled by shoot_laser() which is not needed for the player.
                j.shoot_laser()

            j.move(enemy_speed)
            # Move lasers towards the Player.
            j.move_laser(4, Player_ship, 60)
            # If the enemy is beyond the screen, delete that enemy and remove
            # a life.
            if j.get_height() + j.y > h:
                lives -= 1
                enemies.remove(j)
            # If the Player collides with an enemy ship, he loses health and the enemy
            # is destroyed.
            if collide(j, Player_ship):
                # Adding a collision sound effect.
                exp_sound = mixer.Sound(os.path.join("assets", "exp2.wav"))
                exp_sound.play()
                # You need to decrement the health directly by extracting
                # class variable.
                Player_ship.health -= 40
                # Making sure a negative number of health is not displayed
                if Player_ship.health < 0:
                    Player_ship.health = 0
                enemies.remove(j)
        # Negative velocity means that the laser goes up.
        Player_ship.move_laser(-8, enemies, 20)


# Making a main menu. This main menu function will be called. Then if enter is pressed,
# then game_main() will be run.
def main_menu():
    game_font = pygame.font.SysFont("consolas", 70)
    text = game_font.render("Press Enter To Play", 1, (255, 255, 255))
    run = True
    while run:
        WINDOW.blit(BACKGROUND, (0, 0))
        WINDOW.blit(text, (w // 2 - text.get_width() // 2, h // 2 - text.get_height() // 2))
        pygame.display.update()
        # Detecting press on the quit button of the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_RETURN]:
            game_main()
    # If the loop is not running, it means that the game is quit.
    pygame.quit()


main_menu()
