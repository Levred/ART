"""
Grammaire du language de marqueur VTAM
"""

from parsimonious.grammar import Grammar

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
        inline_stop = "<(/" no_else_expr ")>" &nl?
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

