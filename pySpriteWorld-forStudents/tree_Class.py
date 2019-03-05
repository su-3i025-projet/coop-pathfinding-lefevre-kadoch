from math import *
from node_Class import *
import random
import heapq

class Tree:
     
     def __init__(self, coordO, but):
          
          self.origin = Node(0,coordO[0], coordO[1], None)
          #self.frontier = {}
          self.frontier = []
          self.reserve = []
          self.chemin = []
          self.but = but
          
     
     def distMan (self, noeud):
          return abs(noeud.x-self.but[0])+abs(noeud.y-self.but[1]) 
     
     def expansion_voisin(self, tabMurs,rowSize, colSize, noeud):
          """ Rend la liste des voisins du noeud """
          x = noeud.x
          y = noeud.y

          res = []
          
          if ((x+1<rowSize) and ((x+1,y) not in tabMurs)): # droite
               noeudFils = Node(noeud.distO+1, x+1, y, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               
          if ((y+1<colSize) and ((x,y+1)not in tabMurs)): # haut 
               noeudFils = Node(noeud.distO+1, x, y+1, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               
          if ((x-1>0) and ((x-1,y) not in tabMurs)): # gauche
               noeudFils = Node(noeud.distO+1, x-1, y, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               
          if ((y-1>0) and ((x,y-1)not in tabMurs)): # bas
               noeudFils = Node(noeud.distO+1, x, y-1, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)

          return res

          
     def retropropagation(self, node, liste):
          """ Retrouve le parcours du chemin le plus optimale
     dans l'arbre en partantdu fils """
          if (node.parent==None):
               return liste
          else:
               liste.append(node.get_coord())
               return self.retropropagation(node.parent, liste)

     def min_f(self, liste):
          """Renvoie le tuple (n,f),indice avec le f minimum et l'indice associé dans la liste"""
          minf = liste[0][1]
          res = liste[0]
          index_min = 0
          for i in range(len(liste)):
               if liste[i][1] < minf:
                    minf = liste[i][1]
                    res = liste[i]
                    index_min = i
               
          return res,index_min
     
     def isInReserve(self,reserve,noeud):
          for i in range(len(reserve)):
               if noeud.get_coord() == reserve[i].get_coord():
                    return True
          return False

     def etoile(self, x0, y0, tabMurs, rowSize, colSize):
          """Algo de A* """
          
          n0 = Node(0,x0,y0,None)
          dist_tmp = n0.distO+self.distMan(n0)
          self.frontier = [(n0,dist_tmp)]

          self.reserve = []
          best = n0

          while self.frontier != [] and best.get_coord() != self.but :
               (best,min_f),indice = self.min_f(self.frontier)
               self.frontier.pop(indice)

               if self.isInReserve(self.reserve, best) == False:
                    self.reserve.append(best)
                    newNode = self.expansion_voisin(tabMurs, rowSize, colSize, best) # change expansion voisin pour afficher liste
                    for n in newNode :
                         f = n.distO + self.distMan(n)
                         ajout = (n,f)
                         self.frontier.append(ajout)

          #Construction du chemin via la methode retropropagation
          #Necessite d'etre inversé car le chemin est créé de la feuille (fiole) à la racine (position initale)
          return list(reversed(self.retropropagation(best, [])))




          
