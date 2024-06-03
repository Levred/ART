#!/usr/bin/env python3
"""
Permet de générer un document à partir d'un template
Certains morceaux du template délimités par des marqueurs sont gardés/enlevés
selon les marqueurs spécifiés dans la commande.
"""

import sys
import argparse
from exceptions import *
import time
from xc_directory import open_dir, result_file
from consistency import check_consistency

from utils import parse_markers
from vtamparser import grammar
from vtamparser import visitor
from vtamparser.var_grammar import parse
from vtamparser.var_visitor import VarVisitor

def render(template, markers, debug=False):
    """
    Rend un template en remplaçant les sections basées sur les marqueurs.

    Args:
        template (str): Le contenu du template à traiter.
        markers (dict): Un dictionnaire de marqueurs à appliquer.
        debug (bool): Indicateur pour afficher le tree de parsing pour le débogage.

    Returns:
        str: Le contenu du template rendu.
    """
    tree = grammar.parse(template)
    v = visitor.XcfilterVisitor(markers)
    if debug:
        print(tree)

    return v.visit(tree)

def open_file_with_encoding(file_path):
    """
    Ouvre un fichier avec différents encodages pour gérer les erreurs de décodage.

    Args:
        file_path (str): Chemin du fichier à ouvrir.

    Returns:
        str: Le contenu du fichier.
    """
    encodings = ['utf-8', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Impossible de décoder {file_path} avec les encodages {encodings}")

def main(template_file, output_file, markers, marker_verif_file, force, ignore_deduction):
    """
    Point d'entrée principal pour traiter le fichier template et générer la sortie.

    Args:
        template_file (str): Chemin du fichier template.
        output_file (str): Chemin du fichier de sortie.
        markers (dict): Dictionnaire des marqueurs.
        marker_verif_file (str): Chemin du fichier de vérification des marqueurs.
        force (bool): Forcer la génération du fichier sans vérification de consistance.
        ignore_deduction (bool): Ignorer la déduction des marqueurs.
    """
    start_time = time.time()

    try:
        # Vérifier le fichier de vérification des marqueurs selon les arguments donnés
        check_consistency(markers, marker_verif_file, force, ignore_deduction)

        # Rendre le template
        template_content = open_file_with_encoding(template_file)
        result = render(template_content, markers)

        # Écrire le résultat dans le fichier de sortie
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(result)
    
    except IncorrectVerificationFile:
        print("Abandon ...")
        return
    except FileNotFoundError:
        print("Le fichier d'entrée donné ", template_file, " n'a pas été trouvé.")
    except UnicodeDecodeError as e:
        print(f"Erreur Unicode lors du traitement de {template_file} : {e}")
    finally:
        end_time = time.time()
        print(f"Fichier {template_file} traité en {(end_time - start_time)*1000:.3f} ms.")
def open_variants(var_file):
    """
    Ouvre et analyse le fichier de variantes.

    Args:
        var_file (str): Chemin du fichier de variantes.

    Returns:
        dict: Dictionnaire des variantes.
    """
    variant_content = open_file_with_encoding(var_file)
    tree = parse(variant_content)
    v = VarVisitor()
    var = v.visit(tree)
    return var

if __name__ == "__main__":

    # Analyse des arguments de la ligne de commande
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-m CHECK_FILE.marker] [-v VARIANT_FILE.var] [-f] [-i] [-dir] TEMPLATE_FILE OUTPUT_FILE +|-[MARKER_1] ... +|-[MARKER_N]')
    parser.add_argument('-m', "--marker_file", type=str, nargs=1, help='Le fichier z3 pour vérifier la consistance des marqueurs. Si non précisé, il utilisera le fichier default.markers. Utilisez -f pour ignorer la vérification de consistance.')
    parser.add_argument('-v', '--variant_file', type=str, nargs=1, help='Le fichier pour obtenir les variantes. Si non précisé, vous ne pourrez pas utiliser les variantes.')
    parser.add_argument('-f', "--force", action='store_true', help='Forcer la génération de fichiers et ignorer tout ce qui concerne la vérification de consistance entre les marqueurs.')
    parser.add_argument('-i', "--ignore_deduction", action='store_true', help='Vérifier la consistance des marqueurs mais ne pas déduire les marqueurs du fichier.')
    parser.add_argument('-dir', "--use_directory", action='store_true', help='Utiliser un répertoire au lieu d\'un fichier unique.')
    parser.add_argument('TEMPLATE_FILE', type=str, help='Le fichier template de base.')
    parser.add_argument('OUTPUT_FILE', type=str, help='Le nom du fichier à générer.')
    parser.add_argument("MARKERS", type=str, nargs=argparse.REMAINDER, help='Les marqueurs choisis précédés de +/- pour les activer ou désactiver.')

    args = parser.parse_args()
    var = None
    force = args.force
    ignore_deduction = args.ignore_deduction
    task_list = {}  # Liste de tâches du programme
    
    if args.use_directory:
        # Récupérer les informations du répertoire (liste des fichiers, variantes, consistance)
        task_list, marker_verif_file, var_file, force = open_dir(args.TEMPLATE_FILE, args.OUTPUT_FILE, force)
        if var_file is not None:
            var = open_variants(var_file)
    else:
        marker_verif_file = args.marker_file
        template_file = args.TEMPLATE_FILE
        output_file = args.OUTPUT_FILE
        task_list = {template_file: output_file}
        if args.variant_file is not None:
            var = open_variants(args.variant_file[0])

    markers = parse_markers.parse(args.MARKERS, var)
    for template_file, output_file in task_list.items():
        main(template_file, output_file, markers, marker_verif_file, force, ignore_deduction)

    if args.use_directory:
        # Créer le fichier pour suivre chaque marqueur utilisé
        result_file(args.OUTPUT_FILE, markers)
