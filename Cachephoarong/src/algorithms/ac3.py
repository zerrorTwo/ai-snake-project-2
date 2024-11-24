from collections import deque
from .node import Node
from ..constants import *
import heapq


def get_domain(pos, grid_size, obstacles, grid):
    """Lấy miền giá trị hợp lệ cho một vị trí"""
    domain = []
    x, y = pos
    for dx, dy in [UP, RIGHT, DOWN, LEFT]:
        new_x, new_y = x + dx, y + dy
        if (0 <= new_x < grid_size[0] and
                0 <= new_y < grid_size[1] and
                (new_x * GRIDSIZE, new_y * GRIDSIZE) not in obstacles and
                grid[new_y][new_x] not in [SNAKE_BODY, SNAKE_HEAD, SNAKE_TAIL]):
            domain.append((dx, dy))
    return domain


def ac3(start_pos, goal_pos, grid_size, obstacles, grid):
    queue = deque()
    domains = {}
    current = Node(start_pos)
    goal = Node(goal_pos)

    open_list = [(current, 0)]
    visited = {current}
    parent = {}

    while open_list:
        current_node, current_cost = open_list.pop(0)

        if current_node.position == goal_pos:
            path = []
            while current_node in parent:
                path.append(current_node.position)
                current_node = parent[current_node]
            path.append(start_pos)
            return path[::-1]

        current_domain = get_domain(current_node.position, grid_size, obstacles, grid)

        for dx, dy in current_domain:
            next_pos = (current_node.position[0] + dx, current_node.position[1] + dy)
            next_node = Node(next_pos)

            if next_node not in visited:
                visited.add(next_node)
                parent[next_node] = current_node

                h_cost = abs(next_pos[0] - goal_pos[0]) + abs(next_pos[1] - goal_pos[1])

                insert_idx = 0
                while (insert_idx < len(open_list) and
                       h_cost > abs(open_list[insert_idx][0].position[0] - goal_pos[0]) +
                       abs(open_list[insert_idx][0].position[1] - goal_pos[1])):
                    insert_idx += 1
                open_list.insert(insert_idx, (next_node, current_cost + 1))

    return None