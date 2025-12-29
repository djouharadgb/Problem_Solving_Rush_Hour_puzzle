from RushHourPuzzle import RushHourPuzzle

class Node:

    def __init__(self, state, parent=None, action=None, g=0, f=0):
        self.state = state #instance of the rush hour puzzle                 
        self.parent = parent #state board li 9blo (la vache qui rit xD) 
        self.action = action    #the action of the parent to get the successor
    

        self.g = g                 
        self.f = f      #fitness function f = g + h          

    def getPath(self): #sequence des etats pour compter le cout 
        path = []
        path = []
        node = self

        while node is not None:
            path.append(node.state)
            node = node.parent
        path.reverse()
        return path


    def getSolution(self):#seqence d'actions pour arriver au but
        actions = []
        node = self
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions
    
    # g is already set, we just need to add the appropriate h
    def setF(self, heuristic_func):

        h = heuristic_func(self.state)
        self.f = self.g + h
        return self.f


