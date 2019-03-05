class Node:
    def __init__(self, distO, x, y,parent=None):
        """
        //IMPLEMENTATION DE LA CLASSE NOEUD//
        """
        self.parent  = parent
        self.noeudsFils = []
        self.distO = distO
        self.x = x
        self.y = y
	
    def __str__(self, level=0):
        ret = "|\t"*(1 if(level>0)else 0)*level+"├───────"*(1 if(level>0)else 0)+repr(self)+"\n"
        for child in self.noeudsFils:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return self.afficheNoeud()

    def setH (self, h):
        self.h = h

    def get_f(self):
        return self.h + self.distO

    def afficheNoeud(self):
        return "("+str(self.x)+","+str(self.y)+") :: distO = "+str(self.distO)

    def ajouterEnfant(self, enfant):
        """
        Ajout d'un noeud enfant a la liste des noeuds fils
        """
        self.noeudsFils.append(enfant)

    def getParent(self):
        return self.parent

    def getAction(self):
        return self.action

    def get_coord(self):
        return (self.x,self.y)

