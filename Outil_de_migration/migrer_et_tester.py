import os
import shutil
import subprocess
import random

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
            if marqueur.startswith('NO_'):
                no_marqueurs.add(marqueur)
            else:
                marqueurs.add(marqueur)

    return marqueurs, no_marqueurs

def creer_chaine_marqueurs(marqueurs, no_marqueurs):
    """
    Choisis aléatoirement les marqueurs a appliquer pour les test en respectant l'usage des NO_marqueurs.
    Renvoi une chaine de charactères avec le choix des marqueurs dans le format de xcfilter
    
    Args:
        marqueurs (set): Ensemble de marqueurs.
        no_marqueurs (set): Ensemble de NO_marqueurs.
    
    Returns:
        str: Chaîne de caractères des marqueurs combinés.
    """
    chaine_marqueurs = []
    for marqueur in marqueurs:
        no_marqueur = f"NO_{marqueur}"
        if no_marqueur in no_marqueurs:
            choix = random.choice([True, False])
            chaine_marqueurs.append(f"+{marqueur}" if choix else f"-{marqueur}")
            chaine_marqueurs.append(f"-{no_marqueur}" if choix else f"+{no_marqueur}")
        else:
            chaine_marqueurs.append(f"+{marqueur}")

    chaine_marqueurs.extend([f"+{no_marqueur}" for no_marqueur in no_marqueurs if no_marqueur[3:] not in marqueurs])

    return ' '.join(chaine_marqueurs)


def generer_fichier(chemin_fichier, repertoire_sortie, chemin_xcfilter, chaine_marqueurs, test_id, forcer=True):
    """
    Génère un fichier avec les marqueurs spécifiés.
    
    Args:
        chemin_fichier (str): Chemin du fichier à traiter.
        repertoire_sortie (str): Répertoire où enregistrer le fichier généré.-
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        chaine_marqueurs (str): Chaîne de caractères des marqueurs.
        test_id (int): Identifiant du test (sert à nommer le fichier de sortie).
        forcer (bool): Forcer la génération de fichiers et ignorer la vérification de la consistance.
    """
    if not os.path.exists(chemin_fichier):
        print(f"Le fichier d'entrée donné {chemin_fichier} n'a pas été trouvé.")
        return

    chemin_fichier_sortie = os.path.join(repertoire_sortie, f"{os.path.basename(chemin_fichier)}_test_{test_id}")

    cmd = [
        'python', chemin_xcfilter,
    ]
    if forcer:
        cmd.append('-f')
    cmd.extend([
        chemin_fichier,
        chemin_fichier_sortie
    ] + chaine_marqueurs.split())

    try:
        subprocess.run(cmd, check=True)
        print(f"Fichier généré : {chemin_fichier_sortie}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du traitement du fichier {chemin_fichier} avec les marqueurs {chaine_marqueurs}: {e}")

def generer_tests_pour_fichiers(repo_original, repo_migre, repo_test_original, repo_test_migre, chemin_xcfilter, nombre_tests, forcer=True):
    """
    Génère des fichiers de test pour verifier que le fichier migrer engendre la même chose.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers originaux.
        repo_migre (str): Répertoire contenant les fichiers migrés.
        repo_test_original (str): Répertoire temporaire pour les fichiers de test originaux.
        repo_test_migre (str): Répertoire temporaire pour les fichiers de test migrés.
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        nombre_tests (int): Nombre maximum de tests à générer par fichier.
        forcer (bool): Forcer la génération de fichiers et ignorer la vérification de la consistance.
    """
    for root, dirs, files in os.walk(repo_original):
        for file in files:
            chemin_source = os.path.join(root, file)
            chemin_relatif = os.path.relpath(chemin_source, repo_original)
            chemin_cible = os.path.join(repo_migre, chemin_relatif)
            if not os.path.exists(chemin_cible):
                print(f"Le fichier migré correspondant {chemin_cible} n'a pas été trouvé.")
                continue

            marqueurs, no_marqueurs = recuperer_marqueurs(chemin_source)
            chaines_marqueurs = [creer_chaine_marqueurs(marqueurs, no_marqueurs) for i in range(nombre_tests)]

            for i, chaine_marqueurs in enumerate(chaines_marqueurs):
                generer_fichier(chemin_source, repo_test_original, chemin_xcfilter, chaine_marqueurs, i + 1, forcer)
                generer_fichier(chemin_cible, repo_test_migre, chemin_xcfilter, chaine_marqueurs, i + 1, forcer)

def migrer_fichiers(repo_original, repo_migre):
    """
    Migre les fichiers d'un répertoire source vers un répertoire cible en utilisant un script de migration.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers à migrer.
        repo_migre (str): Répertoire où enregistrer les fichiers migrés.
    """
    script_migration = 'migration.py'
    if os.path.exists(repo_migre):
        shutil.rmtree(repo_migre)
    os.makedirs(repo_migre)
    
    for root, dirs, files in os.walk(repo_original):
        for file in files:
            chemin_source = os.path.join(root, file)
            chemin_relatif = os.path.relpath(chemin_source, repo_original)
            chemin_cible = os.path.join(repo_migre, chemin_relatif)

            dossier_cible = os.path.dirname(chemin_cible)
            if not os.path.exists(dossier_cible):
                os.makedirs(dossier_cible)

            cmd = ['python', script_migration, chemin_source, chemin_cible]
            subprocess.run(cmd, check=True)

def comparer_fichiers(chemin_fichier1, chemin_fichier2):
    """
    Compare le contenu de deux fichiers ligne par ligne.
    
    Args:
        chemin_fichier1 (str): Chemin du premier fichier.
        chemin_fichier2 (str): Chemin du second fichier.
    
    Returns:
        bool: True si les fichiers sont identiques, False sinon.
    """
    with open(chemin_fichier1, 'r') as fichier1, open(chemin_fichier2, 'r') as fichier2:
        lignes1 = fichier1.readlines()
        lignes2 = fichier2.readlines()

        if lignes1 != lignes2:
            for numero_ligne, (ligne1, ligne2) in enumerate(zip(lignes1, lignes2), start=1):
                if ligne1 != ligne2:
                    print(f"Différence à la ligne {numero_ligne} :\n{ligne1}\n{ligne2}")
            return False
    return True

def comparer_repertoires(repertoire1, repertoire2):
    """
    Compare le contenu de deux répertoires fichier par fichier.
    
    Args:
        repertoire1 (str): Chemin du premier répertoire.
        repertoire2 (str): Chemin du second répertoire.
    
    Returns:
        bool: True si les répertoires sont identiques, False sinon.
    """
    for root, dirs, files in os.walk(repertoire1):
        for file in files:
            chemin_fichier1 = os.path.join(root, file)
            chemin_relatif = os.path.relpath(chemin_fichier1, repertoire1)
            chemin_fichier2 = os.path.join(repertoire2, chemin_relatif)

            if not os.path.exists(chemin_fichier2):
                print(f"Le fichier correspondant {chemin_fichier2} n'a pas été trouvé.")
                return False

            if not comparer_fichiers(chemin_fichier1, chemin_fichier2):
                return False
    return True

def lister_marqueurs_repertoire(repertoire):
    """
    Liste les marqueurs et les non-marqueurs de chaque fichier dans le répertoire donné.
    
    Args:
        repertoire (str): Chemin du répertoire à analyser.
    """
    for root, dirs, files in os.walk(repertoire):
        for file in files:
            chemin_fichier = os.path.join(root, file)
            marqueurs, no_marqueurs = recuperer_marqueurs(chemin_fichier)
            print(f"Fichier : {chemin_fichier}")
            print(f"Marqueurs : {marqueurs}")
            print(f"Non-marqueurs : {no_marqueurs}")

def main(repo_original, repo_migre, chemin_xcfilter, nombre_tests, garder_tests):
    """
    Fonction principale pour migrer, générer des tests et comparer les fichiers.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers à migrer.
        repo_migre (str): Répertoire où enregistrer les fichiers migrés.
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        nombre_tests (int): Nombre maximum de tests à générer par fichier.
        garder_tests (bool): Garder les fichiers de test après comparaison.
    """
    # Donne un nom par defaut
    if repo_migre is None:
        repo_migre = f"{repo_original}_out"

    # Supprimer le répertoire cible s'il existe déjà
    if os.path.exists(repo_migre):
        shutil.rmtree(repo_migre)

    # Lister les marqueurs et non-marqueurs de chaque fichier dans le répertoire source (débogage)
    lister_marqueurs_repertoire(repo_original)

    # Migrer les fichiers
    migrer_fichiers(repo_original, repo_migre)

    repertoire_test_original = f"{repo_original}_test_original"
    repertoire_test_migre = f"{repo_migre}_test_migre"

    # Générer les fichiers de test pour l'original et les fichiers migrés
    generer_tests_pour_fichiers(repo_original, repo_migre, repertoire_test_original, repertoire_test_migre, chemin_xcfilter, nombre_tests)

    # Comparer les répertoires de test
    if comparer_repertoires(repertoire_test_original, repertoire_test_migre):
        print("Migration et génération réussies. Les fichiers correspondent.")
    else:
        print("Échec de la migration ou de la génération. Les fichiers ne correspondent pas.")

    # Supprimer les fichiers de test sauf si l'option pour les garder est spécifiée
    if not garder_tests:
        shutil.rmtree(repertoire_test_original)
        shutil.rmtree(repertoire_test_migre)
    else:
        print(f"Les fichiers de test sont conservés dans {repertoire_test_original} et {repertoire_test_migre}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrer et tester des fichiers.")
    parser.add_argument("repo_original", type=str, help="Répertoire contenant les fichiers à migrer")
    parser.add_argument("repo_migre", type=str, nargs='?', default=None, help="Répertoire où enregistrer les fichiers migrés")
    parser.add_argument("--chemin_xcfilter", type=str, required=True, help="Chemin vers le script xcfilter")
    parser.add_argument("--nombre_tests", type=int, default=2, help="Nombre de tests maximum à générer par fichier")
    parser.add_argument("--garder_tests", action="store_true", help="Garder les fichiers de test après comparaison")

    args = parser.parse_args()

    main(args.repo_original, args.repo_migre, args.chemin_xcfilter, args.nombre_tests, args.garder_tests)
