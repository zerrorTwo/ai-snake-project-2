import random
import math
from .node import Node

def heuristic(node, goal_node):
    """Tính khoảng cách Manhattan"""
    return abs(node.position[0] - goal_node.position[0]) + \
           abs(node.position[1] - goal_node.position[1])

def simulated_annealing(start_pos, goal_pos, grid, obstacles):
    initial_temp = 1000
    final_temp = 1
    alpha = 0.95

    current = Node(start_pos)
    goal = Node(goal_pos)

    current_path = [current]
    best_path = current_path
    best_cost = float('inf')

    temp = initial_temp
    while temp > final_temp:
        current_node = current_path[-1]
        neighbors = current_node.get_neighbors(grid, obstacles)

        if not neighbors:
            break

        next_node = random.choice(neighbors)
        new_path = current_path + [next_node]

        current_cost = len(current_path) + heuristic(current_path[-1], goal)
        new_cost = len(new_path) + heuristic(next_node, goal)

        delta_cost = new_cost - current_cost
        if delta_cost < 0 or random.random() < math.exp(-delta_cost / temp):
            current_path = new_path

            if new_cost < best_cost:
                best_path = new_path
                best_cost = new_cost

        if next_node == goal:
            return [node.position for node in best_path]

        temp *= alpha

    if best_path:
        return [node.position for node in best_path]
    return None