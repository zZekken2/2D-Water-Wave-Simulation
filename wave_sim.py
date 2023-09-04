import pygame
from pygame.locals import *
from threading import Thread
import time
from OpenGL.GL import *
from OpenGL.GLU import *

# ----- CONSTANTS -----
WIDTH = 900
HEIGHT = 600
FPS = 60

target_height = HEIGHT // 2  # Rest height of the water

water_origin = 0
water_end = WIDTH

# ----- Main class -----
class Water:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL) # this flags are required to use OpenGL properly
        pygame.display.set_caption("Water Waves Simulation")

        self.time = pygame.time.Clock()

        self.initial_speed = 300

        self.springs = []

        self.spring_num = abs((water_origin - water_end) // 3)  # Calculates the number of springs
        self.spring_width = (water_origin + water_end) // self.spring_num  # Calculates the width the springs have to be

        self.spring_list()

        self.running = True
        self.run_simulation()

    def run_simulation(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    pygame.quit()
                    exit()

                if event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.start_index = pos[0] // self.spring_width
                    self.get_values()
                    self.add_values()
                    self.start_waves()


            glClearColor(0.173, 0.153, 0.153, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            gluOrtho2D(0, WIDTH, HEIGHT, 0)
            glColor3f(0, 0.42, 1)

            for spring in self.springs:
                spring.draw_springs()

            self.time.tick(FPS)
            pygame.display.flip()

    def spring_list(self):
        # To create the wave iteration, a list is required that is
        # continually updated to encompass the values of the new wave.

        new_springs = [] # Whenever the method is called the list is reset
        for spring in range(water_origin, water_end, self.spring_width):
            new_springs.append(Springs(spring, target_height, self.spring_width))
        
        self.springs = list(new_springs)

    # ----- Stores the values of the current wave -----
    def get_values(self):
        self.heights = []
        self.speeds = []
        for i in range(len(self.springs)):
            self.heights.append(self.springs[i].height - target_height)
            self.speeds.append(self.springs[i].speed)
    # -----------------------------------------------------------

    # ----- Adds the new values ​​so that the list of springs is correctly updated -----
    def add_heights(self):
        for i, height in enumerate(self.heights):
            self.springs[i].height += height

    def add_speeds(self):
        for i, speed in enumerate(self.speeds):
            self.springs[i].speed += speed

    def add_values(self):
        self.spring_list()
        self.add_heights()
        self.add_speeds()
    # ----------------------------------------------------------------------------------

    def start_waves(self):
        self.springs[self.start_index].speed = self.initial_speed
        self.updates = Update_Control(self.springs)
        self.updates.start()


# ----- Handles the spring/wave calculations -----
class Springs:
    def __init__(self, x, target_height, spring_width):
        self.x = x
        self.bottom_y = HEIGHT # just for organization purposes
        self.wave_height = 0
        self.height = target_height

        self.speed = 0
        self.spring_width = spring_width

    def hooke_law(self, target_height, tension, dampening):
        self.wave_height = self.height - target_height
        self.speed += - tension * self.wave_height - self.speed * dampening
        self.height += self.speed

    def draw_springs(self):
        glBegin(GL_QUAD_STRIP)
        glVertex2d(self.x, self.height) # Top left
        glVertex2d(self.x + self.spring_width, self.height) # Top right
        glVertex2d(self.x, self.bottom_y) # Bottom left
        glVertex2d(self.x + self.spring_width, self.bottom_y) # Bottom right
        glEnd()


# ----- Handles all the updates -----
class Update_Control(Thread):  # Update_Control inherits the functionalities of Thread
    def __init__(self, springs):
        Thread.__init__(self)  # Iniciates the inherited properties
        self.springs = springs

        self.springs_tension = 0.025
        self.springs_dampening = 0.020
        self.spread_speed = 0.25

        self.updating = True

    def spring_update(self):
        for i in range(len(self.springs)):
            self.springs[i].hooke_law(target_height, self.springs_tension, self.springs_dampening)

    # ----- Handles the left and right neighbors of the activated spring -----
    def neighbor_list(self):
        self.lDeltas = list(self.springs)
        self.rDeltas = list(self.springs)

    def neighbor_update(self):
        for _ in range(5):
            # -----UPDATES-VELOCITY-----
            for i in range(len(self.springs)):
                if i > 0:
                    self.lDeltas[i] = self.spread_speed * (self.springs[i].height - self.springs[i - 1].height)
                    self.springs[i - 1].speed += self.lDeltas[i]

                if i < len(self.springs) - 1:
                    self.rDeltas[i] = self.spread_speed * (self.springs[i].height - self.springs[i + 1].height)
                    self.springs[i + 1].speed += self.rDeltas[i]

            # -----UPDATES-HEIGHT-----
            for i in range(len(self.springs)):
                if i > 0:
                    self.springs[i - 1].height += self.lDeltas[i]
                if i < len(self.springs) - 1:
                    self.springs[i + 1].height += self.rDeltas[i]
    # ------------------------------------------------------------------------

    def reset_water(self, count):
            for i in range(len(self.springs)):
                if not int(self.springs[i].speed) and not int(self.springs[i].wave_height):
                    count += 1
            if count == len(self.springs):
                for i in range(len(self.springs)):
                    if self.springs[i].height >= target_height + 1 or self.springs[i].height <= target_height + 1:
                        self.springs[i].speed = 0
                        self.springs[i].height = target_height
                        self.springs[i].wave_height = 0

                        if i == len(self.springs)-1:
                            self.updating = False

    def run(self):  # run() is one of the property methods inherited by Thread
        while self.updating:
            self.spring_update()
            self.neighbor_list()
            self.neighbor_update()

            count = 0
            self.reset_water(count)


            time.sleep(0.01)


if __name__ == "__main__":
    Water()
