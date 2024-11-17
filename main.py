import pygame
import sys
import random
import heapq
import numpy as np
from pygame.display import update
from env import *

class Snake(object):
    def __init__(self):
        self.length = 1 # chiều dài ban đầu bằng 0
        self.coords = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))] # xuất hiện giữa bảng
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT]) # các hướng con rắn có thể di chuyển
        self.color = (240, 240, 240)
        self.snake_tail = (0, 0)

    #Hàm dùng để láy 
    def head_position(self):
        return self.coords[0]

    def snake_turn(self, point):
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.head_position()
        x, y = self.direction
        new = (((cur[0] + (x*GRIDSIZE))), (cur[1] + (y*GRIDSIZE)))
        if (len(self.coords) > 2 and new in self.coords[2:-1]) or new[0] == -GRIDSIZE or new[1] == -GRIDSIZE or new[0] == SCREEN_WIDTH or new[1] == SCREEN_HEIGHT:
            self.reset_game()
            grid_game_reset()
            food.random_pos()
        else:
            
            for i in self.coords:
                grid[int(i[1] / GRIDSIZE), int(i[0] / GRIDSIZE)] = 1
            
            grid[int(new[1] / GRIDSIZE), int(new[0] / GRIDSIZE)] = 3
            
            if len(self.coords) + 1 > self.length:
                old = self.coords.pop()
                grid[int(old[1] / GRIDSIZE), int(old[0] / GRIDSIZE)] = 0
            self.coords.insert(0, new)
            grid[int(self.coords[-1][1] / GRIDSIZE), int(self.coords[-1][0] / GRIDSIZE)] = 4
            self.snake_tail = self.coords[-1]

    def reset_game(self):
        global score
        self.length = 1
        self.coords = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        score = 0
    
    def draw(self, surface):
        for index, p in enumerate(self.coords):
            r = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            if index == 0:
                pygame.draw.rect(surface, (254, 110, 26), r)
                pygame.draw.rect(surface, (93, 216, 228), r, 1)
                continue
            if index == snake.length - 1:
                pygame.draw.rect(surface, (150, 148, 255), r)
                pygame.draw.rect(surface, (93, 216, 228), r, 1)
                continue
            pygame.draw.rect(surface, (abs(240 - 4*index), abs(240 - 4*index), abs(240 - 4*index)), r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1)

    def user_key(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake_turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.snake_turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake_turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake_turn(RIGHT)

class Food(object):
    def __init__(self):
        self.position = (0, 0)
        self.color = (161, 238, 189)
        self.random_pos()

    def get_position(self):
        return self.position

    def random_pos(self):
        grid[int(self.position[1]/GRIDSIZE), int(self.position[0]/GRIDSIZE)] = 0
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE, random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)
        #if the 
        if self.position in snake.coords:
            self.random_pos() #recursive call
        grid[int(self.position[1]/GRIDSIZE), int(self.position[0]/GRIDSIZE)] = 2

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, (93, 216, 228), r, 1)

    def get_position(self):
        return self.position

def draw_grid(surface, myfont):
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            if (x + y) % 2 == 0:
                r = pygame.Rect((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE))
                pygame.draw.rect(surface, (44, 47, 51), r)
                text = myfont.render(str((x, y)), 1, (0, 0, 0))
                # surface.blit(text, ((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE)))
            else:
                rr = pygame.Rect((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE))
                pygame.draw.rect(surface, (35, 39, 42), rr)
                text = myfont.render(str((x, y)), 1, (0, 0, 0))
                # surface.blit(text, ((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE)))

class Node():
    def __init__(self, position, parent = None):
        self.position = (int(position[0]), int(position[1]))
        #parent is the parent node
        self.parent = parent
    
    # Compare Nodes
    def __eq__(self, other):
        return self.position == other.position

    # Print Nodes
    def __repr__(self):
        return str(self.position)

    def get_parent(self):
        return self.parent

    def get_neighbors(self):
        #returns neighbors (UP, RIGHT, DOWN, LEFT)
        #THIS DOES NOT MEAN THE NEIGHBORING coords ARE not obstacles
        parent_pos = self.position
        x = parent_pos[0]
        y = parent_pos[1]

        children = []
        for new_position in [UP, RIGHT, DOWN, LEFT]:
            node_position = (self.position[0] + new_position[0], self.position[1] + new_position[1])
            temp = self
            broken = False
            while temp is not None:
                if (temp.position == node_position):
                    broken = True
                    break
                temp = temp.parent
            if broken:
                continue
            if node_position[0] >= GRID_WIDTH or node_position[0] < 0 or node_position[1] >= GRID_HEIGHT or node_position[1] < 0:
                continue
            if (grid[node_position[1], node_position[0]] == 1 or grid[node_position[1], node_position[0]] == 3 or (grid[node_position[1], node_position[0]] == 4)):
                continue
            new_node = Node(node_position, self)
            children.append(new_node)
        return children

    def check_on_grid(self):
        x = self.position[0]
        y = self.position[1]
        return (x >= GRID_WIDTH or x < 0 or y >= GRID_HEIGHT or y < 0)
    
    def check_snake_node(self, snake):
        x = self.position[0]
        y = self.position[1]
        
        for pos in snake.coords:
            if (pos[0] == x and pos[1] == y):
                return True
        return False
    
    def get_position(self):
        return self.position
    
    def listify(self):
        list = []
        list.insert(0, self.position)

        node = self.parent
        while node is not None:
            list.insert(0, node.position)
            node = node.parent
        return list

def check_collision(nodes):
        return_bools = []
        for node in nodes:
            return_bools.append(node.check_on_grid() and (not node.check_snake_node))
            
        return return_bools

def dfs(start_pos, goal_pos):
    #fake stack đẻ chạy thuật toán
    open_list = []
    #mảng lưu các vị trí đã đi qua
    visited = []

    start_node = Node(start_pos)
    goal_node = Node(goal_pos)

    open_list.append(start_node)

    while (len(open_list) != 0):
        current_node = open_list.pop(-1) # lấy phần tử cuối mảng theo stack Last in first out 

        visited.append(current_node)
        
        if (current_node == goal_node):
            path = []
            while current_node != start_node:
                path.append(current_node.get_position())
                current_node = current_node.get_parent()
            #code before wouldnt insert start node into path so i added it here
            path.append(start_node.get_position())

            return path[::-1]

        cur_x = (start_node.get_position())[0]
        cur_y = (start_node.get_position())[1]
        goal_x = goal_node.get_position()[0]
        goal_y = goal_node.get_position()[1]

        current_node_neighbors = current_node.get_neighbors()

        for child in current_node_neighbors:
            if child in visited:
                continue

            if child not in open_list:
                open_list.insert(0, child) # thêm vào đầu danh sách
    
    return None
        
def bfs(start_pos, goal_pos):
    #fake queue đẻ chạy thuật toán
    open_list = []
    #mảng lưu các vị trí đã đi qua
    visited = []

    start_node = Node(start_pos)
    goal_node = Node(goal_pos)

    open_list.append(start_node)

    while len(open_list) != 0:
        current_node = open_list.pop(0)  # Lấy phần tử đầu tiên trong danh sách (thay vì phần tử cuối trong DFS)

        visited.append(current_node)
        
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.get_position())
                current_node = current_node.get_parent()
            path.append(start_node.get_position())

            return path[::-1]

        cur_x = (start_node.get_position())[0]
        cur_y = (start_node.get_position())[1]
        goal_x = goal_node.get_position()[0]
        goal_y = goal_node.get_position()[1]

        current_node_neighbors = current_node.get_neighbors()

        for child in current_node_neighbors:
            # Nếu nút là vật cản hoặc đã có trong visited thì bỏ qua
            if child in visited:
                continue

            # Nếu nút chưa có trong open_list, thêm vào open_list
            if child not in open_list:
                open_list.append(child)

    return None


def a_star(start_pos, goal_pos):
    open_list = []  # Danh sách các nút cần xét
    visited = []  # Danh sách các nút đã xét
    
    start_node = Node(start_pos)
    goal_node = Node(goal_pos)
    
    # Hàm heuristic, tính khoảng cách Manhattan giữa hai điểm
    def heuristic(node, goal_node):
        return abs(node.get_position()[0] - goal_node.get_position()[0]) + \
               abs(node.get_position()[1] - goal_node.get_position()[1])

    # Dùng heapq để làm danh sách open_list, mỗi phần tử là một tuple (f(n), node)
    heapq.heappush(open_list, (0 + heuristic(start_node, goal_node), start_node))  # f(n) = g(n) + h(n)

    # Mảng lưu trữ g_cost, h_cost, và trace
    g_costs = {start_node: 0}  # Chi phí đi từ điểm bắt đầu
    h_costs = {}
    traces = {}

    while open_list:
        # Lấy nút có f(n) nhỏ nhất từ open_list
        _, current_node = heapq.heappop(open_list)
        visited.append(current_node)

        if current_node == goal_node:
            # Truy vết đường đi từ goal về start
            path = []
            while current_node != start_node:
                path.append(current_node.get_position())
                current_node = traces[current_node]  # Sử dụng trace để truy vết đường đi
            path.append(start_node.get_position())
            return path[::-1]  # Đảo ngược đường đi để từ start đến goal

        # Lấy các láng giềng của nút hiện tại
        current_node_neighbors = current_node.get_neighbors()

        for child in current_node_neighbors:
            if child in visited:
                continue  # Bỏ qua nếu child đã được xét

            # Tính chi phí g(n) (cost so far)
            g_cost = g_costs[current_node] + 1  # Chi phí giữa các nút là 1 (có thể thay đổi)
            h_cost = heuristic(child, goal_node)  # Tính chi phí heuristic
            f_cost = g_cost + h_cost  # f(n) = g(n) + h(n)

            if child not in g_costs or g_cost < g_costs[child]:  # Nếu child chưa có trong open_list hoặc có chi phí g_cost thấp hơn
                g_costs[child] = g_cost
                h_costs[child] = h_cost
                traces[child] = current_node  # Lưu trace
                heapq.heappush(open_list, (f_cost, child))
            elif g_cost == g_costs[child]:  # Nếu chi phí g_cost của child bằng chi phí hiện tại trong open_list
                if h_cost < h_costs[child]:  # Nếu chi phí heuristic của child nhỏ hơn
                    h_costs[child] = h_cost
                    traces[child] = current_node  # Cập nhật trace

    return None  # Nếu không tìm được đường đi

def grid_game_reset():
    global grid
    grid = np.zeros((GRID_WIDTH, GRID_HEIGHT))
    grid = grid.astype(int)

grid_game_reset()

directions = []

def snake_add_direction(path):
    directions = []

    for i in range(len(path) - 1):
        direction_vector = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        directions.insert(0,direction_vector)
    return directions

def snake_dead():
    snake.reset_game()
    grid_game_reset()
    food.random_pos()
    while True:
        for event in pygame.event.get():
                print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



def main():
    global score, food, snake, surface, simulated
    pygame.init()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    myfont = pygame.font.SysFont("monospace", 16)

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    draw_grid(surface, myfont)

    snake = Snake()
    food = Food()

    while (True):
        
        clock.tick(10)
        if snake.head_position() == food.get_position():
            snake.length += 1
            score = snake.length - 1
            food.random_pos()
            print("The score is {}".format(score))
            print("NEW FOOD: (" + str(food.get_position()[0] / GRIDSIZE) + ", " + str(food.get_position()[1] / GRIDSIZE) + ")")

        snake.draw(surface)
        food.draw(surface)
        screen.blit(surface, (0, 0))
        screen.blit(surface, (0, 0))
        text = myfont.render("Score {0}".format(score), 1, (255, 255, 0))
        screen.blit(text, (5, 10))
        
        draw_grid(surface, myfont)
        
        start_pos = (snake.head_position()[0]/GRIDSIZE, snake.head_position()[1]/GRIDSIZE)
        food_pos = (food.get_position()[0] / GRIDSIZE, food.get_position()[1]/GRIDSIZE)

        path = dfs(start_pos, food_pos)
        print(path)
        snake_dir = snake_add_direction(path).pop()

        snake.snake_turn(snake_dir)
        snake.move()
         
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()