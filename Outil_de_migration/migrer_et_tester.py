import os
import shutil
import subprocess
import random
from migration import process_file, recuperer_marqueurs
from tqdm import tqdm

def creer_chaine_marqueurs(marqueurs, no_marqueurs):
    """ 
    Choisis aléatoirement les marqueurs à appliquer pour les tests en respectant l'usage des NO_marqueurs.
    Renvoie une chaîne de caractères avec le choix des marqueurs dans le format de xcfilter.
    
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
        repertoire_sortie (str): Répertoire où enregistrer le fichier généré.
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        chaine_marqueurs (str): Chaîne de caractères des marqueurs.
        test_id (int): Identifiant du test (sert à nommer le fichier de sortie).
        forcer (bool): Forcer la génération de fichiers et ignorer la vérification de la consistance.
    
    Returns:
        bool: True si le fichier a été généré avec succès, False sinon.
    """
    if not os.path.exists(chemin_fichier):
        tqdm.write(f"Le fichier d'entrée donné {chemin_fichier} n'a pas été trouvé.")
        return False

    chemin_fichier_sortie = os.path.join(repertoire_sortie, f"{os.path.basename(chemin_fichier)}_test_{test_id}")
    os.makedirs(os.path.dirname(chemin_fichier_sortie), exist_ok=True)

    cmd = [
        'python', chemin_xcfilter,
    ]
    if forcer:
        cmd.append('-f')
    cmd.extend([
        chemin_fichier,
        chemin_fichier_sortie
    ] + chaine_marqueurs.split())
    commande_str = ' '.join(cmd)

    with open("xcfilter_errors.log", "a") as error_file:
        try:
            subprocess.run(commande_str, check=True, shell=True, stdout=subprocess.PIPE, stderr=error_file, text=True)
            return True
        except subprocess.CalledProcessError:
            return False

def comparer_fichiers(chemin_fichier1, chemin_fichier2):
    """
    Compare le contenu de deux fichiers ligne par ligne.
    
    Args:
        chemin_fichier1 (str): Chemin du premier fichier.
        chemin_fichier2 (str): Chemin du second fichier.
    
    Returns:
        bool: True si les fichiers sont identiques, False sinon.
    """
    try:
        with open(chemin_fichier1, 'r', encoding='utf-8') as fichier1, open(chemin_fichier2, 'r', encoding='utf-8') as fichier2:
            lignes1 = fichier1.readlines()
            lignes2 = fichier2.readlines()

            if lignes1 != lignes2:
                for numero_ligne, (ligne1, ligne2) in enumerate(zip(lignes1, lignes2), start=1):
                    if ligne1 != ligne2:
                        tqdm.write(f"Différence à la ligne {numero_ligne} :\n{ligne1}\n{ligne2}")
                return False
    except FileNotFoundError as e:
        tqdm.write(f"Erreur : {e}")
        return False
    return True

def generer_tests_pour_fichiers(repo_original, repo_migre, repo_test_original, repo_test_migre, chemin_xcfilter, nombre_tests, forcer=True):
    """
    Génère des fichiers de test pour vérifier que le fichier migré engendre la même chose.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers originaux.
        repo_migre (str): Répertoire contenant les fichiers migrés.
        repo_test_original (str): Répertoire temporaire pour les fichiers de test originaux.
        repo_test_migre (str): Répertoire temporaire pour les fichiers de test migrés.
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        nombre_tests (int): Nombre maximum de tests à générer par fichier.
        forcer (bool): Forcer la génération de fichiers et ignorer la vérification de la consistance.
    
    Returns:
        tuple: Nombre de fichiers testés, nombre de fichiers avec des erreurs.
    """
    fichiers_testes = 0
    fichiers_erreurs = 0
    fichiers = [(root, file) for root, dirs, files in os.walk(repo_original) for file in files]
    
    for root, file in tqdm(fichiers, desc="Traitement des fichiers", unit="fichier"):
        chemin_source = os.path.join(root, file)
        chemin_relatif = os.path.relpath(chemin_source, repo_original)
        chemin_cible = os.path.join(repo_migre, chemin_relatif)
        
        if not os.path.exists(chemin_cible):
            tqdm.write(f"Le fichier migré correspondant {chemin_cible} n'a pas été trouvé.")
            continue

        fichiers_testes += 1
        fichier_a_erreur = False

        marqueurs, no_marqueurs = recuperer_marqueurs(chemin_source)[:2]
        chaines_marqueurs = [creer_chaine_marqueurs(marqueurs, no_marqueurs) for _ in range(nombre_tests)]
        
        for i, chaine_marqueurs in enumerate(tqdm(chaines_marqueurs, desc=f"Tests pour {file}", leave=False)):
            fichier_test_original = os.path.join(repo_test_original, f"{file}_test_{i + 1}")
            fichier_test_migre = os.path.join(repo_test_migre, f"{file}_test_{i + 1}")

            if not generer_fichier(chemin_source, repo_test_original, chemin_xcfilter, chaine_marqueurs, i + 1, forcer):
                tqdm.write(f"Erreur xcfilter avec le fichier original : {chemin_source}")
                fichier_a_erreur = True
                continue

            if not generer_fichier(chemin_cible, repo_test_migre, chemin_xcfilter, chaine_marqueurs, i + 1, forcer):
                tqdm.write(f"Erreur de migration avec le fichier : {chemin_cible}")
                fichier_a_erreur = True
                continue
            
            if not comparer_fichiers(fichier_test_original, fichier_test_migre):
                tqdm.write(f"Les fichiers ne correspondent pas : {fichier_test_original} et {fichier_test_migre}")
                fichier_a_erreur = True

        if fichier_a_erreur:
            fichiers_erreurs += 1

    return fichiers_testes, fichiers_erreurs

def migrer_fichiers(repo_original, repo_migre, prefixe):
    """
    Migre les fichiers d'un répertoire source vers un répertoire cible en utilisant un script de migration.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers à migrer.
        repo_migre (str): Répertoire où enregistrer les fichiers migrés.
    """
    if os.path.exists(repo_migre):
        shutil.rmtree(repo_migre)
    os.makedirs(repo_migre)
    
    fichiers = [(root, file) for root, dirs, files in os.walk(repo_original) for file in files]
    pbar = tqdm(fichiers, desc="Migration des fichiers", unit="fichier")
    
    for root, file in pbar:
        chemin_source = os.path.join(root, file)
        chemin_relatif = os.path.relpath(chemin_source, repo_original)
        chemin_cible = os.path.join(repo_migre, chemin_relatif)

        dossier_cible = os.path.dirname(chemin_cible)
        if not os.path.exists(dossier_cible):
            os.makedirs(dossier_cible)

        process_file(chemin_source, chemin_cible, prefixe)

def lister_marqueurs_repertoire(repertoire):
    """
    Liste les marqueurs et les non-marqueurs de chaque fichier dans le répertoire donné.
    
    Args:
        repertoire (str): Chemin du répertoire à analyser.
    """
    fichiers = [(root, file) for root, dirs, files in os.walk(repertoire) for file in files]
    tqdm.write(f"Traitement de {len(fichiers)} fichiers:")
    for root, file in tqdm(fichiers, desc="Liste des marqueurs", unit="fichier"):
        chemin_fichier = os.path.join(root, file)
        #marqueurs, no_marqueurs = recuperer_marqueurs(chemin_fichier)[:2]
        tqdm.write(chemin_fichier)

def main(repo_original, repo_migre, chemin_xcfilter, nombre_tests, garder_tests, prefixe):
    """
    Fonction principale pour migrer, générer des tests et comparer les fichiers.
    
    Args:
        repo_original (str): Répertoire contenant les fichiers à migrer.
        repo_migre (str): Répertoire où enregistrer les fichiers migrés.
        chemin_xcfilter (str): Chemin vers le script xcfilter.
        nombre_tests (int): Nombre maximum de tests à générer par fichier.
        garder_tests (bool): Garder les fichiers de test après comparaison.
    """
    # Donne un nom par défaut
    if repo_migre is None:
        repo_migre = f"{repo_original}_out"

    # Supprimer le répertoire cible s'il existe déjà
    if os.path.exists(repo_migre):
        shutil.rmtree(repo_migre)

    # Lister les marqueurs et non-marqueurs de chaque fichier dans le répertoire source
    lister_marqueurs_repertoire(repo_original)

    # Migrer les fichiers
    migrer_fichiers(repo_original, repo_migre, prefixe)

    repertoire_test_original = f"{repo_original}_test_original"
    repertoire_test_migre = f"{repo_migre}_test_migre"

    # Générer les fichiers de test pour l'original et les fichiers migrés
    fichiers_testes, fichiers_erreurs = generer_tests_pour_fichiers(repo_original, repo_migre, repertoire_test_original, repertoire_test_migre, chemin_xcfilter, nombre_tests)

    tqdm.write(f"{fichiers_testes} fichiers testés.")
    tqdm.write(f"{fichiers_testes - fichiers_erreurs} fichiers migrés correctement.")
    tqdm.write(f"{fichiers_erreurs} fichiers contenant des erreurs.")

    # Supprimer les fichiers de test sauf si l'option pour les garder est spécifiée
    if not garder_tests:
        shutil.rmtree(repertoire_test_original)
        shutil.rmtree(repertoire_test_migre)
    else:
        tqdm.write(f"Les fichiers de test sont conservés dans {repertoire_test_original} et {repertoire_test_migre}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migrer et tester des fichiers.")
    parser.add_argument("repo_original", type=str, help="Répertoire contenant les fichiers à migrer")
    parser.add_argument("repo_migre", type=str, nargs='?', default=None, help="Répertoire où enregistrer les fichiers migrés")
    parser.add_argument("--chemin_xcfilter", type=str, required=True, help="Chemin vers le script xcfilter")
    parser.add_argument("--nombre_tests", type=int, default=2, help="Nombre de tests maximum à générer par fichier")
    parser.add_argument("--garder_tests", action="store_true", help="Garder les fichiers de test après comparaison")
    parser.add_argument('--prefixe', type=str, default="//", help='Prefixe des marqueurs (par défaut sera //)')
    args = parser.parse_args()

    main(args.repo_original, args.repo_migre, args.chemin_xcfilter, args.nombre_tests, args.garder_tests, args.prefixe)
