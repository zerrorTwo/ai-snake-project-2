import pygame
import sys
import numpy as np
from .constants import *
from .entities.snake import Snake
from .entities.food import Food
from .entities.obstacle import Obstacle
from .ui.menu import Menu
from .ui.grid import draw_grid
from .algorithms import astar, bfs, ac3, simulated_annealing


class Game:
    def __init__(self, ai_mode=False, display_game=False):
        pygame.init()
        pygame.display.set_caption("Cá chép hoá rồng!!")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.ai_mode = ai_mode
        self.display_game = display_game

        self.reset_game()
        self.previous_moves = []  # Lưu các bước di chuyển gần nhất
        self.max_moves_without_food = 100  # Giới hạn số bước không ăn được thức ăn
        self.moves_without_food = 0  # Đếm số bước không ăn được thức ăn

    def reset_game(self):
        """Khởi tạo lại game"""
        self.grid = init_grid()
        self.snake = Snake()
        self.obstacles = Obstacle()
        self.food = Food()
        self.food.randomize_position(self.grid, self.snake.positions, self.obstacles.positions)
        self.score = 0

    def run(self, network=None):
        """Chạy game loop chính"""
        if self.ai_mode and self.display_game:
            running = True
            while running:
                self.clock.tick(FPS)
                if not self.handle_events():
                    break
                if not self.update(algorithm='AI', network=network):
                    break
                self.draw()
            return self.score
        
        while True:
            algorithm = Menu.show_main_menu(self.screen)
            self.reset_game()
            
            running = True
            while running:
                self.clock.tick(FPS)
                if not self.handle_events():
                    break
                if not self.update(algorithm):
                    break
                self.draw()

    def draw(self):
        """Vẽ game"""
        self.surface.fill(BLACK)
        draw_grid(self.surface)

        self.obstacles.draw(self.surface)
        self.snake.draw(self.surface)
        self.food.draw(self.surface)

        self.screen.blit(self.surface, (0, 0))

        score_text = self.font.render(f"Score {self.score}", True, (255, 255, 0))
        self.screen.blit(score_text, (5, 10))

        pygame.display.update()

    def handle_events(self):
        """Xử lý các sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self.pause_game()
        return True

    def pause_game(self):
        """Xử lý tạm dừng game"""
        continue_button, restart_button = Menu.show_pause_menu(self.screen)

        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if continue_button.collidepoint(event.pos):
                        return True
                    elif restart_button.collidepoint(event.pos):
                        return False
        return True

    def update(self, algorithm=None, network=None):
        """Cập nhật trạng thái game"""
        # Nếu đang chạy chế độ AI
        if self.ai_mode and network:
            # TODO: Thêm logic để lấy input state và sử dụng neural network
            # Ví dụ:
            state = self.get_state()  # Cần thêm hàm này
            output = network.forward(state)
            direction = self.get_direction_from_output(output)  # Cần thêm hàm này
            
            # Di chuyển rắn theo hướng đã chọn
            self.snake.turn(direction)
            if not self.snake.move(self.grid, self.obstacles.positions):
                return False
            
        else:  # Chế độ thuật toán tìm đường
            # Lấy vị trí hiện tại và đích
            start_pos = (self.snake.get_head_position()[0] / GRIDSIZE,
                        self.snake.get_head_position()[1] / GRIDSIZE)
            goal_pos = (self.food.position[0] / GRIDSIZE,
                       self.food.position[1] / GRIDSIZE)

            # Tìm đường đi theo thuật toán được chọn
            path = None
            if algorithm == 'A*':
                path = astar.a_star(start_pos, goal_pos, self.grid, self.obstacles.positions)
            elif algorithm == 'BFS':
                path = bfs.bfs(start_pos, goal_pos, self.grid, self.obstacles.positions)
            elif algorithm == 'AC3':
                path = ac3.ac3(start_pos, goal_pos, (GRID_WIDTH, GRID_HEIGHT),
                              self.obstacles.positions, self.grid)
            elif algorithm == 'SA':
                path = simulated_annealing.simulated_annealing(start_pos, goal_pos,
                                                               self.grid, self.obstacles.positions)

            if path is None or len(path) < 2:
                return False

            # Tính hướng di chuyển từ đường đi
            next_pos = path[1]
            direction = (
                next_pos[0] - start_pos[0],
                next_pos[1] - start_pos[1]
            )

            # Di chuyển rắn
            self.snake.turn(direction)
            if not self.snake.move(self.grid, self.obstacles.positions):
                return False

        # Kiểm tra ăn thức ăn
        if self.snake.get_head_position() == self.food.position:
            self.snake.length += 1
            self.score = self.snake.length - 1
            self.food.randomize_position(self.grid, self.snake.positions,
                                       self.obstacles.positions)

        return True

    def get_state(self):
        """Lấy trạng thái hiện tại của game cho neural network"""
        # TODO: Implement state extraction
        # Ví dụ đơn giản:
        head_x, head_y = self.snake.get_head_position()
        food_x, food_y = self.food.position
        
        # Tạo vector 24 chiều chứa thông tin về:
        # - Vị trí tương đối của thức ăn
        # - Các chướng ngại vật xung quanh
        # - Hướng di chuyển hiện tại
        # - Vị trí thân rắn
        state = np.zeros(24)
        # ... điền thông tin vào state ...
        
        return state.reshape(1, -1)  # Reshape để phù hợp với neural network

    def get_direction_from_output(self, output):
        """Chuyển đổi output của neural network thành hướng di chuyển"""
        # output là một mảng 4 chiều [lên, phải, xuống, trái]
        direction_idx = np.argmax(output)
        
        # Chuyển đổi index thành hướng di chuyển
        directions = [
            (0, -1),  # lên
            (1, 0),   # phải
            (0, 1),   # xuống
            (-1, 0)   # trái
        ]
        
        return directions[direction_idx]

    def run_ai_mode(self, network):
        """Chạy game trong chế độ AI training"""
        self.reset_game()
        running = True
        while running:
            self.clock.tick(FPS_AI)
            
            # Xử lý các sự kiện cơ bản như thoát game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # Cập nhật và vẽ game
            if not self.update(algorithm='AI', network=network):
                break
            self.draw()  # Thêm vào để hiển thị giao diện

        return self.score