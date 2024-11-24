from collections import deque
from .node import Node

def bfs(start_pos, goal_pos, grid, obstacles):
    open_list = deque()
    visited = set()

    start_node = Node(start_pos)
    goal_node = Node(goal_pos)

    open_list.append(start_node)
    visited.add(start_node)

    while open_list:
        current_node = open_list.popleft()

        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            path.append(start_node.position)
            return path[::-1]

        for child in current_node.get_neighbors(grid, obstacles):
            if child not in visited:
                visited.add(child)
                open_list.append(child)

    return None