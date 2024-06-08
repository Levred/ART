import colorsys
from random import randint,uniform
import os
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from vtamparser.var_grammar import parse as grammar_parse
from vtamparser.var_visitor import VarVisitor
from utils.parse_markers import parse
from exceptions import BadVariantFile

class MarkerFrame(Frame) :
    '''
    Type de structure permettant à l'utilisateur de manipuler les marqueurs et les variantes \n
    Le placement des widget en son sein est géré par .grid() et uniquement sur la colonne 0:\n
     - row = 0 est laissé vide pour un eventuel rappel des propriétés de cohérences \n
     - row = 1 contient la sous-strucure qui gère les variantes \n
     - row = 2 contient le bouton de remise à zéro des marqueurs (remise à l'état "non précisé") \n
     - row = 3 - ... contient les différentes cases à cocher des marqueurs 
    
    Fonctions utiles : \n
        - Marqueurs :
            - add_marqueur(marqueur) \n
    Attributs utiles :\n
        - self.colors :  dict[marqueur: str] = couleur: str (Ex: #RRGGBB) \n
        - self.variants :dict[variantes: str]= détail de la variante : list[str]\n 
    '''

    def __init__(self, master,report:Text) -> None:
        super().__init__(master)

        self.buttons = {}
        self.colors = {'not' : '#CECECE','base': 'black'}
        self.report = report
        self.variants = {}
        self.var_file = None
        self.var_frame = Frame(self)
        self.var_frame.grid(column=0,row=1,sticky=N)
        self.var_fbutton = Button(self.var_frame,text='Changer de variantes',command= lambda : self.change_file())
        self.var_fbutton.grid(column=0,row=0)
        self.var_button = {}        

        self.func = None
        self.button_reset = Button(self,text='Remise à zero')
        self.button_reset.grid(column=0,row = 2)

    '''     GESETION DES MARQUEURS      '''

    def set_func(self,func):
        self.func = func
        self.button_reset.configure(command=lambda:[chk.state(['!alternate','!selected']) for chk in self.buttons.values()]+[self.func()])

        
    
    def clic(self,marker):
        '''
        Permet de gérer les états des boutons :
            - Vide : marqueurs non positionné
            - Coché : marqueur pris
            - Case noire : marqueurs suprimmé   

        Attention : une fois que le bouton quitte l'état "vide" il ne peut y retourner sans la remise à zero des boutons 
        '''
        if 'alternate' in self.buttons[marker].state():
            pass
        elif self.buttons[marker].instate(['selected']) :
            pass
        else:
            self.buttons[marker].state(['alternate','!selected'])
            
        self.func()

    
    
    def add_marker(self,marker : str) : 
        if marker not in self.colors.keys() :
            self.colors[marker] = self.random_color()
            self.colors['not ' + marker] = self.random_color()

            newstyle = ttk.Style()
            newstyle.configure(f'{marker}.TCheckbutton',background = self.colors[marker])
            self.buttons[marker] = ttk.Checkbutton(self, text = marker,command= lambda : self.clic(marker),style=f'{marker}.TCheckbutton')
            self.buttons[marker].grid(column=0,row=len(self.buttons)+2,sticky=W)
            self.buttons[marker].state(['!selected','!alternate'])


    def reset_buttons(self) :
        self.func = None
        for button in self.buttons.values():
            button.grid_remove()
            button.forget()
        self.buttons = {}
        self.colors = {'not' : '#CECECE','base': 'black'}

    
    def get_states(self) :
        states = {}
        for marker in self.buttons.values():

            if 'alternate' in marker.state():
                states[(marker.cget('text'))] = False
            elif 'selected' in marker.state() :
                states[(marker.cget('text'))] = True
        return states


    def random_color(self) :
        '''
        Based on https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
        
        '''
        def hsv_to_rgb(h,s,v) :
            r,g,b = colorsys.hsv_to_rgb(float(h),s,v)
            return f'#{hex(int(r*255))[2:].upper():>02s}{hex(int(g*255))[2:].upper():>02s}{hex(int(b*255))[2:].upper():>02s}' 
        h = uniform(0,1)

        color = hsv_to_rgb(h, 0.99, 0.82)
        return color


    '''     GESTION DES VARIANTES       '''

    def change_file(self,file=None):
        if file == None :
            self.var_file = askopenfilename(filetypes=[("Variant source Files", "*.var")],title='Open a file')
        else :
            self.var_file = file
        
        if not self.var_file in [None,''] :

            # Clear ancient variants
            for button in self.var_button.values():
                button.grid_remove()
                button.forget()
            self.var_button = {}

            #Get variants from the file
            variant = open(self.var_file,'r')
            tree = grammar_parse(variant.read())
            variant.close()
            v = VarVisitor()
            self.variants = v.visit(tree)
            
            for var in self.variants.keys() :
                self.new_var_button(var)


    def new_var_button(self,var):
        self.var_button[var] = ttk.Button(self.var_frame,text=var)
        self.var_button[var].configure(command= lambda : self.apply_var(var))
        self.var_button[var].grid(column = (len(self.var_button)+1)%2,row = (len(self.var_button)+1)//2)


    def apply_var(self,variant:str):
        marqueurs = {}
        try :
            marqueurs = parse(self.variants[variant],self.variants,dejavu={variant : ''},marqueurs=self.get_states(),variant_name=variant,report=self.report)
            for marqueur in marqueurs.keys() :
                try :
                    if marqueurs[marqueur]:
                        self.buttons[marqueur].state(['!alternate','selected'])
                    else:
                        self.buttons[marqueur].state(['alternate','!selected'])
                except KeyError:
                    self.report.config(state='normal')
                    self.report.insert(INSERT,f'{marqueur} n\'est pas présent dans ce fichier\n')
                    self.report.yview('scroll',len(self.report.get('0.0',INSERT)),'units')
                    self.report.config(state='disabled')
            self.func()
        except BadVariantFile as e :
            self.report.config(state='normal')
            self.report.insert(INSERT,e.value)
            self.report.yview('scroll',len(self.report.get('0.0',INSERT)),'units')
            self.report.config(state='disabled')
            print(e.value)
        


    def old_random_color(self) :
        '''
        Generate a random hexadecimal color
        Return:
        :return color: hexadecimal code for a color (#rrggbb)
        :type color: str
        '''
        return f"#{hex(randint(0,255))[2:].upper():>02s}{hex(randint(0,255))[2:].upper():>02s}{hex(randint(0,255))[2:].upper():>02s}"


class TkFileText(Frame) :
    '''
    Cadre permettant de naviguer entre les fichiers
    '''

    def __init__(self, master,nom_fichier: str,marker_frame : MarkerFrame ,text : Text) -> None:
        self.marker_frame = marker_frame
        super().__init__(master,background='black')
        self.nom_fichier = nom_fichier
        self.title = Button(self,text=self.nom_fichier.split(sep=os.sep)[-1],background=marker_frame.random_color(),relief='flat')
        self.escape_buton = Button(self,text='X',command= lambda : self.escape(),relief='flat',background='#b30000')
        self.title.grid(column=0,row=0)
        self.escape_buton.grid(column=1,row=0)
        self.text = text


    
    def escape(self):
        self.text.config(state='normal')
        self.grid_remove()
        self.nom_fichier = None
        self.text.delete('0.0',END)
        self.forget()
        self.text.config(state='disabled')

        
    
    def set_func(self,func) :
        self.title.config(command=lambda : func())

class ErrorWindow(Tk):
    
    def __init__(self,error_message: str ,screenName = None, baseName = None) -> None:
        super().__init__(screenName, baseName)
        Label(self,text=error_message).pack(fill=BOTH)