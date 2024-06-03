import re

def comma_splitting(chaine):
    """
    Splits a string by commas, ignoring commas inside parentheses.

    Args:
        chaine (str): The input string.

    Returns:
        list: List of substrings split by commas.
    """
    return re.split(r',\s*(?![^()]*\))', chaine)

def get_inside_parentheses(chaine):
    """
    Returns the content inside the first pair of parentheses and the remaining string.

    Args:
        chaine (str): The input string.

    Returns:
        list: List containing the content inside parentheses and the remaining string.
    """
    niveau_parenthese = 0
    debut_parenthese = 0

    for i, char in enumerate(chaine):
        if char == "(":
            if niveau_parenthese == 0:
                debut_parenthese = i
            niveau_parenthese += 1
        elif char == ")":
            niveau_parenthese -= 1
            if niveau_parenthese == 0:
                return [chaine[debut_parenthese + 1:i], chaine[i + 1:]]

def get_markers(chaine):
    """
    Extracts markers from a string.

    Args:
        chaine (str): The input string.

    Returns:
        set: Set of markers.
    """
    pile = [chaine]
    resultat = set()

    while pile:
        premiere_chaine = pile.pop()
        if "(" not in premiere_chaine and "," not in premiere_chaine:
            if premiere_chaine:
                resultat.add(premiere_chaine)
            continue

        for i, char in enumerate(premiere_chaine):
            if char == ",":
                pile.extend(comma_splitting(premiere_chaine))
                break
            elif char == "(":
                pile.extend(get_inside_parentheses(premiere_chaine))
                break

    return resultat

def get_markers_from_file(z3_file):
    """
    Extracts markers from a Z3 file.

    Args:
        z3_file (str): Path to the Z3 file.

    Returns:
        set: Set of markers found in the file.
    """
    markers = set()
    with open(z3_file, "r") as f:
        for l in f:
            markers.update(get_markers(l))
    markers.discard('\n')
    return markers
