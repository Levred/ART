#!/usr/bin/env python3
import re
import argparse

def read_file_with_fallback(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.readlines()

def recuperer_marqueurs(chemin_fichier):
    """
    Extrait les marqueurs d'un fichier donné.
    
    Args:
        chemin_fichier (str): Chemin du fichier à analyser.
    
    Returns:
        tuple: Un ensemble de marqueurs et un ensemble de NO_marqueurs.
    """
    marqueurs = set()
    no_marqueurs = set()
    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as file:
            contenu = file.read()
    except UnicodeDecodeError:
        with open(chemin_fichier, 'r', encoding='latin-1') as file:
            contenu = file.read()

    for ligne in contenu.splitlines():
        parties = ligne.strip().split()

        if len(parties) >= 3 and parties[2] == 'START' and parties[3] == 'DELETE':
            marqueur = parties[1]
            prefixe = parties[0] + " "
            if marqueur.startswith('NO_'):
                no_marqueurs.add(marqueur)
            else:
                marqueurs.add(marqueur)

    return marqueurs, no_marqueurs, prefixe

def process_file(input_file, output_file, prefixe):
    if output_file is None:
        output_file = input_file + "out"
    
    if prefixe == 'auto':
        prefixe = recuperer_marqueurs(input_file)[2]

    # Lecture du fichier d'entrée avec gestion de l'encodage
    lines = read_file_with_fallback(input_file)

    # Modifier les lignes de début de bloc par les if
    for i, line in enumerate(lines):
        if re.match(rf'{prefixe}NO_(\w+)\s+START\s+DELETE', line):
            marker = re.match(rf'{prefixe}NO_(\w+)\s+START\s+DELETE', line).group(1)
            lines[i] = f'{prefixe}if not {marker} START DELETE\n'
        elif re.match(rf'{prefixe}(\w+)\s+START\s+DELETE', line):
            marker = re.match(rf'{prefixe}(\w+)\s+START\s+DELETE', line).group(1)
            lines[i] = f'{prefixe}if {marker} START DELETE\n'

    # remplace les enchainements par "# else START DELETE"
    i = 0
    while i < len(lines) - 1:
        current_line = lines[i]
        next_line = lines[i + 1]

        stop_delete_marker = re.match(rf'{prefixe}(\w+)\s+STOP\s+DELETE', current_line)
        no_start_delete_marker = re.match(rf'{prefixe}if\s+not\s+(\w+)\s+START\s+DELETE', next_line)
        start_delete_marker = re.match(rf'{prefixe}if\s+(\w+)\s+START\s+DELETE', next_line)
        
        if stop_delete_marker and no_start_delete_marker:
            marker = stop_delete_marker.group(1)
            if marker == no_start_delete_marker.group(1):
                lines[i] = f'{prefixe}else START DELETE\n'
                lines.pop(i + 1)
                continue

        if re.match(rf'{prefixe}NO_(\w+)\s+STOP\s+DELETE', current_line) and start_delete_marker:
            no_marker = re.match(rf'{prefixe}NO_(\w+)\s+STOP\s+DELETE', current_line).group(1)
            if no_marker == start_delete_marker.group(1):
                lines[i] = f'{prefixe}else START DELETE\n'
                lines.pop(i + 1)
                continue
        
        i += 1

    # Modifie les lignes de fin de bloc pour en finir avec les NO_marqueurs
    for i, line in enumerate(lines):
        if re.match(rf'{prefixe}NO_(\w+)\s+STOP\s+DELETE', line):
            marker = re.match(rf'{prefixe}NO_(\w+)\s+STOP\s+DELETE', line).group(1)
            lines[i] = f'{prefixe}{marker} STOP DELETE\n'

    # Écriture dans le fichier de sortie avec gestion de l'encodage
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    except UnicodeEncodeError:
        with open(output_file, 'w', encoding='latin-1') as f:
            f.writelines(lines)

def main():
    parser = argparse.ArgumentParser(description='Process file to replace marked sections.')
    parser.add_argument('input_file', type=str, help='The input file to process.')
    parser.add_argument('output_file', type=str, nargs='?', default=None, help='The output file to save the result (optional).')
    parser.add_argument('--prefixe', type=str, default="auto", help='Prefixe des marqueurs (par defaut sera auto)')

    args = parser.parse_args()

    process_file(args.input_file, args.output_file, args.prefixe)

if __name__ == '__main__':
    main()
