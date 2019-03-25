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
import math
    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else "soluce_2"
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5# frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player

def collision(chemin1,chemin2): 
    for pos in chemin1:
        if pos in chemin2:
            print("Position :: ",pos," -> chemin2 : ",chemin2) 
            return True
    return False

def tempsExec(chemins):
    somme = 0
    max_t = len(chemins[0])
    for chemin in chemins:
        if chemin == None:
            return math.inf, math.inf 
        somme+=len(chemin)
        if len(chemin)>max_t:
            max_t = len(chemin)
    return somme, max_t

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
    alea = 0 # default
    if len(sys.argv) == 2:
        alea = int(sys.argv[1])

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
    #•print ("Wall states:", wallStates)
    
    #-------------------------------
    # Placement aleatoire des fioles de couleur 
    #-------------------------------
    
    #Exemple de Collision
    i =0
    
    for o in game.layers['ramassable']: # les rouges puis jaunes puis bleues
    # et on met la fiole qqpart au hasard
        if alea==1:
            x = random.randint(1,colSize-2)
            y = random.randint(1,rowSize-2)
            while (x,y) in wallStates:
                x = random.randint(1,colSize-2)
                y = random.randint(1,rowSize-2)
            
            o.set_rowcol(x,y)
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

    # initialiser liste_joueurs
    liste_joueurs = [i for i in range(nbPlayers)]
    
    sum_ite = 0
    t_max = 0

    while len(liste_joueurs) != 0:
        
        print(liste_joueurs)
        for i in liste_joueurs:
            tree = Tree(posPlayers[i],goalStates[i])
            tree_liste.append(tree)
            chemins[i]=tree.etoile(initStates[i][0],initStates[i][1],wallStates,rowSize, colSize)
    
        passage = []
        joueur = liste_joueurs.pop(0)
        passage.append(joueur)
        wallStates.append(chemins[joueur][-1])

        """
        Creation des differents groupes de passage
        """
        for j2 in liste_joueurs:
            if collision(chemins[joueur],chemins[j2]) == False:
                print("joeur ajouter")
                passage.append(j2)
                liste_joueurs.remove(j2)
                wallStates.append(chemins[j2][-1])

        max_chemin_tmp = [len(chemins[j]) for j in passage]
        chemin_tmp = [chemins[j] for j in passage]
        #On recupere le temps total
        sum_ite_tmp, tmax_tmp = tempsExec(chemin_tmp)

        #Somme des iteration dans chaque groupe de passage + les iterations d'immobilisation des agents
        sum_ite+=sum_ite_tmp+(len(chemin_tmp)*t_max)
        t_max += tmax_tmp

        for i in range(max(max_chemin_tmp)):
            for j in passage:
                row,col = posPlayers[j]
        
                if (row,col) != tree_liste[j].but:
                    
                    next_row, next_col = chemins[j][i]

                    players[j].set_rowcol(next_row,next_col)
                    game.mainiteration()

                    col=next_col
                    row=next_row
                    posPlayers[j]=(row,col)
                        
                    # si on a  trouvé un objet on le ramasse
                    if (row,col) == tree_liste[j].but:
                        o = players[j].ramasse(game.layers)
                        game.mainiteration()
                        print ("Objet trouvé par le joueur ", j)
                        #goalStates.remove((row,col)) # on enlève ce goalState de la liste
                        score[j]+=1
                        #Affectation d'une nouvelle fiole s'il en reste
                        
                
    print ("scores:", score)
    print("Nombre Total d'iteration ::", sum_ite, " Temps total :: ",t_max)
    pygame.quit()
    

if __name__ == '__main__':
    main()
    
