from RushHourPuzzle import RushHourPuzzle
from Node import Node
import heapq
import time


def h1(state):
    """
    Heuristic 1: Distance from target vehicle (X) to exit
    Exit is at position (board_width - 2, board_height // 2 - 1)
    """
    for v in state.vehicles:
        if v["id"] == "X":
            goal_x = state.board_width - 2 #position de la sortie
            distance = goal_x - v["x"] #distance horizontale
            return distance
    return 0


def h2(state):
    """
    Heuristic 2: max(h1, number of vehicles blocking the path to exit)
    Using max instead of sum to ensure admissibility
    """
    # First get h1
    h1_value = h1(state)
    
    # Find X vehicle
    x_vehicle = None
    for v in state.vehicles:
        if v["id"] == "X":
            x_vehicle = v #yhws aala x
            break
    
    if x_vehicle is None:
        return h1_value
    
    # Count blocking vehicles
    blocking_count = 0
    x_row = x_vehicle["y"] #position de x 
    x_end = x_vehicle["x"] + x_vehicle["length"] #position de la fin dont le v se trouve
    goal_x = state.board_width - 2 # Position de la sortie
    
    # Check each column from X's end to goal
    for col in range(x_end, goal_x + 2):
        if col < state.board_width and state.board[x_row][col] != ' ': #nchofo dans la ligne de x esq kyn li ybloquiw la voie
            blocking_count += 1 
            #explication
            """""
Si X est en position 1-2:
- x_end = 3 (position après X)
- goal_x = 4 (sortie)
- La boucle vérifie les positions 3, 4, et 5 et 5 is the wall
- Trouve B et C comme obstacles
- blocking_count sera 2   """ 

    # Take the maximum to ensure admissibility c’est‑à‑dire pour tout état s : h(s) ≤ h*(s) (h* = coût réel minimal jusqu’au but).
    return max(h1_value, blocking_count)


def h3(state):
    """
    Heuristic 3: Analyses blocking vehicles and their minimum moves needed
    More sophisticated than h2 - considers if vehicles can move easily
    """
    # Get distance component (h1)
    h1_value = h1(state)
    
    # Find X vehicle
    x_vehicle = None
    for v in state.vehicles:
        if v["id"] == "X":
            x_vehicle = v
            break
    
    if x_vehicle is None:
        return h1_value
    
    # Analyze blocking vehicles
    x_row = x_vehicle["y"]
    x_end = x_vehicle["x"] + x_vehicle["length"]
    goal_x = state.board_width - 2
    
    min_moves = 0  # Minimal moves needed
    blockers = set()  # Track unique blockers
    
    # First pass: identify unique blockers
    for col in range(x_end, goal_x + 2):
        if col < state.board_width:
            cell = state.board[x_row][col]
            if cell != ' ' and cell != 'X':
                blockers.add(cell)
    
    # Second pass: analyze each blocker's situation
    for blocker_id in blockers:
        # Find the blocker vehicle
        blocker = None
        for v in state.vehicles:
            if v["id"] == blocker_id: #nchofo esq blocker ta3 X 
                blocker = v
                break
        
        if blocker:
            if blocker["orientation"] == 'V':
                # Vertical vehicle must move at least 1 space
                min_moves += 1 #always ki ykon vertical il suffit de bouger une fois
            else:
                # Horizontal vehicle might need 2 moves if trapped
                spaces_before = 0
                spaces_after = 0
                x, y = blocker["x"], blocker["y"]
                
                # Check spaces before
                if x > 0 and state.board[y][x-1] == ' ': #li 9bl blocker vide
                    spaces_before = 1
                    
                # Check spaces after
                end_x = x + blocker["length"]
                if end_x < state.board_width and state.board[y][end_x] == ' ':
                    spaces_after = 1
                
                # If no free space on either side, need at least 2 moves
                if spaces_before + spaces_after == 0: #no place to moove
                    min_moves += 2
                else:
                    min_moves += 1
    
    # Take maximum to ensure admissibility
    return max(h1_value, min_moves)    



def AStar(s, successorsFn, isGoal, h):
    # Priority queue: stores (f, counter, node)
    # counter prevents comparison of nodes when f values are equal
    Open = []
    counter = 0 #in the heap, loukan f values ykounou equal, nverifyiw counter to see chkoun ja 1st
    
    # Track f values for states in Open and Closed
    Open_dict = {}  # state -> (f, node) as heapq is harder when it comes to updating, searching
    Closed = {}  # state -> f
    
    init_node = Node(state=s, parent=None, action=None, g=0)
    init_node.f = h(init_node.state)
    
    heapq.heappush(Open, (init_node.f, counter, init_node)) #list li nhato fiha, what were gonna push
    Open_dict[init_node.state] = (init_node.f, init_node)#kol ma we push nhato f dict
    counter += 1
    
    while len(Open) > 0:
        # Get node with lowest f
        current_f, _, current = heapq.heappop(Open) #when we pop, we get the tuple (f, counter, node)
        
        # Remove from Open_dict
        if current.state in Open_dict:
            del Open_dict[current.state]
        
        if isGoal(current.state):
            return current
        
        Closed[current.state] = current.f
        
        for action, successor in successorsFn(current.state):
            child = Node(state=successor, parent=current, action=action)
            child.g = current.g + 1  # c(current, action, successor) = 1
            child.f = child.g + h(child.state)
            
            # Check if child.state not in Open and not in Closed
            in_open = child.state in Open_dict
            in_closed = child.state in Closed
            
            if not in_open and not in_closed:
                heapq.heappush(Open, (child.f, counter, child))
                Open_dict[child.state] = (child.f, child)
                counter += 1
            
            # If in Open with higher f, replace
            elif in_open:
                old_f, old_node = Open_dict[child.state]
                if child.f < old_f:
                    # Remove old, add new
                    Open_dict[child.state] = (child.f, child)
                    heapq.heappush(Open, (child.f, counter, child))
                    counter += 1
            
            # If in Closed with higher f, reopen
            elif in_closed:
                old_f = Closed[child.state]
                if child.f < old_f:
                    del Closed[child.state]
                    heapq.heappush(Open, (child.f, counter, child))
                    Open_dict[child.state] = (child.f, child)
                    counter += 1
    
    return None
