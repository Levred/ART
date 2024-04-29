#!/usr/bin/env python3
"""
Permet de generer un document a partir d'un template
Certains morceaux du template delimites par des marqueurs sont gardes/enleves
selon les marqueurs specifies dans la commande
"""
import sys
import argparse
from xc_directory import open_dir,result_file
from consistency import check_consistency
from exceptions import *
from utils import parse_markers
from vtamparser import grammar
from vtamparser import visitor
from vtamparser.var_grammar import parse
from vtamparser.var_visitor import VarVisitor

def render(template, markers, debug=False):
    tree = grammar.parse(template)
    v = visitor.XcfilterVisitor(markers)
    if debug: print(tree)

    return v.visit(tree)

def main(template_file, output_file, markers, marker_verif_file, force, ignore_deduction):
    try:
        # Check the marker verification file according to the given arguments
        check_consistency(markers, marker_verif_file, force, ignore_deduction)

        # Render template
        template = open(template_file, "r", encoding='utf-8')
        result = render(template.read(), markers)
        # Write to file
        f = open(output_file, "w",encoding='utf-8')
        f.write(result)
        f.close()
    
    except IncorrectVerificationFile:
        print("Aborting ...")
        return
    except FileNotFoundError:
        print("The given input file ", template_file, " has not been found.")


def open_variants(var_file):
    variant = open(var_file,'r')
    tree = parse(variant.read())
    variant.close()
    v = VarVisitor()
    var = v.visit(tree)
    return var

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-m CHECK_FILE.marker] [-v VARIANT_FILE.var] [-f] [-i] [-dir] TEMPLATE_FILE OUTPUT_FILE +|-[MARKER_1] ... +|-[MARKER_N]')
    parser.add_argument('-m', "--marker_file", type=str, nargs=1, help='The z3 file to verify the markers consistency. If not precised, it will use the default.markers \
                                                        file. Use -f to ignore consistency checking.')
    parser.add_argument('-v','--variant_file',type=str, nargs=1, help='The file to get variants from. If not precised, you won\'t be able to use variants')
    parser.add_argument('-f', "--force", action='store_true', help='Force the file generation and ignore anything related to consistency checking between markers.')
    parser.add_argument('-i', "--ignore_deduction", action='store_true', help='Check markers consistency but don\'t deduce markers from the file.')
    parser.add_argument('-dir',"--use_directory",action='store_true',help='Use a directory instead of a unique file')
    parser.add_argument('TEMPLATE_FILE', type=str, help='The base template file')
    parser.add_argument('OUTPUT_FILE', type=str, help='The name of the file to generate')
    parser.add_argument("MARKERS", type=str, nargs=argparse.REMAINDER, \
	    help='The chosen markers prefixed by +/- to activate or deactivate them')

    args = parser.parse_args()
    var = None
    force = args.force
    ignore_deduction = args.ignore_deduction
    task_list = {}      #To do list from the programm 
    
    if args.use_directory:
        #Get the information in the directory (list of files, variant, consistency)
        task_list,marker_verif_file,var_file,force = open_dir(args.TEMPLATE_FILE,args.OUTPUT_FILE,force)
        if var_file != None:
            var = open_variants(var_file)

    else:
        marker_verif_file = args.marker_file
        template_file = args.TEMPLATE_FILE
        output_file = args.OUTPUT_FILE
        task_list = {template_file:output_file}
        if args.variant_file != None :
            var = open_variants(args.variant_file[0])

    markers = parse_markers.parse(args.MARKERS,var)
    for template_file,output_file in task_list.items() :
        main(template_file, output_file, markers, marker_verif_file, force, ignore_deduction)


    if args.use_directory :
        #Create the file to keep track of each markers used
        result_file(args.OUTPUT_FILE,markers)