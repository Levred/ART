from random import randint
# AVEC_MODULE START DELETE
from ex_module1 import Objet
# AVEC_MODULE STOP DELETE

# not AVEC_MODULE START DELETE
def creer_objet(nom,attribut1,attrbut2):
    objet = [nom,attribut1,attrbut2]
# SOMME START DELETE
def sum(objet,<(MODIF)>modif<(/MODIF)>):
    s = 0
    for i in modif:
        s+= i
    
    for i in objet[1:] :
        s+= i
    
    return s

# SOMME STOP DELETE
# AFFICHER_SOMME START DELETE
def afficher_somme(objet,<(MODIF)>modif<(/MODIF)>):
    print(f'Score de {objet[0]} : {sum(objet,<(MODIF)>modif<(/MODIF)>)}')

#AFFICHER_SOMME STOP DELETE
# not AVEC_MODULE STOP DELETE x

objets =  []
for nom in ['1','2','3','4']:
    objets.append(<(not AVEC_MODULE)>creer_objet<(/not AVEC_MODULE)><(AVEC_MODULE)>Objet<(/AVEC_MODULE)>(nom,randint(0,10),randint(0,10)))
# AFFICHER_SOMME START DELETE
for objet in objets:
    <(AVEC_MODULE)>objet.<(/AVEC_MODULE)>afficher_somme(objet,<(MODIF)>-3<(/MODIF)>)
# AFFICHER_SOMME STOP DELETE 