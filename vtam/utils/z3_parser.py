import re


def comma_splitting(chaine):
    """Splits a string according to the commas, but
        ignores commas that are inside parentheses

        Example :
        comma_splitting("And(A, B), Or(C, D)") == ["And(A, B)", "Or(C, D)"]
    """
    return re.split(r',\s*(?![^()]*\))', chaine)


def get_inside_parentheses(chaine):
    """Returns a list formed of :
        - What is inside the first pair of parentheses found
        - The rest of the string (after the right parenthesis)
    """
    niveau_parenthese = 0
    debut_parenthese = 0
    fin_parenthese = 0
    recherche_fermante = False
    
    for i in range(len(chaine)):
        if chaine[i] == "(":
            if not recherche_fermante: # First parenthesis found
                debut_parenthese = i
            recherche_fermante = True
            niveau_parenthese += 1
        if chaine[i] == ")":
            niveau_parenthese -= 1
            if niveau_parenthese == 0:
                fin_parenthese = i
                return [chaine[debut_parenthese+1:fin_parenthese], chaine[fin_parenthese+1:]]


def get_markers(chaine):
    """Gets the markers that are in the given string.
        Returns the markers as a set.
    """ 
    pile = [chaine]
    resultat = set()
    
    while pile != []:
        premiere_chaine = pile.pop()
        # If it's a marker : 
        if "(" not in premiere_chaine and "," not in premiere_chaine:
            if premiere_chaine != '':
                resultat |= {premiere_chaine}
            continue
        # Otherwise we have to analyze the string
        for i in range(len(premiere_chaine)):
            # Either it is a list with commas as separator :
            if premiere_chaine[i] == ",":
                # Split according to the comma, excluding commas inside parentheses :
                pile += comma_splitting(premiere_chaine)
                break
            # ... Or it is under the format Thing(...)
            if premiere_chaine[i] == "(":
                pile += get_inside_parentheses(premiere_chaine)
                break
            
    return resultat 

def get_markers_from_file(z3_file):
    """Gets the markers present in a z3 file
        Returns the markers as a Set.
    """
    markers = set()
    with open(z3_file, "r") as f:
        for l in f:
            # Parsing line by line ...
            markers |= get_markers(l) # fills in the markers list, from the z3 checking file
    markers.remove('\n')

    return markers
