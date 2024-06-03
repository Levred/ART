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

def process_file(input_file, output_file):
    # Lecture du fichier d'entrée avec gestion de l'encodage
    lines = read_file_with_fallback(input_file)
    
    # Modifier les lignes de début de bloc par les if
    for i, line in enumerate(lines):
        if re.match(r'#\s+NO_(\w+)\s+START\s+DELETE', line):
            marker = re.match(r'#\s+NO_(\w+)\s+START\s+DELETE', line).group(1)
            lines[i] = f'# if not {marker} START DELETE\n'
        elif re.match(r'#\s+(\w+)\s+START\s+DELETE', line):
            marker = re.match(r'#\s+(\w+)\s+START\s+DELETE', line).group(1)
            lines[i] = f'# if {marker} START DELETE\n'

    # remplace les enchainements par "# else START DELETE"
    i = 0
    while i < len(lines) - 1:
        current_line = lines[i]
        next_line = lines[i + 1]

        stop_delete_marker = re.match(r'#\s+(\w+)\s+STOP\s+DELETE', current_line)
        no_start_delete_marker = re.match(r'#\s+if\s+not\s+(\w+)\s+START\s+DELETE', next_line)
        start_delete_marker = re.match(r'#\s+if\s+(\w+)\s+START\s+DELETE', next_line)
        
        if stop_delete_marker and no_start_delete_marker:
            marker = stop_delete_marker.group(1)
            if marker == no_start_delete_marker.group(1):
                lines[i] = '# else START DELETE\n'
                lines.pop(i + 1)
                continue

        if re.match(r'#\s+NO_(\w+)\s+STOP\s+DELETE', current_line) and start_delete_marker:
            no_marker = re.match(r'#\s+NO_(\w+)\s+STOP\s+DELETE', current_line).group(1)
            if no_marker == start_delete_marker.group(1):
                lines[i] = '# else START DELETE\n'
                lines.pop(i + 1)
                continue
        
        i += 1

    # Modifie les lignes de fin de bloc pour en finir avec les NO_marqueurs
    for i, line in enumerate(lines):
        if re.match(r'#\s+NO_(\w+)\s+STOP\s+DELETE', line):
            marker = re.match(r'#\s+NO_(\w+)\s+STOP\s+DELETE', line).group(1)
            lines[i] = f'# {marker} STOP DELETE\n'

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
    parser.add_argument('output_file', type=str, help='The output file to save the result.')
    args = parser.parse_args()

    process_file(args.input_file, args.output_file)

if __name__ == '__main__':
    main()
