# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo
from tree_Class import *

import random 
import numpy as np
import sys

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else "pathfindingWorld_multiPlayer"
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 15# frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player


def conditionZone(next_row, next_col, wallStates):
    if ((next_row,next_col) not in wallStates) and next_row>0 and next_row<=rowSize and next_col>0 and next_col<=colSize:
         return True
    else: False

def predictHasNext(chemins, next_row, next_col, j, ite):
    for p in range(len(chemins)):
        if ((p!=j)&(len(chemins[p])>ite)):
            print(chemins[p])
            print(ite)
            if (chemins[p][ite-1] == (next_row,next_col)):
                return True
    return False

def hasNext(next_row, next_col, posPlayers, j, chemins, ite):
    for i in range(len(posPlayers)):
        if ((i!=j) & ((next_row,next_col)==posPlayers[i])):
            if predictHasNext(chemins, next_row, next_col, j, ite):
                return True

    return False
    

def majChemin(next_row, next_col,  wallStates, chemins, j, posPlayers):
    wall_tmp =  wallStates.copy()
    for i in range(len(chemins)):
        #si ce n'est pas moi
        #Je verifie que la position d'un joueur ne correspond pas a celui que je veux prendre
        #Si ce n'est cas on creer un nouveau chemin en considerant la position d'un joueur comme etant un mur
        if ((i!=j)&(posPlayers[i]==(next_row, next_col))):
            wall_tmp.append((next_row, next_col))
            
    #On reconstruit l'arbre en considerant la position courante du joueur comme son nouvel origine
    tree = Tree((next_row, next_col), chemins[j][-1])
    return tree.etoile(posPlayers[j][0],posPlayers[j][1],wall_tmp,rowSize, colSize)
            

def main():

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()

    global colSize, rowSize
    colSize = game.spriteBuilder.colsize
    rowSize = game.spriteBuilder.rowsize
    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    print ("Wall states:", wallStates)
    
    #-------------------------------
    # Placement aleatoire des fioles de couleur 
    #-------------------------------
    
    #Exemple de Collision
    tuplePos = [(7, 1),(5, 5),(18, 8)]
    i =0
    
    for o in game.layers['ramassable']: # les rouges puis jaunes puis bleues
    # et on met la fiole qqpart au hasard
        """
        x = random.randint(1,19)
        y = random.randint(1,19)
        while (x,y) in wallStates:
            x = random.randint(1,19)
            y = random.randint(1,19)
        """
        o.set_rowcol(tuplePos[i][0],tuplePos[i][1])
        #o.set_rowcol(x,y)
        game.layers['ramassable'].add(o)
        game.mainiteration()                
        i+=1
        
    print(game.layers['ramassable'])

    
    
    #-------------------------------
    # Initialisation des chemins des joeurs 
    #-------------------------------
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    
    posPlayers = initStates

    chemins = []
    tree_liste = []

    #random.shuffle(goalStates)
    for i in range(nbPlayers):
        tree = Tree(posPlayers[i],goalStates[i])
        print("GOAL STATE DE",i," ::",goalStates[i])
        tree_liste.append(tree)
        chemins.append(tree.etoile(initStates[i][0],initStates[i][1],wallStates,rowSize, colSize))
    
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...

    
    
    for i in range(iterations):
        
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            row,col = posPlayers[j]
    
            if (row,col) != tree_liste[j].but:
                    
                #print("Joueur ",j," ite :: ",i," longueur du chemin = ",len(chemins[j]))

                next_row, next_col = chemins[j][i]
                if (conditionZone(next_row, next_col, wallStates)):
                    
                    #Quelqu'un est sur mon chemin on recree le chemin pour le joueur j
                    if (hasNext(next_row, next_col, posPlayers, j, chemins, i)):
                        chemin_j = majChemin(next_row, next_col,  wallStates, chemins, j, posPlayers)
                        chemins[j] = chemins[j][:i]+chemin_j
                        #print("TESSSSSSSSSSSSST",chemins[j])
                        (next_row, next_col) = chemins[j][i]

                    players[j].set_rowcol(next_row,next_col)
                    print ("pos :", j, next_row,next_col)
                    game.mainiteration()

                    col=next_col
                    row=next_row
                    posPlayers[j]=(row,col)
                    
                # si on a  trouvé un objet on le ramasse
                if (row,col) == tree_liste[j].but:
                    o = players[j].ramasse(game.layers)
                    game.mainiteration()
                    print ("Objet trouvé par le joueur ", j)
                    goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    score[j]+=1
                    #Affectation d'une nouvelle fiole s'il en reste
                    
                    
                    """
                    #Generation d'une nouvelle fiole
                    # et on remet un même objet à un autre endroit
                    x = random.randint(1,19)
                    y = random.randint(1,19)
                    while (x,y) in wallStates:
                        x = random.randint(1,19)
                        y = random.randint(1,19)
                    o.set_rowcol(x,y)
                    goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    game.layers['ramassable'].add(o)
                    game.mainiteration()
                    """
                    
                
            
    print ("scores:", score)
    pygame.quit()
    

if __name__ == '__main__':
    main()
    


