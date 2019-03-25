from math import *
from node_Class import *
import random
import heapq
import time

class Tree_space_time:
     
     def __init__(self, coordO, but):
          
          self.origin = Node(0,coordO[0], coordO[1], None)
          self.frontier = []
          self.reserve = []
          self.chemin = []
          self.but = but
          
     
     def collision(self, dico, temps_after,pos_before, pos_after):
          """
          Detecte les collisions:
               - Permutation de case
                    Si dans la case ou je vais il y a un autre agent qui va dans ma case precedente
               - Arrivé sur une meme case
                    Si je vais une case qui est deja reservé au meme instant
          """
          # IL manque cette condition :  or (temps_after in dico[pos_before] cependant dans certaine condition le elle amene a faire quand meme des collisions
          if ((temps_after in dico[pos_before]) and (temps_after-1 in dico[pos_after])) or (temps_after in dico[pos_after]):
               return True
          else: return False

     def agent_wall(self,dico,pos,t):
          """
          Verifie s'il y a un agent fixe à la futur position du joueur
               - True s'il n'y en a pas
               - False s'il y en a bien un 
          """
          if len(dico[pos])==0:
               return True
          else:
               if t < min(dico[pos])-1:
                    return True
               else:
                    return False

     def agent_escape(self, dico, pos, t):
          """
          Verifie s'il y a un agent en fuite dont il faudrait laisser passer
               - True s'il n'y en a pas
               - False s'il y en a bien un 
          """
          if len(dico[pos])==0:
               return True
          else:
               if t > max(dico[pos])+1:
                    return True
               else:
                    return False

     def distMan (self, noeud):
          """
          Calcul de la distance de Manhattan entre la position du noeud et le but
          """
          return abs(noeud.x-self.but[0])+abs(noeud.y-self.but[1]) 
               
     def expansion_voisin(self, tabMurs, dico, agentFixe, escape, temps,colSize, rowSize, noeud):
          """ Rend la liste des voisins potentiels du noeud pour le calcul de A*
          
          Pour ce faire:
               - Verifier que la case n'est pas un mur
               - Verifier que cette meme case n'a pas deja étée révervée et quelle ne générera aucune collision
               - Verifier si un autre agent devenu immobile apres la fin de son execution ne gene pas
          
          Si aucune des cases ne verifient ces conditions on retourne la position initiale du noeud 
          """
          x = noeud.x
          y = noeud.y
          pos = (x,y)

          canMove = False
          res = []
          
          if ((x+1<rowSize) and ((x+1,y) not in tabMurs)) and (not self.collision(dico,temps,pos,(x+1,y))) and self.agent_wall(agentFixe,(x+1,y),temps) and self.agent_escape(escape,(x+1,y),temps): # droite
               noeudFils = Node(noeud.distO+1, x+1, y, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               canMove = True
               
          if ((y+1<colSize) and ((x,y+1)not in tabMurs)) and (not self.collision(dico,temps,pos,(x,y+1))) and self.agent_wall(agentFixe,(x,y+1),temps) and self.agent_escape(escape,(x,y+1),temps): # haut 
               noeudFils = Node(noeud.distO+1, x, y+1, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               canMove = True

          if ((x-1>=0) and ((x-1,y) not in tabMurs))and (not self.collision(dico,temps,pos,(x-1,y))) and self.agent_wall(agentFixe,(x-1,y),temps) and self.agent_escape(escape,(x-1,y),temps): # gauche
               noeudFils = Node(noeud.distO+1, x-1, y, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               canMove = True

          if ((y-1>=0) and ((x,y-1)not in tabMurs)) and (not self.collision(dico,temps,pos,(x,y-1))) and self.agent_wall(agentFixe,(x,y-1),temps) and  self.agent_escape(escape,(x,y-1),temps): # bas
               noeudFils = Node(noeud.distO+1, x, y-1, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)
               canMove = True

          elif (canMove == False) :
               """
               Si on ne peut pas bouger a cet instant t, on fait une pause en créant un
               noeud fils qui a la meme position qu'avant l'expansion
               """
               val = 1
               #Si l'agent est bloqué par le chemin d'un autre agent et que sa position courante generera une collision au prochain tour
               #Donner un coup important au noeud pour qu'il ne soit pas revister par l'algo A*
               if (self.collision(dico,temps,pos,(x,y))):
                    val = len(dico)
               print("MISE EN ATTENTE POUR LAISSER PASSER UN AGENT")
               noeudFils = Node(noeud.distO+val, x, y, noeud)
               noeudFils.setH(self.distMan (noeudFils))
               res.append(noeudFils)
               noeud.ajouterEnfant(noeudFils)

          return res
     
          
     def retropropagation(self, node, liste):
          """ Retrouve le parcours du chemin le plus optimale
          dans l'arbre en partantdu fils """
          if (node.parent==None):
               liste.append(node.get_coord())
               return liste
          else:
               liste.append(node.get_coord())
               return self.retropropagation(node.parent, liste)

     def ajout_chemin_dico(self,chemin, dico):
         """
         Ajoute un chemin complet dans le dictionnaire des reservations
             - Value   = tableau des temps t reservés
             - Key     = reservation de la position   
         """
         t = 0
         
         for pos in range(len(chemin)):
              dico[chemin[pos]].append(t)
              t+=1
              if pos == len(chemin)-1:
                   for _ in range(len(dico)):
                        t+=1
                        dico[chemin[pos]].append(t)
                        dico[chemin[pos]].append(t+1)


     def min_f(self, liste):
          """
          Renvoie le tuple (n,f),indice avec le f minimum et l'indice associé dans la liste
          """
          minf = liste[0][1]
          res = liste[0]
          index_min = 0
          if (liste[0]==None) : print("PROBLEM HERE!!!")
          for i in range(len(liste)):
               if liste[i][1] < minf:
                    minf = liste[i][1]
                    res = liste[i]
                    index_min = i
               
          return res,index_min
     
     def addFrontier(self, frontier, reserve, node):
          """
          Ajoute un couple (noeud,Dist_f) a la frontiere:
               - si noeud est deja present avec une valeur de f plus petite ne pas l'ajouter
               - sinon , si noeud deja present mais valeur f plus petite ...
          """
          f = node.get_f()
          for elem in frontier:
               n_elem,nf = elem
               if n_elem.get_coord() == node.get_coord():
                    if f<nf:
                         #reserve.append(frontier.remove(elem))
                         frontier.append((node,f))
                         return True
                    else:
                         return False
          frontier.append((node,f))
          return True

     def isInReserve(self,reserve,noeud):
          if noeud == None:
               return True
          for i in range(len(reserve)):
               if (noeud.get_coord() == reserve[i].get_coord()) and (noeud.distO == reserve[i].distO) :
                    return True
          return False


     def etoile(self, x0, y0, tabMurs, dico, agentFixe,escape, rowSize, colSize):
          """Algo de A* """
     
          #print("POSITION INTIALE :: ", (x0,y0))
          n0 = Node(0,x0,y0,None)
          dist_tmp = n0.distO+self.distMan(n0)
          self.frontier = [(n0,dist_tmp)]

          self.reserve = []
          best = n0

          while self.frontier != [] and best.get_coord() != self.but :

               (best,_),indice = self.min_f(self.frontier)
               self.frontier.pop(indice)
               temps = best.distO

               if best.distO > len(dico)**3:
                    print("BREAK IMPOSSIBLE DE PASSER")
                    #break
                    return None
               """
               Ceci permet de gerer les cas ou l'agent se serait bloqué dans un chemin sans issue
               par un autre agent qui aurait deja reservé les places. Il faut donc chercher une autre solution
               """
               """
               while (temps==dico[best.get_coord()]):
                    (best,_),indice = self.min_f(self.frontier)
                    self.frontier.pop(indice)
                    temps = best.distO
               """
               if self.isInReserve(self.reserve, best) == False:
                    self.reserve.append(best)
                    newNode = self.expansion_voisin(tabMurs, dico, agentFixe, escape, temps+1,rowSize, colSize, best) # change expansion voisin pour afficher liste
                    #print ("\nEXPANSION VOISIN -> ",best)
                    for n in newNode :
                         #self.frontier.append((n,n.get_f()))
                         self.addFrontier(self.frontier,self.reserve, n)

          #Construction du chemin via la methode retropropagation
          #Necessite d'etre inversé car le chemin est créé de la feuille (fiole) à la racine (position initale)
          
          #Si on a pas laisser fuir un agent 
          if len(dico[best.get_coord()])>0 and best.distO <= max(dico[best.get_coord()]):
               return None
          
          final = self.retropropagation(best, [])
          final = list(reversed(final))

          #Ajout du chemin au dictionnaire des reservations 
          self.ajout_chemin_dico(final,dico)

          #On ajoute à la position l'instant terminal t pour considerer le joueur comme un mur à partir de ce moment la
          agentFixe[final[-1]].append(len(final)-1)
          return final
