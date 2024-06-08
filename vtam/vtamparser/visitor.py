#!/usr/bin/env python3
from parsimonious.nodes import NodeVisitor, RegexNode

class XcfilterVisitor(NodeVisitor):
    """
    Visiteur pour xcfilter.
    Le constructeur prend pour argument le dictionnaire 
    des marqueurs à appliquer
    """
    def __init__(self, marqueurs):
        self.marqueurs = marqueurs
        
    def visit_content(self, node, visited_children):
        """ Retourne le resultat de l'application des marqueurs """
        output = ""
        for child in visited_children:
            output += child[0]

        return output
    
    def visit_block(self, node, visited_children):
        """ Retourne :
                - le contenu du marqueur si celui-ci est True
                - rien si le marqueur est False
                - la version intermédiaire si le marqueur n'a pas été spécifié
        """
        
        eval_expr = visited_children[0]
        contenu = visited_children[1]
        elifs = visited_children[2]
        if visited_children[3] != '':
            else_ = visited_children[3][0]
        else :
            else_ = ''
        
        if isinstance(eval_expr, str):
            # Un des marqueurs de l'expression n'a pas ete spécifié
            # on retourne la version intermédiaire du marqueur bloc
            inter = "".join(visited_children[:2])
            for i in elifs :
                inter+= i[0]
            for i in else_ :
                inter+= i
            inter +="".join(visited_children[4:])
            return inter
        elif eval_expr:
            # On affiche le contenu du marqueur
            return contenu
        else: 
            return self.elif_else_or_nothing(elifs,else_,visited_children[-1])

    def visit_block_start(self, node, visited_children):
        """ 
        Retourne le resultat de l'evaluation de l'expression 
        ou bien la version intermédiaire 
        """
        
        eval_expr = visited_children[4]
        if isinstance(eval_expr, str):
            # On doit retourner la version intermédiaire
            return self.str_list(visited_children)
        else:
            return eval_expr

    def visit_block_stop(self, node, visited_children):
        """ 
        Retourne le resultat de l'evaluation de l'expression 
        ou bien la version intermédiaire 
        """
        # On doit retourner la version intermédiaire au cas ou il serait utile
        return node.text
    
    def visit_elif(self,node,visited_children):
        '''Retourne:
                + l'expression intermédiaire dans tout les cas       
                    et:
                        - le contenu du marqueur si celui-ci est True
                        - rien si le marqueur est False
                        - None si il n'est pas précisé
        '''
        eval_expr = visited_children[0][1]
        contenu = visited_children[1]
        visited_children[0] = visited_children[0][0]
        if eval_expr == None:
            return "".join(visited_children),None
        elif eval_expr:
            return "".join(visited_children),contenu
        else :
            return "".join(visited_children),""

    def visit_elif_start(self,node,visited_children):
        '''Retourne:
                + l'expression intermédiaire dans tout les cas       
                    et:
                        - l'évaluation du marqueur si celui-ci est précisé
                        - None si il n'est pas précisé
        '''
        
        eval_expr = visited_children[5]
        if isinstance(eval_expr, str):
            return node.text,None
        else:
            return node.text,eval_expr
    
    def visit_else(self,node,visited_children):
        return "".join(visited_children[0]),visited_children[1]

    def visit_inline(self, node, visited_children):
        
        """ Retourne :
                - le contenu du marqueur si celui-ci est True
                - rien si le marqueur est False
                - la version intermédiaire si le marqueur n'a pas été spécifié
        """
        eval_expr = visited_children[0]
        contenu = visited_children[1]

        if isinstance(eval_expr, str):
            # Un des marqueurs de l'expression n'a pas ete spécifié
            # on retourne la version intermédiaire du marqueur inline
            return "".join(visited_children)
        elif eval_expr:
            # On affiche le contenu du marqueur
            return contenu
        else: 
            return ""

    def visit_inline_start(self, node, visited_children):
        """ 
        Retourne le resultat de l'evaluation de l'expression 
        ou bien la version intermédiaire 
        """
        eval_expr = visited_children[1]
        if isinstance(eval_expr, str):
            return "".join(visited_children)
        else:
            return eval_expr

    def visit_inline_stop(self, node, visited_children):
        """ 
        Retourne le resultat de l'evaluation de l'expression 
        ou bien la version intermédiaire 
        """
        eval_expr = visited_children[1]
        if isinstance(eval_expr, str):
            return "".join(visited_children)
        else:
            return eval_expr
    
    def visit_inline_content(self, node, visited_children):
        output = ""
        for child in visited_children:
            output += child[0]

        return output

    def visit_text(self, node, visited_children):
        """ Retourne le texte contenu """
        return node.text

    def visit_no_else_expr(self,node,visited_children):
        return visited_children[1]
        
    def visit_expr(self, node, visited_children):
        """ Retourne l'expression évaluée """
        
        return visited_children[0]

    def visit_par_expr(self, node, visited_children):
        
        return visited_children[1]

    def visit_balise_elif(self,node,visited_children) :
        return node.text

    def visit_if(self,node,visited_children) :
        return "".join(visited_children)

    def visit_not(self, node, visited_children):
        """ 
        Retourne la verison intermédiaire ou bien
        l'expression après application de not 
        """
        eval_expr = visited_children[1]
        if isinstance(eval_expr, str):
            return "not " + eval_expr
        else: 
            return not eval_expr

    def visit_marqueur_id(self, node, visited_children):
        """ Retourne la valeur du marqueur si celui-ci est spécifié,
        l'id du marqueur sinon"""
        
        marqueur_id = node.text
        if marqueur_id in list(self.marqueurs):
            return self.marqueurs[marqueur_id]
        else:
            return marqueur_id
        
    def generic_visit(self, node, visited_children):
        if len(node.children) > 0 and isinstance(node.children[0], RegexNode):
            # Pour les RegexNode on retourne directement le texte
            # qui a match
            return node.children[0].text
        else:
            return visited_children or node.text

    def str_list(self,liste) :
        '''
        Transformer une liste de liste en un string
        ex : str_list([['a','b'],'c']) == 'abc'
        '''
        if isinstance(liste,list):
            txt = ''
            for i in liste:
                txt +=self.str_list(i)
            return txt
        elif isinstance(liste,str) :
            return liste
        else:
            return ''

    def elif_else_or_nothing(self,elifs:list[tuple[str,bool]],else_:list,block_stop : str):
        fini = False
        i = 0
        while not fini :
            if i == len(elifs):
                fini = True
            else:
                if elifs[i][1] == None:
                    fini = True
                elif elifs[i][1] == '':
                    i+=1
                else:
                    return elifs[i][1]
        if i != len(elifs):
            # Un des elif n'est pas précisé
            elifs[i] = list(elifs[i])
            contenu = elifs[i][0].split('\n')
            contenu[0] = contenu[0].replace('elif','if')
            
            elifs[i][0] = "\n".join(contenu)
            
            if else_ != '':
                contenu = "".join([k[0] for k in elifs[i:]] + list(else_)) + block_stop
            else : 
                contenu = "".join([k[0] for k in elifs[i:]]) + block_stop
            return contenu
        else:
            # Aucun des elifs n'es True
            if else_ != '':
                return else_[1]
            else : 
                return ''
