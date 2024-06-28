import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
TRANSFORM_SCALE = 2.5
WIDTH, HEIGHT = 1280, 720
BUTTON_RADIUS = 20
BUTTON_COLOR = (120, 120, 120)
FPS = 60
LINE_COLOR = (40, 40, 40)
LINE_WIDTH = 2
TEXT_COLOR = (0, 0, 0)

# Create the Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 36)  # Use default system font, size 36
pygame.display.set_caption("Kaooa Game")
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Vulture(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = None
        self.color = (225, 0, 0)


class Crow(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = None
        self.color = (225, 225, 0)


class Option(Player):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = None
        self.color = (135, 167, 255)

class Game:
    def __init__(self):
        self.crow_count = 0
        self.crows = []
        self.vulture = None
        self.players = ("crow", "vulture")
        self.opt_moves = []
        self.start = False
        self.current_move = 0
        self.current_position = ()
        self.map = {}
        self.ended = False

    def switch_move(self):
        self.current_move = not self.current_move
        return self.players[not self.current_move]

    def add_player_to_map(self, x, y, neighbour_graph):
        if self.start:
            return

        if not self.is_spot_empty((x, y)):
            if self.map[(x, y)] == 2 and self.current_move == 1:
                self.move_to(self.current_position, x, y, neighbour_graph)
            elif self.check_move(x, y) and self.current_move == 1:
                self.move(x, y, neighbour_graph)
            else:
                self.clear_options()
                # print("Error: Spot Occupied")
            return

        self.clear_options()
        if not self.check_and_place(x, y):
            return

        if self.crow_count == 7:
            self.start = True

        # switches only after an appropriate move
        self.switch_move()
     
    def check_move(self, x, y):
        if self.current_move and self.vulture:
            if x == self.vulture.x and y == self.vulture.y:
                return True
        else:
            for crow in self.crows:
                if x == crow.x and y == crow.y:
                    return True
        return False

    def is_spot_empty(self, tup):
        if tup not in self.map.keys():
            return True
        else:
            return False

    def move_to(self, prev, x, y, neighbour_graph):
        if (x, y) in neighbour_graph[prev]["leaps"]:
            leap_index = neighbour_graph[prev]["leaps"].index((x, y))
            self.kill_crow(prev, leap_index, neighbour_graph)
            
            if 7 + len(the_game.crows) - the_game.crow_count < 4 and not the_game.ended:
                self.ended = True
                print("Vulture Won!")
        
        self.map.pop(prev)

        for opt in self.opt_moves:
            if opt.x == x and opt.y == y:
                self.opt_moves.remove(opt)
                break

        self.map[(x, y)] = self.current_move

        # crow
        if self.start and not self.current_move:
            for crow in self.crows:
                if crow.x == prev[0] and crow.y == prev[1]:
                    crow.x = x
                    crow.y = y

        elif self.current_move:
            if self.vulture.x == prev[0] and self.vulture.y == prev[1]:
                self.vulture.x, self.vulture.y = (x, y)

        self.clear_options()
        self.switch_move()

    def move(self, x, y, neighbour_graph):
        tup = (x, y)
        if self.is_spot_empty(tup):
            return
        
        if self.map[tup] == 2:
            self.move_to(self.current_position, x, y, neighbour_graph)
            return

        self.clear_options()

        # storing options as 2
        if (self.map[tup] == 0 or self.map[tup] == 1) and self.check_move(x, y):
            possible_moves = 0

            # if no must-kill condition, True this boole, comment the passed if statement
            boole = False
            for neighbour in neighbour_graph[tup]["neighbours"]:
                if neighbour not in self.map.keys():
                    if self.current_move and boole:
                        pass
                    else:
                        self.opt_moves.append(Option(neighbour[0], neighbour[1]))
                        self.map[neighbour] = 2
                        possible_moves += 1

                # leaps only for vulture
                elif self.current_move and neighbour in self.map.keys():
                    leap_index = neighbour_graph[tup]["neighbours"].index(neighbour)
                    leap = neighbour_graph[tup]["leaps"][leap_index]
                    if leap and leap not in self.map.keys():
                        if not boole:
                            boole = True
                            self.clear_options()
                        self.opt_moves.append(Option(leap[0], leap[1]))
                        self.map[leap] = 2
                        possible_moves += 1

            if self.current_move and possible_moves == 0 and not the_game.ended:
                the_game.ended = True
                print("Crows Won!")

        # add border for opted player
        self.current_position = (x, y)

    def kill_crow(self, tup, index, neighbour_graph):
        crow_ref = neighbour_graph[tup]["neighbours"][index]
        for crow in self.crows:
            if crow.x == crow_ref[0] and crow.y == crow_ref[1]:
                self.crows.remove(crow)
                self.map.pop((crow.x, crow.y))
                print(f"Crow at {tup} is dead.")
                return True

    def check_and_place(self, x, y):
        # case of crow
        if not self.current_move:
            if self.crow_count < 7:
                player_object = Crow(x, y)
                self.crows.append(player_object)
                self.crow_count += 1
                self.map[(player_object.x, player_object.y)] = self.current_move
                print(f"Crow is placed at {x, y}")
                return True

            print("Error: Crows has reached the maximum limit (7).")

        # case of vulture
        else:
            if not self.vulture:
                player_object = Vulture(x, y)
                self.vulture = player_object
                self.map[(player_object.x, player_object.y)] = self.current_move
                print(f"Vulture is placed at {x, y}")
                return True

            print("Error: Vulture already on the board!")
        return False
    
    def clear_options(self):
        for opt in self.opt_moves:
            if (opt.x, opt.y) in self.map.keys():
                self.map.pop((opt.x, opt.y))
        self.opt_moves = []

    def get_current_color(self):
        if not self.current_move:
            return (255, 246, 222)
        else:
            return (252, 225, 225)

def draw_button(x, y, color=BUTTON_COLOR, radius=BUTTON_RADIUS):
    pygame.draw.circle(screen, (255,255,255), (x, y), radius + 5)
    pygame.draw.circle(screen, color, (x, y), radius)

# checks if a given co-ordinates are within a circle
def is_inside_circle(mouse_x, mouse_y, button_x, button_y):
    distance = math.sqrt((mouse_x - button_x) ** 2 + (mouse_y - button_y) ** 2)
    return distance <= BUTTON_RADIUS

# transform from corner-based origin to center-based
def transform(tup):
    x, y = tup
    x *= TRANSFORM_SCALE
    y *= TRANSFORM_SCALE
    return ((WIDTH / 2 + x), HEIGHT / 2 + (-y))

# detransform from center-based origin to corner-based
def detransform(point):
    x, y = point
    x -= WIDTH / 2
    y = -(y - HEIGHT / 2)
    x /= TRANSFORM_SCALE
    y /= TRANSFORM_SCALE
    return (x, y)


# sorts the order of points on line
def insert_point_in_order(points, new_point):
    x_new, y_new = new_point
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]

        if x1 <= x_new <= x2 or x2 <= x_new <= x1:
            points.insert(i + 1, new_point)
            return

    points.append(new_point)

# finds intersection points between two lines
def find_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        return None

    intersection_x = round(
        ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4))
        / denominator,
        2,
    )
    intersection_y = round(
        ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4))
        / denominator,
        2,
    )

    return transform((intersection_x, intersection_y))


# Button coordinates
button_coordinates = [(0, 100), (-65, -100), (-105, 23), (105, 23), (65, -100)]
# corners = deepcopy(button_coordinates)

for i in range(len(button_coordinates)):
    button_coordinates[i] = transform(button_coordinates[i])

lines = [
    [(0, 100), (65, -100)],
    [(-65, -100), (0, 100)],
    [(-105, 23), (105, 23)],
    [(-105, 23), (65, -100)],
    [(-65, -100), (105, 23)],
]


def draw_line(start, end):
    pygame.draw.line(screen, LINE_COLOR, start, end, LINE_WIDTH)

def is_in_proximity(button, button_coordinates):
    for other_point in button_coordinates:
        distance = math.sqrt((button[0] - other_point[0])**2 + (button[1] - other_point[1])**2)
        if distance <= 1:
            return True
    return False

# finding the intersection points, then placing the button there.
for i in range(len(lines)):
    for j in range(len(lines)):
        line = lines[i]
        line2 = lines[j]
        if line == line2:
            continue

        button = find_intersection(line, line2)
        if is_in_proximity(button, button_coordinates):
            continue

        insert_point_in_order(lines[i], detransform(button))
        insert_point_in_order(lines[j], detransform(button))
        button_coordinates.append(button)

for i in range(len(lines)):
    for j in range(len(lines[i])):
        lines[i][j] = transform(lines[i][j])

# To store the neighbours and the leaps
neighbour_graph = {}

for button in button_coordinates:
    # neighbours (differ by 1 place), leaps (differ by 2 places)
    neighbour_graph[button] = {"neighbours": [], "leaps": []}

def add_to_neighbours(button, neighbour):
    if neighbour not in neighbour_graph[button]["neighbours"]:
        neighbour_graph[button]["neighbours"].append(neighbour)

def add_to_leaps(button, leap):
    if not leap or leap not in neighbour_graph[button]["leaps"]:
        neighbour_graph[button]["leaps"].append(leap)

for button in button_coordinates:
    for line in lines:
        if button in line:
            button_index = line.index(button)
            if button_index - 2 >= 0:
                add_to_leaps(button, line[button_index - 2])

            if button_index - 1 >= 0:
                add_to_neighbours(button, line[button_index - 1])
                if button_index - 2 < 0:
                    add_to_leaps(button, None)

            if button_index + 2 < len(line):
                add_to_leaps(button, line[button_index + 2])

            if button_index + 1 < len(line):
                add_to_neighbours(button, line[button_index + 1])
                if button_index + 2 >= len(line):
                    add_to_leaps(button, None)

the_game = Game()

# Main game loop
running = True
while running:
    screen.fill(the_game.get_current_color())

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for button_x, button_y in button_coordinates:
                    if is_inside_circle(mouse_x, mouse_y, button_x, button_y) and not the_game.ended:
                        if not the_game.start:
                            the_game.add_player_to_map(button_x, button_y, neighbour_graph)
                        elif (button_x, button_y) in the_game.map.keys():
                            the_game.move(button_x, button_y, neighbour_graph)

    if the_game.ended:
        text = font.render(f"{the_game.players[not the_game.current_move].capitalize()} Wins!", True, TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.center = (WIDTH // 2, HEIGHT - 50)
        screen.blit(text, text_rect)


    for line in lines:
        draw_line(line[0], line[3])

    # Draw buttons
    for opt in the_game.opt_moves:
        draw_button(opt.x, opt.y, opt.color)

    for crow in the_game.crows:
        draw_button(crow.x, crow.y, crow.color)

    if the_game.vulture:
        draw_button(the_game.vulture.x, the_game.vulture.y, the_game.vulture.color)

    for button_x, button_y in button_coordinates:
        if (button_x, button_y) not in the_game.map.keys():
            draw_button(button_x, button_y)

    for i in range(7 + len(the_game.crows) - the_game.crow_count):
        draw_button(WIDTH - i * 50 - 40, 40, color=(225, 225, 0))

    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
