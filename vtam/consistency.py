from utils import z3_parser
from exceptions import *
from z3 import *
import re

def check_consistency(markers, marker_verif_file, force, ignore_deduction):
    """ Checks the user command parameters to determine the consistency checking to choose"""
    # No verification
    if force:
        print("NOT verifying consistency between markers. Forcing file generation.")
        return

    # Now we want at least to check consistency
    file = ""
    if marker_verif_file == None:
        file = "default.marker"
    # If given, the file should have the .marker extension:
    elif marker_verif_file[0].split(".")[-1] == "marker":
        file = marker_verif_file[0]
    else:
        print("ERROR : The provided checking file", marker_verif_file[0], "should have the .marker extension.")
        raise IncorrectVerificationFile

    consistency(file, markers, ignore_deduction)
    
def consistency(marker_verif_file, command_markers, ignore_deduction):
    """Checks the logical satisfiability of the marker_verif_file and deduce markers values if possible.
    The marker_verif_file should have the z3 syntax.
    command_markers is the dictionnary of markers given by the user command (+/- markers)
    ignore_deduction ignores the deduction step if set to True
    If ignore_deduction is set to False, it may modify the dictionnary before sending it back to the main function
    """
    
    ### First step : consistency checking 
    print("Verifying that the set of markers is consistent with ", marker_verif_file, "\n")

    # First reading of the file : finding present markers in the file.
    # This is necessary, as the user command could omit volontarily some markers...

    markers = set()
    try:
        markers = z3_parser.get_markers_from_file(marker_verif_file)
    except FileNotFoundError:
        print("ERROR : the file ", marker_verif_file, " has not been found. Use -f to ignore everything related to consistency checking.")
        raise IncorrectVerificationFile

    # Create a variable for each marker
    for m in markers:
        # The variables should keep the right name to be evaluated later...
        exec(str(m) + " = Bool(\"" + str(m) + "\")")
        
    # Second reading of the file : we add each line to the solver
    s = Solver()
    string_properties = []
    f = open(marker_verif_file, "r") # it exists.
    nbline = 0
    for l in f:
        nbline += 1
        s.push()
        try:
            s.add(eval(l))
        except SyntaxError:
            print("- ERROR : z3 syntax error at line ", nbline)
            s.pop()
            continue
        string_properties.append(l)
    f.close()
        

    ## Check that the file is consistent by itself
    if s.check() != z3.sat:
        print("- OK : The ", marker_verif_file, " file is not satisfiable by itself.")
        raise IncorrectVerificationFile
    else:
        print("- OK : The ", marker_verif_file, " file is satisfiable by itself.")

    ## Check the properties are satisfiable with one of the left-side members set to True
    ## ... which should be a legitimate feature choice.
    ## Each line should be an Implies(..., ...)
    deja_vus = []
    for i in range(len(string_properties)):
        prop = string_properties[i]
        # Inside Implies(..., ...) parentheses:
        prop_int = z3_parser.get_inside_parentheses(prop)[0]
        # Left side of the Implies(..., ...)
        membre_gauche = z3_parser.comma_splitting(prop_int)[0].replace(" ", "")
        if membre_gauche in deja_vus:
            continue
        deja_vus.append(membre_gauche)
        s.push()
        # We set that member to True in the solver
        exec("s.add(" + membre_gauche + " == True)")
        if s.check() != z3.sat:
            print("- WARNING : The ", marker_verif_file, " file is not satisfiable when choosing the feature line", i+1, " (", membre_gauche, ").")
        s.pop() # Ready to start again 
    
    ## Check the properties are satisfiable with each marker set to true separately:
    for m in markers:
        if m in deja_vus:
            continue
        s.push()
        exec("s.add(" + m + " == True)")
        if s.check() != z3.sat:
            print("- WARNING : The ", marker_verif_file, " file is not satisfiable when choosing the marker", m, "individually.")
        s.pop() # Ready to start again
        
    ## Check the properties are satisfiable with the given user values :
    str_markers =[]
    for m in markers:
        if m in command_markers:
            if command_markers[m]:
                str_markers.append(str(m))
                exec("s.add("+ str(m) + " == True)") # "+" markers
            else:
                str_markers.append("Not("+str(m)+")")
                exec("s.add("+ str(m) + " == False)") # "-" markers

    if s.check() == z3.sat:
        print("- OK : The ", marker_verif_file, " file is also satisfiable (SAT) with the given arguments.\n")
    else:
        print("- ERROR : The ", marker_verif_file, " file is NOT satisfiable (UNSAT) with the given arguments.\n")
        raise IncorrectVerificationFile

    ### Second step : Deduce some markers' values starting from the given markers
    if not ignore_deduction:
        # Putting the markers under a list form :
        var_marqueurs = str(markers).replace("'", "").replace('{', "[").replace('}', ']')
        var_marqueurs_true_false = str(str_markers).replace("'", "")
        
        # Calculating the consequence of the markers of the command:
        exec("global conseq; conseq = s.consequences(" + var_marqueurs_true_false + ", " + var_marqueurs + ")")
        for e in conseq[1]: # conseq[1] represents the Implies(hypothesis, deduction) list
            e_str = str(e)
            interieur = z3_parser.get_inside_parentheses(e_str)[0]
            droite = z3_parser.comma_splitting(interieur)[1] # Get the deduction

            # Recuperate the True deduced variables and put them in the dictionnary
            if "Not" not in droite and droite not in command_markers:
                print("- Marker ", droite, " deduced.")
                command_markers[droite] = True
    else:
        print("Ignoring markers deduction step ...")

