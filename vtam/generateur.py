import os
import itertools
import re
import subprocess
import hashlib

def get_markers_from_file(file_path):
    """
    Extrait les marqueurs d'un fichier donné.

    Args:
        file_path (str): Chemin du fichier à analyser.

    Returns:
        tuple: Un ensemble de marqueurs et un ensemble de marqueurs "NO_".
    """
    markers = set()
    no_markers = set()
    try:
        # Tente de lire le fichier avec l'encodage UTF-8
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        # Si l'encodage UTF-8 échoue, tente de lire le fichier avec l'encodage latin-1
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()

    # Trouve les marqueurs dans différents formats
    markers.update(re.findall(r'//\s*EXTRACT\s+(\w+)', content))
    markers.update(re.findall(r'<\((\w+)\)>', content))
    markers.update(re.findall(r'//\s*if\s+(\w+)\s+START\s+DELETE', content))
    markers.update(re.findall(r'#\s*(\w+)\s+START\s+DELETE', content)) 

    # Identifie les marqueurs "NO_" et les sépare des autres marqueurs
    no_markers.update({m for m in markers if m.startswith("NO_")})
    markers.difference_update(no_markers)

    return markers, no_markers

def get_all_combinations(markers, no_markers, limit=300):
    """
    Génère toutes les combinaisons possibles de marqueurs.

    Args:
        markers (set): Ensemble de marqueurs.
        no_markers (set): Ensemble de marqueurs "NO_".
        limit (int): Limite de combinaisons à générer.

    Returns:
        list: Liste des combinaisons de marqueurs.
    """
    combinations = []
    marker_list = list(markers)
    n = len(marker_list)
    count = 0

    # Génère toutes les combinaisons de +marqueur, -marqueur, et marqueurs non traités
    for combo in itertools.product(['+', '-', ''], repeat=n):
        combination = [f"{sign}{marker}" for sign, marker in zip(combo, marker_list) if sign]
        # Ajoute les combinaisons avec NO_MARKER comme XOR
        for no_marker in no_markers:
            original_marker = no_marker[3:]
            if f"+{original_marker}" in combination:
                combination.remove(f"+{original_marker}")
                combination.append(f"-{no_marker}")
            elif f"-{original_marker}" in combination:
                combination.remove(f"-{original_marker}")
                combination.append(f"+{no_marker}")
        combinations.append(combination)
        count += 1
        if count >= limit:
            break

    return combinations

def create_marker_string(marker_combination):
    """
    Crée une chaîne de caractères représentant une combinaison de marqueurs.

    Args:
        marker_combination (list): Liste de marqueurs combinés.

    Returns:
        str: Chaîne de caractères des marqueurs combinés.
    """
    return ' '.join(marker_combination)

def get_hashed_filename(base_name, marker_string):
    """
    Génère un nom de fichier basé sur un hash de la chaîne de marqueurs.

    Args:
        base_name (str): Nom de base du fichier.
        marker_string (str): Chaîne de marqueurs combinés.

    Returns:
        str: Nom de fichier hashé.
    """
    hash_object = hashlib.md5(marker_string.encode())
    hash_string = hash_object.hexdigest()
    return f"{base_name}_{hash_string}"

def process_directory(directory_name, force=False):
    """
    Traite un répertoire pour générer toutes les combinaisons possibles de marqueurs pour chaque fichier.

    Args:
        directory_name (str): Nom du répertoire à traiter.
        force (bool): Forcer la génération de fichiers et ignorer la vérification de la consistance.
    """
    file_markers = {}

    # Parcourt récursivement le répertoire pour trouver tous les fichiers
    for root, _, files in os.walk(directory_name):
        for file in files:
            file_path = os.path.join(root, file)
            markers, no_markers = get_markers_from_file(file_path)
            file_markers[file_path] = (markers, no_markers)
    
    output_directory = f"{directory_name}_output"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for file_path, (markers, no_markers) in file_markers.items():
        marker_combinations = get_all_combinations(markers, no_markers)
        print(f"Processing {file_path}: {len(marker_combinations)} combinations")
        for marker_combination in marker_combinations:
            marker_string = create_marker_string(marker_combination)
            base_name = os.path.basename(file_path)
            output_file_name = get_hashed_filename(base_name, marker_string)
            output_file_path = os.path.join(output_directory, output_file_name)

            # Prépare la commande xcfilter
            cmd = [
                'python3', 'xcfilter.py',
            ]
            if force:
                cmd.append('-f')
            cmd.extend([
                file_path,
                output_file_path
            ] + marker_string.split())

            # Exécute la commande
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors du traitement du fichier {file_path} avec les marqueurs {marker_string}: {e}")

if __name__ == "__main__":
    import argparse

    # Analyse des arguments de la ligne de commande
    parser = argparse.ArgumentParser(description="Générer toutes les combinaisons possibles de marqueurs pour les fichiers d'un répertoire.")
    parser.add_argument("directory_name", type=str, help="Nom du répertoire à traiter")
    parser.add_argument("-f", "--force", action="store_true", help="Forcer la génération des fichiers et ignorer la vérification de la consistance")
    args = parser.parse_args()

    # Appel de la fonction principale
    process_directory(args.directory_name, args.force)
