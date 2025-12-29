from RushHourPuzzle import RushHourPuzzle
from Node import Node
from collections import deque
import time


def BFS(s, successorsFn, isGoal):
    
    #We use deque for Open since we need FIFO for open list
    #We use set for closed since we need its items to be unique + fast search

    Open = deque()
    Closed = set()
    
    # We initialise the first node with the state s passée en paramètre
    init_node = Node(state=s, parent=None, action=None, g=0)
    
    if isGoal(init_node.state):
        return init_node
    
    #hna we add the node to, open, and its state to open states
    #Why open states? To make search for if state exists much faster than it would be in deque
    Open.append(init_node)
    Open_states = set([init_node.state]) #set means access direct O(1)
    
    #moving states men open lel closed après parcours
    while len(Open) > 0:
        current = Open.popleft()
        Open_states.remove(current.state)
        Closed.add(current.state)
        
        for action, successor in successorsFn(current.state):
            child = Node(state=successor, parent=current, action=action, g=current.g + 1)
            
            if isGoal(child.state):
                return child
            
            if child.state not in Closed and child.state not in Open_states:
                Open.append(child)
                Open_states.add(child.state)
    
    return None

#How BFS Works:
# So in BFS, we initialise  open and closed lists
# We add the initial state to open
# While open is not empty, we:
# - Remove the first node from open
# - If it's the goal, return it
# - Else, generate its successors
# - For each successor, if it's not in open or closed, add it to open   
# - If khlaset open without finding the goal, return None
