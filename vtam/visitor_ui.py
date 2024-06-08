import tkinter as tk
from tkinter import ttk
from marker_ui import MarkerFrame
from parsimonious.nodes import NodeVisitor, RegexNode

class VisitorUI(NodeVisitor):
    '''
    Visiteur qui traite le résultat d'un texte balisé puis analysé par la grammaire adapté
    '''

    def __init__(self,text : tk.Text,marker_frame : MarkerFrame):
        '''
        Construit un visiteur pour l'interface grapphique
        
        Paramètres :\n

        :param text: Widget de texte dans lequel écrire le texte
        :type text: tk.Text \n
        :param marker_frame: cadre dans lequel palcer les marqueurs trouvés
        :type marker_frame: marker_ui.Markerframe 
        '''
        self.text = text
        self.marker_frame = marker_frame
        self.tags = ['base']                     #Pile des tags [fond,...,surface]
        self.nottag = ''                         # tag à appliquer au bloc else
        self.marqueurs = self.marker_frame.get_states() #etats des marqueurs
        self.fini = []                          #Pile de booleen qui renseigne l'état d'un bloc

    def tagblock(self,tag):
        ''' Génerer le tag à aposer sur l'éventuel bloc else'''
        if 'not ' in tag :
            self.nottag = tag[4:]
        else :
            self.nottag = f'not {tag}'

    
    ##Visite des blocs


    def visit_content(self,node,visited_children):
        '''
        Retourner le contenu complet dans une liste
        '''
        output = []
        for child in visited_children:
            output.append(child[0])

        return output

    def visit_block(self,node,visited_children):
        '''
        Visiter un bloc et le retourner dans le bon état avec les tag correspondant
        '''
        eval_expr = visited_children[0]
        contenu = visited_children[1]
        elifs = visited_children[2]
        
        if visited_children[3] != '':
            else_ = visited_children[3][0]
        else :
            else_ = ''
        del self.tags[-1]
        
        if isinstance(eval_expr,list):
            #Le premier marqueur n'est pas précisé. On retourne l'expression intermédiaire directement
            del self.fini[-1]
            return visited_children
        elif eval_expr[1]:
            #Le premier marqueur est True on affiche donc le contenu du premier bloc et le reste (éventuels else/elifs) en grisé
            del self.fini[-1]
            return visited_children[1:-1]
        else:
            #Le premier marqueur est False, on grise la première partie et on affiche le reste en fonction de leurs marqueurs
            if self.fini[-1] != None:
                # Au moins un des blocs else/elif est non précisé ou True on les affiche en conséquence
                del self.fini[-1]
                return contenu,elifs,else_
            else:
                # Aucun des blocs else/elif n'est à True et ils sont tous précisés tout est grisé et abscence de else 
                del self.fini[-1]
                visited_children[-1][-1] = self.nottag
                return contenu,elifs,else_,visited_children[-1]

    def visit_block_start(self,node,visited_children):
        '''
        Visiter la balise de départ du bloc
        
        Retourne :  la balise de départ si le marqueur n'est pas précisé, un booleen corespondant au marqueur dans le cas contraire
        '''
        #Nouveau bloc donc nouveau self.fini
        self.fini.append(False)

        eval_expr = visited_children[4][1]
        marqueur = visited_children[4][0]
        #On agit en fonction de la visite du marqueur
        if not isinstance(eval_expr,bool) :
            #Le marqueur n'est pas précisé
            #On ajoute le marqueur aux tags pour avoir la bonne couleur
            self.new_tag(marqueur)

            #On remet le nom du marqueur à sa place et on ajoute le tag a la balise
            visited_children[4] = marqueur
            visited_children.append(self.tags[-1])
            
            #Fin de la recherche du bloc à afficher
            self.fini[-1] = None
            self.tagblock(marqueur)
            return visited_children
        elif eval_expr:
            #le marqueur est à True
            self.fini[-1] = True
            self.new_tag(marqueur)
            return visited_children[4]
        else :
            #le marqueur est à False
            self.new_tag('not')
            self.tagblock(marqueur)
            return visited_children[4]

    def visit_block_stop(self,node,visited_children):
        '''
        Retourne le block tel quel
        '''
        if visited_children[3] != '' :
            eval_expr = visited_children[3][0][0][1]
            if not isinstance(eval_expr,bool) :
                visited_children[3] = visited_children[3][0][0][0]+visited_children[3][0][1]

        visited_children.append(self.tags[-1])
        return visited_children

    def visit_elif(self,node,visited_children):
        '''Retourne:
                + l'expression intermédiaire dans tout les cas       
                    et:
                        - le contenu du marqueur si celui-ci est True
                        - rien si le marqueur est False
                        - None si il n'est pas précisé
        '''
        #Récupération de l'état du marqueur
        eval_expr = visited_children[0].pop(1)

        #Récupération du contenu
        visited_children[1] = visited_children[1][0][0]
        contenu = visited_children[1]

        focus = visited_children[0].pop(1)

        #On remonte la balise
        visited_children[0] = visited_children[0][0]
        tag = self.tags.pop(-1)

        if self.fini[-1] == None:
            #Retourner la version intermédiaire
            return visited_children,tag
        elif eval_expr:
            #le marqueur est à True
            if self.tags[-1] != 'not' and not focus:
                #L'un des marqueurs précédent n'est pas précisé on retourne la version itermédiaire
                return visited_children,tag
            else :
                #Tout les marqueurs précédents sont à False
                return contenu,tag
        else :
            #Le marqueur est à False
            return visited_children,tag

    def visit_elif_start(self,node,visited_children):
        '''Retourne:
                + l'expression intermédiaire dans tout les cas       
                + le tag actuel    
                + un booleen qui indique si le elif a le focus
        '''
        #Récupération de l'état du marqueur
        eval_expr = visited_children[5][1]
        balise = node.text
        focus = False
        
        if not isinstance(eval_expr, bool) or self.fini[-1] == None:
            # le marqueur ou l'un des précédents n'est pas précisé 

            #Application du tag approprié
            if not self.fini[-1]:
                #Ajout du tag du marqueur courant
                self.new_tag(visited_children[5][0],True)
            else :
                #Ajout du tag grisé
                self.tags.append('not')
            
            #Modification de la balise
            if self.fini[-1] == False:
                balise = balise.replace('elif','if')
                self.fini[-1] = None

        elif eval_expr and (self.fini[-1] == False):
            #Cas où le elif doit être affiché seul
            self.new_tag(visited_children[5][0],True)
            self.fini[-1] = True
            focus = True
        else :
            #Cas où le elif doit être grisé
            self.new_tag('not')
        return [balise,self.tags[-1],focus]
    
    def visit_else(self,node,visited_children):
        '''
        Retourne :
            le contenu du bloc sans la balise si le bloc doit être affiché seul
            le contenu du bloc avec la balise sinon

        '''
        tag =  self.tags.pop(-1)
        focus = visited_children[0].pop(2)
        if (self.tags[-1] == 'not') and focus:
            return visited_children[1:]
        return visited_children
    
    def visit_else_start(self,node,visited_children):
        '''
        Retourne :
            + la balise
            + le tag de la balise
            + le focus (booleen indiquant si le bloc est celui qui doit être affiché)
        '''
        focus = False
        if not self.fini[-1]:
            #Les marqueurs précédents étaient tous à False ou non présisés

            #Ajout du tag opposé au premier tag du bloc 
            self.new_tag(self.nottag,True)
            
            if self.fini[-1] != None :
                #Le bloc doit être affiché
                self.fini[-1] = True
                focus = True
        else :
            #Le marqueur doit être affiché
            self.new_tag('not')
        return ["".join(visited_children),self.tags[-1],focus]


    ##INLINE PART


    def visit_inline(self,node,visited_children):
        '''
        Retourne :
                + le contenu
                + le tag approprié (soit 'not' soit le tag du marqueur)
        '''
        eval_expr = visited_children[0][0][1]
        contenu = visited_children[1]
        
        if not isinstance(eval_expr,bool) :
            tag = self.tags.pop(-1)
            
            visited_children.append(tag)

            return visited_children
        elif eval_expr :
            tag = self.tags.pop(-1)
            return contenu,tag
        else :
            del self.tags[-1]
            return contenu,'not'


    def visit_inline_start(self,node,visited_children):
        '''
        Retourne:
                + la balise et le tag approprié
        '''
        eval_expr = visited_children[1][1]
        
        
        if not isinstance(eval_expr,bool) :
            self.new_tag(visited_children[1][0])
            visited_children[1] = visited_children[1][0]

            visited_children.append(self.tags[-1])
            return visited_children
        elif eval_expr :
            self.new_tag(visited_children[1][0])
            return visited_children[1],self.tags[-1]
        else :
            self.new_tag('not')
            return visited_children[1],self.tags[-1]

    def visit_inline_stop(self,node,visited_children):
        '''
        Retourne:
            la balise avec le tag approprié si le marqueur n'est pas précisé
                ou
            le marqueur et le tag approprié sinon
        '''
        eval_expr = visited_children[1][1]

        if not isinstance(eval_expr,bool) :
            visited_children[1] = visited_children[1][0]
            visited_children.append(self.tags[-1])
            return visited_children
        else :
            return visited_children[1],self.tags[-1]
    
    def visit_inline_content(self,node,visited_children): 
        ''' Retourne le contenu avec le tag associé  '''
        output = []
        for child in visited_children:
            output.append(child[0])
        output.append(self.tags[-1])
        return output
        

    ## EXPR PART

    def visit_stop_expr(self,node,visited_children) :
        ''' Retourne l'expression évaluée   '''
        return visited_children[1:]

    def visit_no_else_expr(self,node,visited_children):
        ''' Retourne l'expression évaluée   '''
        return visited_children[1]

    def visit_balise_elif(self,node,visited_children) :
        ''' Retourne "elif"/"else" '''
        return node.text

    def visit_if(self,node,visited_children) :
        ''' Retourne le texte   '''
        return "".join(visited_children)

    def visit_expr(self,node,visited_children): 
        ''' Retourne l'expression évaluée '''
        return visited_children[0]
    
    def visit_par_expr(self,node,visited_children):
        ''' Retourne le résultat de l'expression entre parenthèse'''
        return visited_children[1]

    def visit_not(self,node,visited_children):
        ''' Retourne le contraire de l'expression et le texte associé   '''
        state = visited_children[1][1]
        if visited_children[1][1] != None :
            state = not state
        return node.text, state

    def visit_marqueur_id(self, node, visited_children):
        ''' Evalue le marqueur, l'ajoute à l'interface si neccésaire et retourne le marqueur ainsi que son état'''
        marqueur_id = node.text
        self.marker_frame.add_marker(marqueur_id)
        marqueur_etat = None
        if marqueur_id in list(self.marqueurs) :
            marqueur_etat = self.marqueurs[marqueur_id]
        return marqueur_id,marqueur_etat

    def visit_text(self,node,visited_children):
        ''' Retourne le texte avec le tag actuel''' 
        return node.text,self.tags[-1]
    
    def visit_balise_marqueur(self,node,visited_children): 
        return None

    def generic_visit(self, node, visited_children) :
        if len(node.children) > 0 and isinstance(node.children[0], RegexNode):
            # Pour les RegexNode on retourne directement le texte
            # qui a match
            return node.children[0].text
        else:
            return visited_children or node.text

    def new_tag(self,new_tag,deep = False) :
        if deep :
            if self.tags[-2] == 'not':
                self.tags.append('not')
            else:
                self.tags.append(new_tag) 
        elif self.tags[-1] == 'not' :
            
            self.tags.append('not')

        else :
            self.tags.append(new_tag)

    def read_text(self,tagged_text,tag = 'base'):
        '''
        Affiche le texte visité avec les bonnes couleurs
        '''
        if (not isinstance(tagged_text,str)) and (len(tagged_text) != 0):
            # Le texte est vide ou il demande encore à être décomposé
            if isinstance(tagged_text[-1],str):
                # le dernier cran est un tag on va l'appliquer au reste du texte
                if (tagged_text[-1] in self.marker_frame.colors.keys()):
                    tag = tagged_text[-1]
                    tagged_text = tagged_text[:-1]
            for contenu in tagged_text:
                #On décompose le texte
                self.read_text(contenu,tag)
        else :
            #Le texte est un string on l'affiche avec le tag trouvé
            self.text.insert(tk.INSERT,tagged_text,(tag))
            self.text.tag_add(tag,f'insert-{len(tagged_text)}c',tk.INSERT)
            self.text.tag_config(tag,foreground=self.marker_frame.colors[tag])