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
from tree_escape import *

import math
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
    name = _boardname if _boardname is not None else "test_partage_chemin2"
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5# frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player

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

def createSpaceTime(colSize, rowSize):
    """ crée un dictionnaire avec comme clé un case, et comme valeur une liste des temps reservés.
    colSize : taille d'une colonne
    rowSize : taille d'une ligne
    """
    space_time = {}

    #ATTENTION REGLER S'IL FAUT METTRE EN ABSCISSE LES COLONNES OU EN ORDONNE 

    for x in range(colSize):
        for y in range(rowSize):
            temporel = []
            space_time[(x,y)]=temporel
        
    return space_time


def perms(liste):
    """
    Obtenir toutes les combinaisons possibles d'un tableau de valeur
    Le nombre de combinaison sera len(liste)! 
    """
    if len(liste)==1:
        return [liste]
    else:
        all = []
        for line in perms(liste[:-1]):
            for i in range(len(liste)):
                all += [line[:i] + liste[-1:] + line[i:]]
        return all


def main():

    #for arg in sys.argv:
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])

    init()

    print("\n\n")

    global colSize, rowSize
    colSize = game.spriteBuilder.colsize
    rowSize = game.spriteBuilder.rowsize
    print("\nTAILLE DU MONDE :: ", colSize,"x",rowSize, "Case\n")
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    score = [0]*nbPlayers
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    #print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    #-------------------------------
    # Placement aleatoire des fioles de couleur 
    #-------------------------------
    
    #Exemple de Collision
    #tuplePos = [(7, 1),(5, 5),(18, 8)]
    i =0
    
    for o in game.layers['ramassable']: # les rouges puis jaunes puis bleues
    # et on met la fiole qqpart au hasard
        
        x = random.randint(0,rowSize-1)
        y = random.randint(0,colSize-1)
        while (x,y) in wallStates:
            x = random.randint(0,rowSize-1)
            y = random.randint(0,colSize-1)
        
        #o.set_rowcol(tuplePos[i][0],tuplePos[i][1])
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
    #random.shuffle(posPlayers)
    chemins = []
    chemins_tmp = []
    tree_liste = []
    dico = createSpaceTime(colSize, rowSize)
    goalStates = list(reversed(goalStates))
    
    if len(goalStates)>nbPlayers:
        iter = nbPlayers
    else: 
        iter = len(goalStates)

    """
    RECHERCHE DU MEILLEUR ORDRE DE CREATION DES CHEMINS
    AFIN D'AVOIR LE COUP GENERAL MINIMUM
    """

    #Inititalisation de tous les ordres possibles
    passage = [i for i in range(iter)]
    liste_passage = perms(passage)

    agentFixe = createSpaceTime(colSize, rowSize)
    dico_escape = createSpaceTime(colSize, rowSize)

    #Initialisation du minimum
    for i in passage:
        tree = Tree_space_time(posPlayers[i],goalStates[i])
        tree_liste.append(tree)
        chemins.append(tree.etoile(initStates[i][0],initStates[i][1],wallStates, dico, agentFixe,dico_escape, rowSize, colSize))
    
    chemin_opti = chemins
    passage_opti = passage
    liste_but = [tree_liste[i].but for i in passage]


    #Recherche du passage minimisant le coup total
    for chm in liste_passage:

            dico_tmp  = createSpaceTime(colSize, rowSize)
            agentFixe = createSpaceTime(colSize, rowSize)
            dico_escape = createSpaceTime(colSize, rowSize)
            agent_escape = []
            list_dico_escp = []
            tree_liste.clear()
            chemins_tmp.clear()

            while i < len(chm):
            #for i in chm:
                #tree = Tree_space_time(posPlayers[i],goalStates[i])
                #chemin_tree = tree.etoile(initStates[i][0],initStates[i][1],wallStates, dico_tmp, agentFixe,rowSize, colSize)
                #tree_liste.append(tree)
                #chemins_tmp.append(chemin_tree)
                if (chm[i] not in agent_escape):    
                    tree = Tree_space_time(posPlayers[chm[i]],goalStates[chm[i]])
                    tree_liste.append(tree)
                    chemin_tree = tree.etoile(initStates[chm[i]][0],initStates[chm[i]][1],wallStates, dico_tmp, agentFixe,dico_escape,rowSize, colSize)
                    
                    #L'agent n'a pas reussi à passer à cause d'un autre
                    #il faut tout recalculer en prennant en consideration la fuite de cet agent
                    if (chemin_tree == None):
                        tree_liste.clear()
                        chemins_tmp.clear()
                        agent_escape.append(chm[i])
                        dico_tmp  = createSpaceTime(colSize, rowSize)
                        agentFixe = createSpaceTime(colSize, rowSize)
                        #j'ajoute l'etat courant du dico_escape pour la reconstruction des chemins
                        list_dico_escp.append(dico_escape.copy())
                        chemin_tree = tree.etoile(initStates[chm[i]][0],initStates[chm[i]][1],wallStates, dico_tmp, agentFixe, dico_escape, rowSize, colSize)
                        tree.ajout_chemin_dico(chemin_tree, dico_escape)
                        i = 0
                else:
                    #On recupere le dictionnaire des fuites au moment ou le joueur i à detecter le besoin d'en avoir une
                    #On construi alors le chemion a ce moment la 
                    dico_esc = list_dico_escp[agent_escape.index(chm[i])]
                    chemin_tree = tree.etoile(initStates[chm[i]][0],initStates[chm[i]][1],wallStates, dico_tmp, agentFixe, dico_esc,rowSize, colSize)

                chemins_tmp.append(chemin_tree)
                i+=1

            if tempsExec(chemins_tmp)<tempsExec(chemin_opti):
                chemin_opti = chemins_tmp
                passage_opti = chm
                dico = dico_tmp
                liste_but = [tree_liste[i].but for i in chm]
                
    chemins = chemin_opti
    print("Ordre de passage optimisé ::",passage_opti)
    #print(chemins,passage)

    print("--------------------------\nCHEMINS DES AGENTS CONSTRUIT\n--------------------------\n")

    print("\n",chemins,"\n")

    i=0
    while iter!=sum(score):

        for j in passage_opti:

            row,col = posPlayers[j]

            if (row,col) != liste_but[j]:

                next_row, next_col = chemins[j][i]
                players[j].set_rowcol(next_row,next_col)
                game.mainiteration()
                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
                        
                # si on a  trouvé un objet on le ramasse
                if (row,col) == liste_but[j]:
                    o = players[j].ramasse(game.layers)
                    game.mainiteration()
                    print ("Objet trouvé par le joueur ", j)
                    #goalStates.remove((row,col)) # on enlève ce goalState de la liste
                    score[j]+=1
                    #Affectation d'une nouvelle fiole s'il en reste
                        
                    
                    #Generation d'une nouvelle fiole
                    # et on remet un même objet à un autre endroit
                    #x = random.randint(1,19)
                    #y = random.randint(1,19)
                    #while (x,y) in wallStates:
                    #    x = random.randint(1,19)
                    #    y = random.randint(1,19)
                    #o.set_rowcol(x,y)
                    #goalStates.append((x,y)) # on ajoute ce nouveau goalState
                    #game.layers['ramassable'].add(o)
                    #game.mainiteration()
            else:
                if score[j]==0:
                    players[j].ramasse(game.layers)
                    game.mainiteration()
                    print ("Objet trouvé par le joueur ", j)
                    score[j]+=1
            
        i+=1

    time,max_t = tempsExec(chemins)
    print ("scores:", score,"\nExecuter avec un total de : ",time," iterations -> et un temps de : ",max_t,"pour ",len(chemins), "joeur(s)")
    pygame.quit()

if __name__ == '__main__':
    main()
    

