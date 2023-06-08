import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont('arial', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

WHITE = (255, 255, 255)
PURPLE = (255, 0, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (146, 213, 254)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 10


class Snake:

    def __init__(self, w=680, h=520):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()

        self.direction = Direction.RIGHT

        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y), Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.is_normal_game = True
        self.score = 0
        self.food = None
        self.obstacles = []
        self.portals = []
        self.speed_boost = []
        self._place_food()

    def show_menu(self):
        menu_font = pygame.font.SysFont('arial', 25)
        menu_text = menu_font.render("Snake Game Menu", True, WHITE)
        normal_game_text = menu_font.render("1. Play Normal Game", True, WHITE)
        obstacle_game_text = menu_font.render("2. Play Game with Obstacles", True, WHITE)
        portals_game_text = menu_font.render("3. Play with Portals", True, WHITE)
        speed_boost_text = menu_font.render("4. Play with Speed Boost", True, WHITE)
        while True:
            self.display.fill(BLACK)
            self.display.blit(menu_text, (self.w / 2 - menu_text.get_width() / 2, self.h / 2 - 100))
            self.display.blit(normal_game_text, (self.w / 2 - normal_game_text.get_width() / 2, self.h / 2 - 50))
            self.display.blit(obstacle_game_text, (self.w / 2 - obstacle_game_text.get_width() / 2, self.h / 2))
            self.display.blit(portals_game_text, (self.w / 2 - portals_game_text.get_width() / 2, self.h / 2 + 50))
            self.display.blit(speed_boost_text, (self.w / 2 - speed_boost_text.get_width() / 2, self.h / 2 + 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return
                    elif event.key == pygame.K_2:
                        self.is_normal_game = False
                        self._place_obstacle()
                        return
                    elif event.key == pygame.K_3:
                        self._place_portals()
                        return
                    elif event.key == pygame.K_4:
                        self._place_speed_boost()
                        return

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.is_normal_game == False:
            self._place_obstacle()

        if self.food in self.snake or self.food in self.obstacles:
            self._place_food()

    def _place_portals(self):
        self.portals.clear()

        x1 = random.randint(2, (self.w - BLOCK_SIZE) // BLOCK_SIZE - 2) * BLOCK_SIZE
        y1 = random.randint(2, (self.h - BLOCK_SIZE) // BLOCK_SIZE - 2) * BLOCK_SIZE
        portal1 = Point(x1, y1)

        x2, y2 = portal1
        while abs(x2 - x1) < BLOCK_SIZE * 2 or abs(y2 - y1) < BLOCK_SIZE * 2:
            x2 = random.randint(2, (self.w - BLOCK_SIZE) // BLOCK_SIZE - 2) * BLOCK_SIZE
            y2 = random.randint(2, (self.h - BLOCK_SIZE) // BLOCK_SIZE - 2) * BLOCK_SIZE
        portal2 = Point(x2, y2)

        self.portals.extend([portal1, portal2])

    def _teleport(self):
        destination = random.choice([p for p in self.portals if p != self.head])
        self.head = destination

        self.portals.remove(destination)

        self._place_portals()

    def _place_obstacle(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        obstacle = Point(x, y)
        if obstacle not in self.snake and obstacle != self.food and obstacle not in self.obstacles:
            self.obstacles.append(obstacle)

    def _place_speed_boost(self):
        self.speed_boost.clear()
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        speed_boost = Point(x, y)
        if speed_boost in self.snake or speed_boost == self.food:
            self._place_speed_boost()
        else:
            self.speed_boost.append(speed_boost)
        global SPEED
        SPEED += 5

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        self._move(self.direction)
        self.snake.insert(0, self.head)
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        if self.head in self.portals:
            self._teleport()

        if self.head in self.speed_boost:
            self._place_speed_boost()

        self._update_ui()
        self.clock.tick(SPEED)

        return game_over, self.score

    def _is_collision(self):
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        if self.head in self.snake[1:]:
            return True
        if self.head in self.obstacles:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        for obstacle in self.obstacles:
            pygame.draw.rect(self.display, WHITE, pygame.Rect(obstacle.x, obstacle.y, BLOCK_SIZE, BLOCK_SIZE))

        for portal in self.portals:
            pygame.draw.rect(self.display, PURPLE, pygame.Rect(portal.x, portal.y, BLOCK_SIZE, BLOCK_SIZE))

        for speed_boost in self.speed_boost:
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(speed_boost.x, speed_boost.y, BLOCK_SIZE, BLOCK_SIZE))

        for snake in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(snake.x, snake.y, BLOCK_SIZE, BLOCK_SIZE))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)


if __name__ == '__main__':
    game = Snake()

    game.show_menu()
    while True:
        game_over, score = game.play_step()
        if game_over == True:
            break

    print('Final Score:', score)

    pygame.quit()
