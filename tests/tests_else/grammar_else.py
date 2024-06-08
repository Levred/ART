from parsimonious.grammar import Grammar
import visitor
def parse(text):

    grammar = Grammar(
        r"""
        content = (block / inline / text)*

        block = block_start content else? block_stop
        block_start = hws* "//" hws* no_else_expr hws* "START" hws* "DELETE" hws* nl
        block_stop = hws* "//" hws* "STOP" hws* "DELETE" hws* nl?

        else = else_start content
        else_start = hws* "//" hws* "else" hws* "START" hws* "DELETE" hws* nl 

        inline = inline_start inline_content inline_stop
        inline_start = "<(" expr ")>"
        inline_stop = "<(/" expr ")>" nl?
        inline_content = (inline / text)+
        
        no_else_expr = !"else" expr
        expr = not / marqueur_id / par_expr
        par_expr = "(" expr ")"
        not = "not " expr

        marqueur_id = ~"\w+"
        text = (!balise_marqueur (~"." / ws))*
        balise_marqueur = inline_stop / inline_start / block_stop / block_start / else 
        nl = ~"\n"
        ws = ~"\s"
        hws = ~"[^\S\r\n]"
        """
    )
    return grammar.parse(text)

template = open('src/vtam/tests_else/else_exemple.txt', "r", encoding='utf-8')
tree = parse(template.read())

template.close()
print("'OUI' : NA ,'BOF' : NA\n")
v = visitor.XcfilterVisitor({})
print(v.visit(tree))

print("'OUI' : NA ,'BOF' : True\n")
v = visitor.XcfilterVisitor({'BOF' : True})
print(v.visit(tree))

print("'OUI' : NA ,'BOF' : False\n")
v = visitor.XcfilterVisitor({'BOF' : False})
print(v.visit(tree))

print("'OUI' : True ,'BOF' : NA\n")
v = visitor.XcfilterVisitor({'OUI' : True})
print(v.visit(tree))

print("'OUI' : False ,'BOF' : NA\n")
v = visitor.XcfilterVisitor({'OUI' : False})
print(v.visit(tree))

print("'OUI' : True ,'BOF' : True\n")
v = visitor.XcfilterVisitor({'OUI' : True,'BOF':True})
print(v.visit(tree))

print("'OUI' : True ,'BOF' : False\n")
v = visitor.XcfilterVisitor({'OUI' : True,'BOF':False})
print(v.visit(tree))

print("'OUI':False,'BOF' : False\n")
v = visitor.XcfilterVisitor({'OUI':False,'BOF' : False})
print(v.visit(tree))

print("'OUI':False,'BOF' : True\n")
v = visitor.XcfilterVisitor({'OUI':False,'BOF' : True})
print(v.visit(tree))
