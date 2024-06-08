# AVEC_MODULE START DELETE
class Objet():
    
    def __init__(self,nom,attribut1,attribut2) -> None:
        self.nom = nom
        self.attribut1 = attribut1
        self.attribut2 = attribut2
    
    def get_attribut1(self) :
        return self.attribut1
    
    def get_attribut2(self) :
        return self.attribut2
# SOMME START DELETE  
    def sum(self,<(MODIF)>modif<(/MODIF)>):
        # MODIF START DELETE
        pre_sum =0
        for x in modif:
            pre_sum += x
        # MODIF STOP DELETE
        return self.attribut1+self.attribut2<(MODIF)>+pre_sum<(/MODIF)>
    
    # AFFICHER_SOMME START DELETE
    def afficher_somme(self,<(MODIF)>modif<(/MODIF)>):
        print(f'Score de {self.name} : {self.sum(self,<(MODIF)>modif<(/MODIF)>)}')
    # AFFICHER_SOMME STOP DELETE
# SOMME STOP DELETE
# AVEC_MODULE STOP DELETE