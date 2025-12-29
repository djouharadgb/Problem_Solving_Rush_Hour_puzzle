import csv
import copy

class RushHourPuzzle:

    def __init__(self, csv_file=None):
        self.board_height = 0
        self.board_width = 0
        self.vehicles = []   #Liste de dictionnaires qui represente les v
        self.walls = []      #Liste de tuples (x, y) qui represente les obstacles
        self.board = []      #Matrice du board

        if csv_file:
            self.setVehicles(csv_file)
            self.setBoard()

    def setVehicles(self, csv_file):
        with open(csv_file, newline='') as fichier:
            reader = csv.reader(fichier)

            # Ignore les lignes vides psq qd mm il ya une possibilite ykono
            liste = [ligne for ligne in reader if ligne]  

        self.board_height = int(liste[0][0]) #recuperer height
        self.board_width = int(liste[0][1])  #recuperer width

        self.vehicles = []
        self.walls = []

        # Parcourir les lignes suivantes
        for ligne in liste[1:]: #ignoré le premier élément qui rep dim
            # Ignorer les lignes vides
            if not ligne or not ligne[0]:
                continue
            #this step is important in : setting all lists of walls, v    
            # Si c'est un obstacle #
            if ligne[0].startswith('#'):
                x = int(ligne[1]) #cast cHAR->INT
                y = int(ligne[2])
                self.walls.append((x, y))
            else:
                v_id = ligne[0]
                x = int(ligne[1])
                y = int(ligne[2])
                orientation = ligne[3]
                length = int(ligne[4])

                # Créer un dictionnaire pour le véhicule pour faciliter la manipulation later
                vehicle = {
                    "id": v_id,
                    "x": x,
                    "y": y,
                    "orientation": orientation,
                    "length": length
                }
                self.vehicles.append(vehicle)

        return self.vehicles
    
    def setBoard(self):
        # Créer une matrice vide
        self.board = [[' ' for _ in range(self.board_width)] for _ in range(self.board_height)]

        # Placer les obstacles
        for (x, y) in self.walls:
            self.board[y][x] = '#'

        # Placer les vehicules
        for v in self.vehicles:
            x, y = v["x"], v["y"]
            for i in range(v["length"]):
                if v["orientation"] == 'H':
                    self.board[y][x + i] = v["id"] #tjrs we inverse it as cest des cordonnees cartesiennes
                else:
                    self.board[y + i][x] = v["id"]

        return self.board
    
    def displayBoard(self): #affichage organisee de la mat avan PYGAME
        # Ligne horizontale de séparation
        horizontal_line = "+" + "-" * (self.board_width * 4 - 1) + "+"
        
        print("\n" + horizontal_line)
        for i, row in enumerate(self.board):
            # Afficher la ligne avec des séparateurs verticaux
            print("| " + " | ".join(row) + " |")
            # Afficher une ligne de séparation entre les rangées
            if i < self.board_height - 1:
                print("|" + "+".join(["-" * 3 for _ in range(self.board_width)]) + "|")
        print(horizontal_line)

    def isGoal(self):
        for v in self.vehicles:
            if v["id"] == "X": #on retourne un booleen qui indique que isGoal
                return v["x"] == self.board_width - 2 and v["y"] == (self.board_height // 2 - 1)
        return False
    
    def canMove(self, vehicle, direction): #cette fonction nous indique si il peut se deplacer dans une telle pos
        
        # Vérifie si un véhicule peut se déplacer dans une direction,soit up, left, right or down.
        
        x, y = vehicle["x"], vehicle["y"]
        orientation = vehicle["orientation"]
        length = vehicle["length"]
        
        if orientation == 'H' and direction in ['U', 'D']: #lzm ykono hado
            return False
        if orientation == 'V' and direction in ['L', 'R']:
            return False
        
        # Calculer la nouvelle position
        new_x, new_y = x, y
        
        if direction == 'L': #left x-1
            new_x = x - 1
            if new_x < 0: #we reached the wall
                return False
            if self.board[y][new_x] != ' ':
                return False
                #same for others 
        elif direction == 'R':
            new_x = x + 1
            if new_x + length > self.board_width:
                return False
            if self.board[y][new_x + length - 1] != ' ':
                return False
                
        elif direction == 'U':
            new_y = y - 1
            if new_y < 0:
                return False
            if self.board[new_y][x] != ' ':
                return False
                
        elif direction == 'D':
            new_y = y + 1
            if new_y + length > self.board_height:
                return False
            if self.board[new_y + length - 1][x] != ' ':
                return False
        
        return True
            # Déplace un véhicule dans une direction et retourne le nouvel état

    def moveVehicle(self, vehicle_id, direction):
        
        # On crée une copie de l'état actuel d'abord de l'objet
        new_state = copy.deepcopy(self)
        
        # Then search for le véhicule à déplacer
        vehicle_index = None
        for i, v in enumerate(new_state.vehicles):
            if v["id"] == vehicle_id:
                vehicle_index = i #index pour sauvgarder sa pos et confirmer que we found it
                break
        
        if vehicle_index is None:
            return None
#on cree une deep copy qui contient toutw info sur l'objet

        vehicle = new_state.vehicles[vehicle_index] #on cherche lobjet actuel dans sa copie
        
        if direction == 'L':
            vehicle["x"] -= 1#position x  -1
        elif direction == 'R':
            vehicle["x"] += 1#position x  +1
        elif direction == 'U':
            vehicle["y"] -= 1#position y  -1
        elif direction == 'D':
            vehicle["y"] += 1#position y  +1

        new_state.setBoard() # On met à jour le plateau avec la nouvelle position 
        
        return new_state
    
    def successorFunction(self): #we give it a vehicle and it returns the list of successors
    
        successors = []
        
        for vehicle in self.vehicles:
            vehicle_id = vehicle["id"]
            orientation = vehicle["orientation"]
            
            if orientation == 'H':
                directions = ['L', 'R'] #the possible directions li y9dro ymove fihom (all successors)
            else: 
                directions = ['U', 'D']  #the possible directions li y9dro ymove fihom (all successors)
            
            for direction in directions:
                if self.canMove(vehicle, direction):
                    # Créer le nouvel état
                    new_state = self.moveVehicle(vehicle_id, direction)
                    if new_state:
                        # Ajouter l'action et le successeur à la liste
                        action = (vehicle_id, direction)
                        successors.append((action, new_state))
        
        return successors
    
    def __eq__(self, other):

        # ndiro eq because we can't compare les deux états directly since rah tcompari les adresses mémoire
        # Soo we use it to compare the state of each vehicle position in the board between two states

        if not isinstance(other, RushHourPuzzle):
            return False
        
        if len(self.vehicles) != len(other.vehicles):
            return False
        
        for v1 in self.vehicles:
            found = False
            for v2 in other.vehicles:
                if (v1["id"] == v2["id"] and #we compare id, x and y we can't compare directly two different objects 
                    v1["x"] == v2["x"] and 
                    v1["y"] == v2["y"]):
                    found = True
                    break
            if not found:
                return False
        
        return True
    
    def __hash__(self):

        # In order to save the states in les listes open and closed, lazem we name them with unique names, and the best method is using hashing
        # After ma ncryiw one tuple of all vehicle positions in current state, we hash it using python's function
        vehicle_positions = tuple(sorted(
            (v["id"], v["x"], v["y"]) for v in self.vehicles
        ))
        return hash(vehicle_positions)

# this is the best method because hash + eq assurent bli the state is 100% unique