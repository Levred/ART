import os
import re
from random import randint
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory

import xcfilter as xcf
from consistency import check_consistency
from exceptions import *
from marker_ui import MarkerFrame , TkFileText, ErrorWindow
from utils.z3_parser import comma_splitting
from visitor_ui import VisitorUI
from vtamparser import grammar


def afficher_message(message:str):
    '''
    Afficher un message dans la console de l'interface graphique
    
    Parametres :
    :param message: message à montrer
    :type message: string
    '''
    console.config(state='normal')
    console.insert(INSERT,message)
    console.yview('scroll',len(console.get('0.0',INSERT)),'units')
    console.config(state='disabled')


def open_dir() :
    '''    Ouvrir un dossier source    '''
    #On demande à l'utilisateur l'adresse du fichier
    dossier = askdirectory(title='Ouvrir un dossier')
    if not dossier:
        # Si aucun fichier désigné on annule
        return

    afficher_message(f'------------- Ouverture de {dossier.split("/")[-1]}\n')
    #Récuppèration des parametres : liste des fichier, cohérence et variantes
    files = open_param(dossier)

    #Ouverture des fichiers
    for file in files:
        ouvrir_fichier(file)
    afficher_message(f'------------- {dossier.split("/")[-1]} ouvert\n')


def open_param(dossier:str) -> list[str]:
    ''' 
    Touver et appliquer les parmametres du dossier
    
    :param dossier: adresse du dossier sur l'ordinateur
    :type dossier: str
    
    :return liste_fichiers: liste des fichiers à ouvrir
    :type liste_fichiers: list[str]
    
    '''
    #Récupèration du contenu du dossier
    fichiers = os.listdir(dossier)
    
    coherence = False   #Booléen indiquant si le fichier de cohérence à été trouvé 
    liste = False       #Booléen indiquant si la liste des fichiers à traiter à été trouvée
    #Recherche de fichiers .var .list ou .marqueur
    for f in fichiers :
        #Récupèration de l'extension du fichier
        extension = f.split('.')[-1]
        if extension == 'var':
            liste_marqueurs.change_file(os.path.join(dossier, f))
        elif extension == 'marker':
            change_consistency(os.path.join(dossier, f))
            coherence = True
        elif extension == 'list':
            liste_fichiers = ouvrir_liste(dossier,f)
            liste = True
    if not coherence :
        force.set(True)
    if not liste :
        return trouver_fichiers(dossier)
    return liste_fichiers


def trouver_fichiers(dossier:str):
    '''
    Trouver les fichiers à traiter en fonction de leur extension
    
    :param dossier: addresse du dossier dans lequel chercher
    :type dossier: str

    :return liste_fichier: liste des fichier à traiter
    :type liste_fichier: list[str]
    '''
    #Récupèration de la liste des éléments du dossier
    flist = os.listdir(dossier)
    majoritaire = {}    #Dictionnaire des occurences des extentions
    
    #Parcours des éléments du fichiers en ignorant les .var/list/marker pour compter les occurences
    for f in flist:
        extension = f.split('.')[-1]
        if extension not in ['var','marker','list'] :
            if extension in majoritaire.keys():
                majoritaire[extension] += 1
            else:
               majoritaire[extension] = 1
    
    #Détermination l'extension la plus présente
    max = 0 
    extension = ''
    for ext in majoritaire.keys():
        if majoritaire[ext] > max :
            max = majoritaire[ext]
            extension = ext
    
    #Construction de la liste des fichiers à traiter
    liste_fichiers = []
    for f in flist:
        ext = f.split('.')[-1]
        if ext == extension :
            chemin_fichier = os.path.join(dossier,f)
            liste_fichiers.append(chemin_fichier)
            splite=os.sep
            console.insert(INSERT,f'{f.split(splite)[-1]} ouvert\n')

    return liste_fichiers


def ouvrir_liste(dossier : str,fichier_liste :str):
    '''
    Réccupérer la liste des fichiers à ouvrir à partir d'un *.list

    :param dossier: dossiers dans lequel on se trouve
    :type dossier: string
    :param fichier_liste: fichier en .list
    :type fichier_liste: str
    '''
    with open(os.sep.join([dossier,fichier_liste]), 'r') as file:
        liste_fichiers = []
        #Parcours de chaque ligne à la recherche de noms de fichiers à ouvrir
        for ligne in file:
            ligne = ligne.strip().split()
            for vfile in ligne:
                file_path = os.path.join(dossier,vfile)
                if os.path.isfile(file_path):
                    if not file_path in liste_fichiers :
                        liste_fichiers.append(file_path)
                        sep=os.sep
                        afficher_message(f'{vfile.split(sep)[-1]} ouvert\n')
                else:
                    print(f'{file_path} n\'est pas un fichier ou n\'existe pas')
                    afficher_message(f'WARNING : {vfile} est dans la liste mais n\'est pas un fichier ou n\'existe pas\n')
        return liste_fichiers


def ouvrir_fichier(nouveau_fichier: str = None):
    '''
    Ouvrir un fichier et l'fficher

    Param:
    :param nouveau_fichier: addresse du fichier à afficher si non précisé on le demande à l'utilisateur
    :type nouveau_fichier: str
    '''

    if nouveau_fichier == None :
        #Demande un fichier à l'utilisateur
        nouveau_fichier = askopenfilename(filetypes=[("All Files", "*.*")],title='Ouvrir un modèle')
       
    if not nouveau_fichier:
        #Si aucun fichier n'est demandé on annule
        return

    #Ouverture du fichier et nouvelle fenêtre
    global fichier_actif
    if not nouveau_fichier in [fichier.nom_fichier for fichier in fichiers_ouverts] :
        fichier_actif = nouveau_fichier
        fichiers_ouverts.append(TkFileText(fenetres,fichier_actif.replace('/',os.sep),liste_marqueurs,cadre_texte))
        fichiers_ouverts[-1].set_func(lambda : appliquer_marqueur(nouveau_fichier))
        fichiers_ouverts[-1].grid(column=len(fichiers_ouverts)-1,row=0)

    
    #Clear the previous checkbutton
    liste_marqueurs.reset_buttons()
    
    appliquer_marqueur(fichier_actif)


def appliquer_marqueur(template : str):
    '''
    Appliquer les marqueurs à un fichier
    Param : 
    :param template: fichier modèle
    :type template: str
    '''
    #On applique cette fonction au cases à cocher des marqueurs
    liste_marqueurs.set_func(lambda : appliquer_marqueur(template))

    #On passe le cadre de texte en mode écriture et on le vide
    cadre_texte.config(state='normal')
    cadre_texte.delete('0.0',END)

    #On visite le fichier avec la grammaire
    templ = open(template,'r',encoding='utf-8')
    tree = grammar.parse(templ.read())
    v = VisitorUI(cadre_texte,liste_marqueurs)
    tagged_text = v.visit(tree)
    v.read_text(tagged_text)
    templ.close()

    
    #On récupère l'état des marqeurs
    marqueurs = liste_marqueurs.get_states()
    
    #On affiche le résultat
    try :
        #Vérification de la cohérence des marqueurs
        check_consistency(marqueurs, [fichier_coherence.get()], force.get(), ignore.get())

        if not ignore.get() :
            #On applique les déductions
            for marqueur in marqueurs.keys() :
                if marqueurs[marqueur]:
                    liste_marqueurs.buttons[marqueur].state(['!alternate','selected'])
                else:
                    liste_marqueurs.buttons[marqueur].state(['alternate','!selected'])
    except IncorrectVerificationFile :
        afficher_message('ERROR : The file is NOT satisfiable (UNSAT) with the given arguments.\n')
        ErrorWindow('ERROR : The file is NOT satisfiable (UNSAT) with the given arguments.\n')

    # On repasse le cadre texte en mode figé
    cadre_texte.config(state='disabled')


def afficher_contraintes():
    '''
    Lire les contraintes et les affichers sur l'interface
    '''

    def lire_arg(arg : str) -> str :
        '''
        Lire un argument et le transformer dans une forme plus naturelle

        Ex: Or(MARKER1,MARKER2) --> MARKER1 or MARKER2
        
        Param:
        :param arg: agument (Ex: 'MARKER1', 'Or(MARKER1,MARKER2)', 'And(...)', 'Not(MARKER)')
        :type arg: str

        Return:
        :return arg: argurment transformé (Ex: 'MARKER1', 'MARKER1 or MARKER2',...)
        :type arg: str        
        '''
        if 'Not' in arg :
            f = re.match('Not\((?P<arg>.*)\)',arg)
            return f"not {lire_arg(f.group('arg'))}"
        else :
            f = re.match('(?P<op>.*?)\((?P<a>.*)\).*',arg)
            if f:
                args = comma_splitting(f.group('a'))
                return f"{lire_arg(args[0])} {f.group('op').lower().strip()} {lire_arg(args[1])}"
            else :
                return arg.strip()


    if fichier_coherence.get() == '':
        force.set(True)
        return    

    with open(fichier_coherence.get(),'r') as coherence :
        #Suppression des anciennes contraintes
        implies.set('')

        #Lecture du fichier
        for ligne in coherence:

            #Vérification de la forme de la ligne
            ligne = re.match('Implies\((?P<a>.*)\).*',ligne)
            if ligne :
                #transformation de la ligne
                args = comma_splitting(ligne.group('a'))
                implies.set(implies.get()+f"{lire_arg(args[0])} --> {lire_arg(args[1])}\n")
            else :
                implies.set('Fichier de cohérence incorrect !\nCochez \'Forcer la génération\' pour ignorer cette erreur ou changez de fichier de cohérence')
                return
        force.set(False)


def change_consistency(fichier=None):
    '''
    Changer le fichier de cohérence
    
    :param fichier: nom du nouveau fichier de coherence
    :type fichier: str
    '''
    if fichier == None :
        fichier_coherence.set(askopenfilename(filetypes=[("Consistency Files", "*.marker")],title='Ouvrir un fichier de cohérence'))
    else :
        fichier_coherence.set(fichier)
    #Affichage des contraintes
    afficher_contraintes()


def export_fichier(filepath: str = None):
    '''
    Exporter le fichier actuel
    
    :param filepath: nom du nouveau fichier
    :type filepath: str
    '''
    if filepath == None :
        filepath = asksaveasfilename(filetypes=[("All Files", "*.*")],title='Sauvegarder le résultat')
    
    if not filepath:
        return

    with open(filepath, "w") as file:
        #Application des marqueurs
        xcf.main(fichier_actif,filepath,liste_marqueurs.get_states(),[fichier_coherence.get()],force.get(),ignore.get())


def export_dossier():
    '''
    Exporter le dossier actuel
    '''
    dirpath = askdirectory(title='Exporter le dossier actuel',mustexist=False)

    if not dirpath:
        return
    #Exportation de chaque fichier dans le nouveau dossier
    for fichier in fichiers_ouverts:
        global fichier_actif
        fichier_actif = fichier.nom_fichier
        export_fichier(str(os.path.join(dirpath,fichier_actif.split(sep=os.sep)[-1])))
    fichier_trace(dirpath)

def fichier_trace(dirpath):
    with open(os.path.join(dirpath,'resultat.txt'),'w') as result :
        txt = 'MARQUEURS UTILISES\n'
        for marqueur,state in liste_marqueurs.get_states().items() :
            if state:
                txt += '\t+'+marqueur+'\n'
            else :
                txt += '\t-'+marqueur+'\n'
        result.write(txt)


if __name__ == '__main__' :
    #Création de la fenètre
    vtamGUI = Tk()
    vtamGUI.title("VTAM")

    #Création et ajout des différents widget

    ###Barre inferieure (paramètres de cohérence et console)
    bottom = Frame(vtamGUI)
    bottom.pack(side=BOTTOM,fill=X)

    #Paramètres de cohérence
    check = Frame(bottom)
    check.pack(side=LEFT)
    #Console de l'interface
    console = Text(bottom,height=5,wrap='word')
    console.pack(side=RIGHT,fill=X)
    
    ###Barre latérale (liste des marqueurs, affichage des contraintes)
    liste_marqueurs = MarkerFrame(vtamGUI,console)
    liste_marqueurs.pack(side = LEFT,fill=Y)
    
    #Affichage des contraintes
    contraites = Frame(liste_marqueurs) 
    contraites.grid(column=0,row=0,sticky=NW)

    ###Barre supèrieure (boutons de gestion des fichiers)
    bouttons_fichier = Frame(vtamGUI)    
    bouttons_fichier.pack(side=TOP,anchor=W)
    
    ###Barre des noms de fichiers/sous fenêtres
    fenetres= Frame(vtamGUI)
    fenetres.pack(fill='x',side=TOP)
    fichiers_ouverts = []

    #Fichier contenant la coherance
    global fichier_coherence                                
    fichier_coherence = StringVar(check,'')

    #Paramêtres de cohérence
    force = BooleanVar()
    ignore = BooleanVar()
    fichier_actif = None

    #Initialisation de l'affichage des contraintes
    implies = StringVar(contraites)
    afficher_contraintes()

    label_coherence = Label(contraites,textvariable=implies,justify='left')
    label_coherence.pack()

    #Creation du cadre texte
    cadre_texte = Text(vtamGUI,font= ('Arial', 9))
    cadre_texte.pack(expand=True,fill='both')

    #Créartion des boutons de gestion de fichiers
    bouton_ouvrir_dos = Button(bouttons_fichier,text='Ouvrir un dossier',command=open_dir)
    bouton_ouvrir_fichier = Button(bouttons_fichier, text= 'Ouvrir un fichier', command= ouvrir_fichier)
    bouton_export_fichier = Button(bouttons_fichier, text="Exporter le fichier", command=export_fichier)
    bouton_export_dos = Button(bouttons_fichier,text='Exporter le dossier', command=export_dossier)

    #Création des widgets de gestions de coherance
    bouton_fichier_coherance = Button(check,text='Changer le fichier de cohérence',command= change_consistency)
    check_force = ttk.Checkbutton(check,text='Forcer la génération',variable=force)
    check_ignore_deduction = ttk.Checkbutton(check,text = 'Ignorer les déduction',variable=ignore)
    chemin_coherance = Label(check,textvariable=fichier_coherence)

    #Ajouts des widgets à la fenêtre
    bouton_ouvrir_fichier.grid(column=0,row=0,sticky=W)
    bouton_export_fichier.grid(column=1,row=0,sticky=W)
    bouton_ouvrir_dos.grid(column=2,row=0,sticky=W)
    bouton_export_dos.grid(column=3,row=0,sticky=W)

    bouton_fichier_coherance.grid(column=1,row=0,sticky=E)
    chemin_coherance.grid(column=1,row=1,sticky=E)

    check_force.grid(column=0,row=0,sticky=W)
    check_ignore_deduction.grid(column=0,row=1,sticky=W)

    cadre_texte.insert(INSERT,'Ouvrez un modèle pour commencer')
    cadre_texte.config(state='disabled')

    #Lancement de la fenêtre
    vtamGUI.mainloop()