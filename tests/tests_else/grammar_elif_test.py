from parsimonious.grammar import Grammar
import visitor
def parse(text):

    grammar = Grammar(
        r"""
        content = (block / inline / text)*

        block = block_start content elif* else? block_stop
        block_start = hws w hws if? no_else_expr hws "START" hws "DELETE" hws w? hws nl
        block_stop = hws w hws stop_expr? "STOP" hws "DELETE" hws nl?
        
        elif = elif_start content
        elif_start = hws w hws "elif" hws no_else_expr hws "START" hws "DELETE" hws w? hws nl
        
        else = else_start content
        else_start = hws w hws "else" hws "START" hws "DELETE" hws w? nl 

        inline = inline_start inline_content inline_stop
        inline_start = "<(" no_else_expr ")>"
        inline_stop = "<(/" no_else_expr ")>" nl?
        inline_content = (inline / text)+
        
        stop_expr = !"STOP" no_else_expr hws
        no_else_expr = !balise_elif expr
        expr = not / marqueur_id / par_expr
        par_expr = "(" no_else_expr ")"
        not = "not " no_else_expr
        balise_elif = "else" / "elif"

        if = "if" hws
        w = ~"[^\s]+"
        marqueur_id = ~"\w+"
        text = (!balise_marqueur (~"." / ws))*
        balise_marqueur = inline_stop / inline_start / block_stop / block_start / else_start / elif_start
        nl = ~"\n"
        ws = ~"\s"
        hws = ~"[^\S\r\n]"*
        """
    )
    return grammar.parse(text)

if __name__ == '__main__' :
    template = open('src/vtam/tests_else/elif_exemple.txt', "r", encoding='utf-8')
    tree = parse(template.read())

    template.close()
    print("'A' : NA ,'B' : NA\n")
    v = visitor.XcfilterVisitor({'A':False,'B' : False,'E': True,'F':True,'G':True})
    print(v.visit(tree))

    #print("'A' : NA ,'B' : True\n")
    v = visitor.XcfilterVisitor({'B' : True})
    #print(v.visit(tree))

    #print("'A' : NA ,'B' : False\n")
    v = visitor.XcfilterVisitor({'B' : False})
    #print(v.visit(tree))

    #print("'A' : True ,'B' : NA\n")
    v = visitor.XcfilterVisitor({'A' : True})
    #print(v.visit(tree))

    #print("'A' : False ,'B' : NA\n")
    v = visitor.XcfilterVisitor({'A' : False})
    #print(v.visit(tree))

    #print("'A' : True ,'B' : True\n")
    v = visitor.XcfilterVisitor({'A' : True,'B':True})
    #print(v.visit(tree))

    #print("'A' : True ,'B' : False\n")
    v = visitor.XcfilterVisitor({'A' : True,'B':False})
    #print(v.visit(tree))

    #print("'A':False,'B' : False\n")
    v = visitor.XcfilterVisitor({'A':False,'B' : False})
    #print(v.visit(tree))

    #print("'A':False,'B' : True\n")
    v = visitor.XcfilterVisitor({'A':False,'B' : True})
    #print(v.visit(tree))