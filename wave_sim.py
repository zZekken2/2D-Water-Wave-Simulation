import pygame
from pygame.locals import *
from threading import Thread
import time

# -----CONSTANTS-----
WIDTH = 600
HEIGHT = 600
FPS = 60
WATER_COLOR = (0, 106, 255)
SCREEN_COLOR = (32, 32, 32)


# Main class
class Water:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Water Waves Simulation")

        self.time = pygame.time.Clock()

        self.target_height = HEIGHT // 2

        self.initial_speed = 200  # NOTA: Passar a ser calculada em relação à massa e altura de lançamento do objeto

        self.x_origin = 0
        self.x_end = WIDTH

        self.springs = []

        self.spring_num = abs((self.x_origin - self.x_end) // 2)  # Calculates the number of springs
        self.spring_width = (self.x_origin + self.x_end) // self.spring_num  # Calculates the width the springs have to be

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
                    pos = pygame.mouse.get_pos()  # NOTA: em vez de utilizar só a posição do rato utilizar um objeto em queda
                    self.start_index = pos[0] // self.spring_width
                    self.add_heights()
                    self.start_waves()

            self.get_heights()
            self.draw_level()

            for spring in self.springs:
                spring.draw_springs(self.screen)

            self.time.tick(FPS)
            pygame.display.flip()

    def spring_list(self):
        new_springs = []
        for x in range(self.x_origin, self.x_end, self.spring_width):
            new_springs.append(Springs(x, self.target_height, self.spring_width))
        
        self.springs = list(new_springs)

    def get_heights(self):
        self.heights = [] # Everytime the method is called the list is reset
        for i in range(len(self.springs)):
            self.heights.append(self.springs[i].height - self.target_height)

    def add_heights(self):
        self.spring_list()
        for i, height in enumerate(self.heights):
            self.springs[i].height += height

    def start_waves(self):
        self.springs[self.start_index].speed = self.initial_speed
        self.updates = UpdateControl(self.springs)
        self.updates.start()

    def draw_level(self):
        self.screen.fill(SCREEN_COLOR)


# Handles the springs calculations
class Springs:
    def __init__(self, x, target_height, spring_width):
        self.x = x
        self.bottom_y = HEIGHT
        self.wave_height = 0
        self.height = target_height

        self.speed = 0
        self.spring_width = spring_width

    def hooke_law(self, target_height, tension, dampening):
        self.wave_height = self.height - target_height
        self.speed += - tension * self.wave_height - self.speed * dampening  # NOTA: diferenciar acelaração e velocidade e calcular a velocidade
        self.height += self.speed  # NOTA: aqui é aceleração

    def draw_springs(self, screen):
        pygame.draw.line(screen, WATER_COLOR, (self.x, self.height), (self.x, self.bottom_y), self.spring_width)


# Handles all the updates
class UpdateControl(Thread):  # Update_Control inherits the functionalities of Thread
    def __init__(self, springs):
        Thread.__init__(self)  # Iniciates the inherited properties
        self.springs = springs

        self.target_height = HEIGHT // 2

        self.springs_tension = 0.025
        self.springs_dampening = 0.020
        self.spread_speed = 0.25

        self.updating = True

    def spring_update(self):
        for i in range(len(self.springs)):
            self.springs[i].hooke_law(self.target_height, self.springs_tension, self.springs_dampening)

    def neighbor_list(self):
        self.lDeltas = list(self.springs)  # Creates the left neighbors of the activated spring
        self.rDeltas = list(self.springs)  # Creates the right neighbors

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

    def stop(self):
        while self.updating:
            for i in range(len(self.springs)):
                self.springs[i].speed = 0
                self.springs[i].height = self.target_height
                self.springs[i].wave_height = 0
                time.sleep(0.01)

                if i == len(self.springs):
                    self.updating = False

    def run(self):  # One of the property methods inherited by Thread
        while self.updating:
            self.spring_update()
            self.neighbor_list()
            self.neighbor_update()
            count = 0

            for i in range(len(self.springs)):
                if not int(self.springs[i].speed) and not int(self.springs[i].wave_height):
                    count += 1
            if count == len(self.springs):
                stop_waves = Thread(target=self.stop)
                stop_waves.start()

            time.sleep(0.01)


if __name__ == "__main__":
    Water()
