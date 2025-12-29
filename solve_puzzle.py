from RushHourPuzzle import RushHourPuzzle
from Node import Node
from BFS import BFS
from AStar import AStar, h1, h2, h3, h4
import time


def solve_with_bfs(csv_file):
    """
    Solve puzzle using BFS
    """
    print(f"\n{'='*70}")
    print(f"BFS (Breadth-First Search)")
    print('='*70)
    
    puzzle = RushHourPuzzle(csv_file)
    
    print("\nInitial state:")
    puzzle.displayBoard()
    
    start_time = time.time()
    goal_node = BFS(
        puzzle,
        lambda state: state.successorFunction(),
        lambda state: state.isGoal()
    )
    end_time = time.time()
    
    if goal_node is None:
        print("No solution found!")
        return None
    
    solution = goal_node.getSolution()
    path = goal_node.getPath()
    
    print(f"\nSolution found!")
    print(f"Moves: {len(solution)}")
    print(f"Cost: {goal_node.g}")
    print(f"Time: {end_time - start_time:.4f}s")
    
    print("\nActions:")
    directions = {'L': 'Left', 'R': 'Right', 'U': 'Up', 'D': 'Down'}
    for i, (vehicle, direction) in enumerate(solution, 1):
        print(f"{i}. {vehicle} -> {directions[direction]}")
    
    print("\nFinal state:")
    path[-1].displayBoard()
    
    return {
        'moves': len(solution),
        'cost': goal_node.g,
        'time': end_time - start_time
    }


def solve_with_astar(csv_file, heuristic_func, heuristic_name):
    """
    Solve puzzle using A* with given heuristic
    """
    print(f"\n{'='*70}")
    print(f"A* with {heuristic_name}")
    print('='*70)
    
    puzzle = RushHourPuzzle(csv_file)
    
    print("\nInitial state:")
    puzzle.displayBoard()
    
    start_time = time.time()
    goal_node = AStar(
        puzzle,
        lambda state: state.successorFunction(),
        lambda state: state.isGoal(),
        heuristic_func
    )
    end_time = time.time()
    
    if goal_node is None:
        print("No solution found!")
        return None
    
    solution = goal_node.getSolution()
    path = goal_node.getPath()
    
    print(f"\nSolution found!")
    print(f"Moves: {len(solution)}")
    print(f"Cost: {goal_node.g}")
    print(f"Time: {end_time - start_time:.4f}s")
    
    print("\nActions:")
    directions = {'L': 'Left', 'R': 'Right', 'U': 'Up', 'D': 'Down'}
    for i, (vehicle, direction) in enumerate(solution, 1):
        print(f"{i}. {vehicle} -> {directions[direction]}")
    
    print("\nFinal state:")
    path[-1].displayBoard()
    
    return {
        'moves': len(solution),
        'cost': goal_node.g,
        'time': end_time - start_time
    }


def compare_all_algorithms(csv_file):
    """
    Compare BFS and all A* heuristics on the same puzzle
    """
    print(f"\n{'='*70}")
    print(f"COMPARING ALL ALGORITHMS ON: {csv_file}")
    print('='*70)
    
    results = {}
    
    # Test BFS
    results['BFS'] = solve_with_bfs(csv_file)
    
    # Test A* with h1
    results['A* h1'] = solve_with_astar(csv_file, h1, "h1 (distance to exit)")
    
    # Test A* with h2
    results['A* h2'] = solve_with_astar(csv_file, h2, "h2 (distance + blocking vehicles)")
    
    # Test A* with h3
    results['A* h3'] = solve_with_astar(csv_file, h3, "h3 (h2 + clearing cost)")
    
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    print(f"{'Algorithm':<20} {'Moves':<10} {'Time (s)':<10}")
    print('-'*70)
    for name, result in results.items():
        if result:
            print(f"{name:<20} {result['moves']:<10} {result['time']:<10.4f}")


def compare_heuristics(csv_file):
    """
    Compare only A* heuristics (h1, h2, h3)
    """
    print(f"\n{'='*70}")
    print(f"COMPARING HEURISTICS ON: {csv_file}")
    print('='*70)
    
    results = {}
    
    # Test h1
    results['h1'] = solve_with_astar(csv_file, h1, "h1 (distance to exit)")
    
    # Test h2
    results['h2'] = solve_with_astar(csv_file, h2, "h2 (distance + blocking vehicles)")
    
    # Test h3
    results['h3'] = solve_with_astar(csv_file, h3, "h3 (h2 + clearing cost)")
    
    # Test h4 (terrible heuristic)
    results['h4'] = solve_with_astar(csv_file, h4, "h4 (always 0 - TERRIBLE!)")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print('='*70)
    print(f"{'Heuristic':<20} {'Moves':<10} {'Time (s)':<10}")
    print('-'*70)
    for name, result in results.items():
        if result:
            print(f"{name:<20} {result['moves']:<10} {result['time']:<10.4f}")


if __name__ == "__main__":
    # Compare all algorithms
    compare_all_algorithms("examples/e-f.csv")
    

