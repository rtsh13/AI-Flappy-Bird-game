import os
import neat
import pygame
import os
import random
pygame.font.init()

# Set the width and height of the window. It will remain constant
WIN_WIDTH = 500
WIN_HEIGHT = 700
GEN = 0
# Images of the Birds are stored in the list BIRD_IMGS
# Images of the Pipes are stored in the list PIPE_IMG
# Images of the Base or the Floor stored in the list BASE_IMG
# Images of the Background stored in the list BG_IMG
# scale2x scales the images twice the size

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird" + str(x) + ".png"))) for x in range(1, 4)]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Set the font and the size of the text
STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Bird Class
class Bird:
    """
	Bird class representing the flappy bird
	"""
    MAX_ROTATION = 25 # Angle of the maximum rotation the bird can sustain
    IMGS = BIRD_IMGS
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
		Initialize the object
		:param x: starting x pos (int)
		:param y: starting y pos (int)
		:return: None
		"""
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
		make the bird jump
		:return: None
		"""
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
		make the bird move
		:return: None
		"""
        self.tick_count += 1
        # for downward acceleration
        displacement = self.vel * (self.tick_count) + 0.5 * (3) * (self.tick_count) ** 2  # calculate displacement
        # terminal velocity
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement
        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
		draw the bird
		:param win: pygame window or surface
		:return: None
		"""
        self.img_count += 1
        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        # so when bird is nose diving and it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        # tilt the bird
        rotate_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotate_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotate_image, new_rect.topleft)

    # get_mask function is used to get the mask of the image to avoid collisions
    def get_mask(self):
        """
		gets the mask for the current image of the bird
		:return: None
		"""
        return pygame.mask.from_surface(self.img)

# Pipe Class
class Pipe:
    GAP = 200 # Gaps between the Pipes
    VEL = 5 # Velocity of Pipes, because Pipes will be moving

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # The image is flipped via function because we have just upright picture
        self.PIPE_BOTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    # Function is used to set the height of the pipes generated
    def set_height(self):
        self.height = random.randrange(50, 400)  # Setting the height of the Pipes
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    # Function used for the pipe to move
    def move(self):
        self.x -= self.VEL

    # Draw function displays the pipes in the pygame window
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top)) # Displays the Top Pipe
        win.blit(self.PIPE_TOP, (self.x, self.bottom)) # Displays the Bottom Pipe

    """
    This Function checks for the collision between the bird and the pipe
    Mask, an inbuilt function creates a list of pixels for the image and 
    checks whether the masks of each image collide or not and returns a value
    """
    def collide(self, bird):
        bird_mask = bird.get_mask() # Get the mask of the Bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # Get the mask of the Top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # Get the mask of Bottom Pipe
        top_offset = (self.x - bird.x, self.top - round(bird.y))  # Get the offset of the Top Pipe
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # Get the offset of the Bottom Pipe
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) # Checks for the overlap between the Bottom pipe and Bird
        t_point = bird_mask.overlap(top_mask, top_offset) # Checks for the overlap between the Top pipe and Bird
        if t_point or b_point:
            return True # True indicates the bird is colliding
        return False


# Base Class
class Base:
    VEL = 5 # Velocity of the base
    WIDTH = BASE_IMG.get_width() # Gets the width of the base
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    """ 
    The move function generates the copy of the base image and multiplies the image infinitely 
    """
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

   # Draws the base in pygame window
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

# Setting up the pygame window
def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))  # Displays the Background

    for pipe in pipes:
        pipe.draw(win)

    # Score is displayed on the top right corner and the adjustment of the ever increasing score is taken care of
    text = STAT_FONT.render("Score:" + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen:" + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()  # displays the game and refreshes it


def main(genomes, config):
    """
    Start by creating a list holding genome, the neural network associated
    with it and the bird object that uses the network to play
    """
    birds = [] # List to take care of multiple birds
    nets = []
    ge = []
    global GEN
    GEN+=1
    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(130,250)) #230,350
        g.fitness = 0
        ge.append(g)

    base = Base(630)
    pipes = [Pipe(500)]  # x position
    score = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds)>0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run=False
            break

        for x,bird in enumerate(birds):
            bird.move()
            ge[x].fitness +=0.1 # give each bird a fitness of 0.1 for staying alive for every frame
            output = nets[x].activate((bird.y,abs(bird.y - pipes[pipe_ind].height),abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness=-1 # reduces the specific bird's fitness level who hit the pipe
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge: #Add 10 to the fitnes score because the bird crossed the pipe
                g.fitness +=10 #Default 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score , GEN)

# reads the config of the near functions to be used through the parameter sent by gaining access to the directory
def run(config_path):

    # Set out configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Set our population
    p = neat.Population(config)

    #Reading out statistics
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Set the fitness function that we're going to run for 50 generations
    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # gives us the directory where we are currently located in
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
