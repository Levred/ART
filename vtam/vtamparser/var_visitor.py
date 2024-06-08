from parsimonious.nodes import NodeVisitor, RegexNode

class VarVisitor(NodeVisitor):

    def visit_text(self,node,visited_children):
        variantes = {}
        for var in visited_children:
            variantes[var[0][1:]]=var[1][0]
        
        return variantes

    def visit_variante(self,node,visited_children):
        variante_id = visited_children[1]
        param = []
        for mark in visited_children[5:]:
            param.append(mark)
        return variante_id,param

    def visit_marqueur(self,node,visited_children):
        return visited_children[0]

    def visit_var(self, node, visted_children) :
        return '@'+visted_children[2]

    def visit_var_id(self, node,visited_children):
        return node.text

    def visit_oui(self,node,visited_children):
        return '+'+visited_children[3]

    def visit_non(self,node,visited_children):
        return '-'+visited_children[3]

    def visit_marqueur_id(self,node,visited_children):
        return node.text

    def generic_visit(self, node, visited_children) :
        if len(node.children) > 0 and isinstance(node.children[0], RegexNode):
            # Pour les RegexNode on retourne directement le texte
            # qui a match
            return node.children[0].text
        else:
            return visited_children or node.text