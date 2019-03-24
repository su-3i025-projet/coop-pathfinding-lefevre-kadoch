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

def detect_collision(chemin, dico):
    """
    Detection de collision via le dictionnaire de reservation:
    o Arrivé sur la meme case au meme instant t ou;
    o Permutation de case:
         - unité_1(x,y,t)   = unité_2(x,y,t+1)
         - unité_1(x,y,t+1) = unité_2(x,y,t)
    """
    for t in range(len(chemin)):
        if (t< len(dico)):
            if ((chemin[t] in dico[t+1]) and (chemin[t+1] in dico[t])) or chemin[t] in dico[t]:
                return t
        else:
            return None
    return None

def add_chemin_St(chemin, dico):
    """
    Ajoute un chemin complet dans le dictionnaire des reservations
        - Key   = Temps t
        - Value = Tableau des positions reservées  
    """
    t = 0
    for pos in chemin:
        if t not in dico:
            dico[t] = [pos]
        else:
            dico[t].append(pos)
        t+=1

def cherche_pause(chemin, t, wallStates, rowSize, colSize, dico):
    """
    Retourne une position autre que celles de mon chemin à t-1 et t+1
    En verifiant qu'il ne s'agit pas d'une case contenue dans le tableau des murs
    -> Donc incite le joueur a chercher une case sans revenir en arriere si il y en a une de disponible
    sinon fait machine arriere (dans le pire des cas)
    """
    chemin_a = chemin[t+1] if (len(chemin)>t+1) else None
    chemin_b = chemin[t-1] if (t-1>=0) else None
    x,y = chemin[t]
    print(chemin_a,chemin_b,x,y)
    if ((x+1,y)!=(chemin_a or chemin_b) and conditionZone(x+1,y,wallStates,rowSize, colSize) and (x+1,y) not in dico[t]):
	    return (x+1,y)
    if ((x,y+1)!=(chemin_a or chemin_b) and conditionZone(x,y+1,wallStates,rowSize, colSize) and (x,y+1) not in dico[t]):
        return (x,y+1)
    if ((x-1,y)!=(chemin_a or chemin_b) and conditionZone(x-1,y,wallStates,rowSize, colSize) and (x-1,y) not in dico[t]):
        return (x-1,y)
    if ((x,y-1)!=(chemin_a or chemin_b) and conditionZone(x,y-1,wallStates,rowSize, colSize) and (x,y-1) not in dico[t]):
	    return (x,y-1)
    """
    Enfin si je ne peut pas me deplacer dans les autres direction autre que mon chemin je rebrousse chemin si je le peux sinon je reste
    """

    if (chemin[t-1] not in dico[t]):
        return chemin[t-1]
    else:
        return (x,y)

def enleve_reserv(dico, t, pos):
    """
    Enlever une reservation d'une position (case)
    Permettra à chaque nouveau pas effectué par les agents d'enlever leur reservation 
    afin de laisser les autres agents utiliser le terrain à leur tour (notament s'ils étaient bloqués)
    """
    dico[t].remove(pos)

def ajoute_pos(chemin, pos, t, dico):
    """
    Inserer au temps t dans chemin une position (pour la cooperation)
    """
    chemin.insert(t,pos)

def remove_path(chemin, dico):
    #Enlever toutes les reservations d'un agent via son tableau de chemin du dico
    for t in range (len(chemin)):
        dico[t].remove(chemin[t])

def canPause(wait_pos, chemin):
    """
    Si l'agent reste a cette position est ce qu'il genera un autre agent dans son chemin
    """
    for pos in chemin:
        if (pos==wait_pos):
            return False
    return True

def conditionZone(next_row, next_col, wallStates, rowSize, colSize):
    """
    Est ce qu'au prochain coup je respecte les conditions de jeu
    """
    if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=rowSize and next_col>=0 and next_col<=colSize:
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
                return True
    return False
    

def majChemin(next_row, next_col,  wallStates, chemins, j, posPlayers,rowSize, colSize):
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

def affiche_chemin(chemin, rowSize, colSize, wallStates):
    aff = "|"+"---"*rowSize+"|\n|"
    cpt = 0
    for j in range (colSize): 
        for i in range (rowSize):
            if (i,rowSize-1-j) in chemin:
                aff+=" "+str(cpt)+" "
                cpt+=1
            elif((i,rowSize-1-j) in wallStates):
                aff+="|X|"
            else:
                aff+="   "
        aff+="|\n|"
    aff+="---"*rowSize+"|"
    return aff

wallt = [(0,1),(0,0),(2,1),(2,2),(1,3)]
chemin = [(1,0),(2,0),(3,0)]

dico ={}
add_chemin_St(chemin, dico)
print(dico)
remove_path(chemin,dico)
for t in range(4):
    pause = cherche_pause(chemin, 0, wallt,4,4, dico)
    ajoute_pos(chemin,pause,0,dico)
    print(chemin)
add_chemin_St(chemin, dico)
print(affiche_chemin(chemin,4,4,wallt))
print(dico)
if conditionZone(1,1,wallt,4,4):
    print("TEST :: True")
else: print("TEST :: False")
"""

var = (1,2)
x,y = var
print("X = ",x," Y = ",y)

chm  = [(0,1),(0,0),(1,0)]
chm2 = [(0,0),(1,0),(0,0)]

dico={}

add_chemin_St(chm,dico)
res_value = detect_collision(chm2, dico)
res = ""
if (res_value==None):
    add_chemin_St(chm2,dico)
else: res="Collision à l'instant t="+str(res_value)
print(dico, res)
"""
