from ..constants import *
class Node:
    def __init__(self, position, parent=None):
        self.position = (int(position[0]), int(position[1]))
        self.g_cost = float('inf')
        self.h_cost = float('inf')
        self.f_cost = float('inf')
        self.parent = parent

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __hash__(self):
        return hash(self.position)

    def get_neighbors(self, grid, obstacles):
        """Lấy các node láng giềng hợp lệ"""
        neighbors = []
        for direction in [UP, RIGHT, DOWN, LEFT]:
            new_pos = (
                self.position[0] + direction[0],
                self.position[1] + direction[1]
            )

            # Kiểm tra điều kiện hợp lệ
            if self._is_valid_position(new_pos, grid, obstacles):
                neighbors.append(Node(new_pos, self))

        return neighbors

    def _is_valid_position(self, pos, grid, obstacles):
        """Kiểm tra vị trí có hợp lệ không"""
        x, y = pos

        # Kiểm tra biên
        if (x < 0 or x >= GRID_WIDTH or
                y < 0 or y >= GRID_HEIGHT):
            return False

        # Kiểm tra chướng ngại vật
        if (x * GRIDSIZE, y * GRIDSIZE) in obstacles:
            return False

        # Kiểm tra thân rắn
        if grid[y][x] in [SNAKE_BODY, SNAKE_HEAD, SNAKE_TAIL]:
            return False

        return True