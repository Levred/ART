from parsimonious.grammar import Grammar
def parse(text) :

    grammar = Grammar(
        r'''
        text = variante+
        variante = nl? var hws* ":" nl marqueur+
        marqueur = oui / non / var
        var = hws* "@" var_id nl?
        var_id = ~"\w+"
        oui = hws* '+' hws* marqueur_id nl?
        non = hws* '-' hws* marqueur_id nl?
        marqueur_id = ~"\w+"
        nl = ~"\n"
        hws = ~"[^\S\r\n]"
        
        ''')
    
    return grammar.parse(text)
