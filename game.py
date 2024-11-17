import pygame
import random
import time
import math
import sys
from pygame.locals import *
import io


class CarAgent:
    def __init__(self, x, y, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.0
        self.position = pygame.Vector2(x, y)
        self.max_speed = 5
        self.angle = -90
        self.rotation = 0
        self.clock = pygame.time.Clock()

    def _get_rotated_rect_corners(self, x, y, width, height, angle):
        cx, cy = x + width / 2, y + height / 2

        corners = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ]

        rotated_corners = []
        for corner in corners:
            corner_x, corner_y = corner
            translated_x, translated_y = corner_x - cx, corner_y - cy
            rotated_x = translated_x * math.cos(
                math.radians(angle)
            ) - translated_y * math.sin(math.radians(angle))
            rotated_y = translated_x * math.sin(
                math.radians(angle)
            ) + translated_y * math.cos(math.radians(angle))
            rotated_corners.append((rotated_x + cx, rotated_y + cy))

        return rotated_corners

    def draw(self, win):
        car = pygame.image.load("assets/car.png")
        car = pygame.transform.scale(car, (self.width, self.height))
        car = pygame.transform.rotate(car, self.angle)
        win.blit(
            car,
            self.position - pygame.Vector2(car.get_width() / 2, car.get_height() / 2),
        )

        self.corners = self._get_rotated_rect_corners(
            self.position.x - self.width / 2,
            self.position.y - self.height / 2,
            self.width,
            self.height,
            -self.angle,
        )
        pygame.draw.polygon(win, (0, 255, 0), self.corners, 2)

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.up()
        elif keys[pygame.K_DOWN]:
            self.down()
        elif keys[pygame.K_SPACE]:
            self.brk()
        else:
            self.decelerate()

        if keys[pygame.K_LEFT]:
            self.left()
        elif keys[pygame.K_RIGHT]:
            self.right()
        else:
            self.onward()

        self.velocity.x += self.acceleration
        if self.velocity.x > self.max_speed:
            self.velocity.x = self.max_speed
        elif self.velocity.x < -self.max_speed:
            self.velocity.x = -self.max_speed

        self.position += self.velocity.rotate(-self.angle) * 0.3
        self.angle += math.degrees(self.turn()) * 0.0001

    def turn(self):
        if self.rotation == 0:
            return 0
        else:
            return self.velocity.x / (math.sin(math.radians(self.rotation)))

    def up(self):
        if self.velocity.x > 0:
            self.acceleration = -1.0
        else:
            self.acceleration -= 0.5

    def down(self):
        if self.velocity.x < 0:
            self.acceleration = 1.0
        else:
            self.acceleration += 0.5

    def brk(self):
        if self.velocity.x > 0:
            self.acceleration = -0.5
        else:
            self.acceleration = 0.5

    def decelerate(self):
        if self.velocity.x > 0.1:
            self.acceleration = -0.1
        elif self.velocity.x < 0:
            self.acceleration = 0.1
        else:
            self.acceleration = 0
            self.velocity.x = 0

    def left(self):
        self.rotation -= 0.1

    def right(self):
        self.rotation += 0.1

    def onward(self):
        self.rotation = 0


class Game:
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 400
        self.win = pygame.display.set_mode((self.width, self.height))

        self.clock = pygame.time.Clock()
        self.car = CarAgent(250, 200, 100, 50, (255, 0, 0))
        self.log = False

        self.car1_pos = pygame.Vector2(30, 40)
        self.car2_pos = pygame.Vector2(30, 270)

        self.car1_rect = pygame.Rect(self.car1_pos.x, self.car1_pos.y, 50, 100)
        self.car2_rect = pygame.Rect(self.car2_pos.x, self.car2_pos.y, 50, 100)

    def detect_collision(self):
        car_polygon = self.car.corners
        car1_polygon = [
            (self.car1_pos.x, self.car1_pos.y),
            (self.car1_pos.x + 50, self.car1_pos.y),
            (self.car1_pos.x + 50, self.car1_pos.y + 100),
            (self.car1_pos.x, self.car1_pos.y + 100),
        ]
        car2_polygon = [
            (self.car2_pos.x, self.car2_pos.y),
            (self.car2_pos.x + 50, self.car2_pos.y),
            (self.car2_pos.x + 50, self.car2_pos.y + 100),
            (self.car2_pos.x, self.car2_pos.y + 100),
        ]

        if self.is_collision(car_polygon, car1_polygon) or self.is_collision(
            car_polygon, car2_polygon
        ):
            print("collision")
            return True

    def is_collision(self, car_polygon, other_polygon):
        for corner in car_polygon:
            if self.is_inside(corner, other_polygon):
                return True
        return False

    def is_inside(self, point, polygon):
        x, y = point
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def run(self):
        run = True
        t = 0
        while run:
            t += 1
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            bg = pygame.image.load("assets/bg.png")
            bg = pygame.transform.scale(bg, (400, 400))
            self.win.blit(bg, (0, 0))

            carimg = pygame.image.load("assets/bcar.png")
            carimg = pygame.transform.scale(carimg, (50, 100))

            self.win.blit(carimg, self.car1_pos)
            self.win.blit(carimg, self.car2_pos)

            self.car.move()
            self.car.draw(self.win)
            if self.log:
                if t % 10 == 0:
                    print("pos: ", self.car.position)
                    print("velocity: ", self.car.velocity)
                    print("acceleration: ", self.car.acceleration)
                    print("angle: ", self.car.angle)
                    print("rotation: ", self.car.rotation)
            pygame.display.update()
            if self.detect_collision():
                font = pygame.font.Font(None, 48)
                text = font.render("COLLISION", 1, (255, 0, 0))
                self.win.blit(text, (100, 200))
                pygame.display.update()
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
