# Manuel utilisateur pour l'outil de migration

## Introduction
Cet outil de migration permet de convertir des fichiers contenant des marqueurs spécifiques en une nouvelle version utilisant des structures conditionnelles `if-else`. L'outil peut également générer des fichiers de test pour vérifier que les fichiers migrés produisent les mêmes résultats que les fichiers d'origine.

### Contenu du projet

- `migration.py`: Script pour migrer des fichiers en remplaçant les marqueurs par des structures `if-else`.
- `migrer_et_tester.py`: Script pour migrer des dossiers et générer des fichiers de test pour verifier que les fichier migrés engendrent la même chose que les originaux. 


## Utilisation

### Script de migration (`migration.py`)

Ce script migre des fichiers en remplaçant les marqueurs par des structures `if-else`.

#### Execution

```
python migration.py [INPUT_FILE] [OUTPUT_FILE] [--prefixe]
```

#### Exemple

```
python migration.py exemple/original.py exemple/fichier_migré.py
```

### Script de migration et test (`migrer_et_tester.py`)

Ce script migre des fichiers, génère des fichiers de test et compare les résultats pour vérifier que les fichier migrés engendrent la même chose que les originaux. 

#### Execution

```
python migrer_et_tester.py "source_directory" "target_directory" --xcfilter_path "path_to_xcfilter.py" --nombre_tests 3 --garder_tests --prefixe
```

- `SOURCE_DIRECTORY`: Répertoire contenant les fichiers à migrer.
- `TARGET_DIRECTORY`: Répertoire où enregistrer les fichiers migrés.
- `--xcfilter_path`: Chemin vers le fichier `xcfilter`.
- `--nombre_tests`: Nombre de combinaisons maximales à tester (par défaut 2, 0 est une valeur valable).
- `--garder_tests`: Conserver les fichiers de test après comparaison.
- `--prefixe`: Choisir le prefixe des marqueurs à traiter (par défaut sera //). Le mot clé auto permet de le déterminer automatiquement.
#### Exemple

```
python migrer_et_tester.py ".tests\exemple" ".tests\exemple_migré" --xcfilter_path ".\ART\vtam\xcfilter.py" --nombre_tests 3 --garder_tests --prefixe //
```

### Explication des étapes

1. **Migration des fichiers**: `migrer_et_tester.py` utilise `migration.py` pour convertir les fichiers du répertoire source en la nouvelle version dans le répertoire cible.
2. **Génération des tests**: Le script génère des fichiers de test à partir des fichiers d'origine et des fichiers migrés en utilisant `xcfilter.py`.
3. **Comparaison des résultats**: Le script compare les fichiers de test générés pour vérifier la cohérence entre les fichiers d'origine et les fichiers migrés.
4. **Nettoyage**: Si l'option `--garder_tests` n'est pas spécifiée, les fichiers de test sont supprimés après la comparaison.