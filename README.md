# Manuel utilisateur VTAM

## Introduction

### Motivations
VTAM (Variantes de Textes Avec Marqueurs) est un outil permettant d’engendrer plusieurs variantes d’un document à partir d’un template de façon cohérente.
Le fichier de template contient des marqueurs qui définissent des zones que l’on peut choisir d’inclure ou non selon les marqueurs spécifiés lors de la génération du document.


VTAM propose également à l’utilisateur de vérifier la compatibilité entre les marqueurs, à l’aide d’une syntaxe simple (z3).

### Versions

Une première version a été développée avec le language de template Mako, elle se situe dans le dossier **mako/**
Cette première version inclut une vérification des marqueurs avec un syntaxe type FDL (Feature Description Language).


Dans la deuxième version, le "langage" des templates VTAM est défini grâce à une grammaire PEG et le traitement s’effectue grâce à la libraire Parsimonious. Les sources se trouvent dans le dossier **vtam/**
La vérification des marqueurs se fait en fournissant un fichier sous la syntaxe z3, et permet également de déduire des marqueurs à partir de ceux précisés par l’utilisateur

La troisième version est une amélioration de la deuxième, elle ajoute plus de souplesse dans l'écriture des balises, les blocs if/elif/else, la gestion des variantes et le traitement de dossier entier. En parallèle de cette version une interface graphique à été développée, elle permet de faire tout ce que que cette troisième version fait en visualisant le résultat avant de l'enregistrer.
## Contenu du dossier src

- legacy_examples : des exemples de templates

- tests : contient les test unitaires

- vtam : package contenant toutes les sources

  - utils : scripts de parsing

  - vtamparser : grammaire d'un template VTAM et manipulation de l'AST qui en résulte

    - grammar.py : grammaire des templates
    - var_grammar.py : grammaire des fichiers de variantes
    - var_visitor.py : visiteur des fichiers de variantes
    - visitor.py : visiteur des templates  

  - consistency.py : Vérification de la cohérence et déduction de marqueurs

  - exceptions.py : exceptions nécessaires aux scripts

  - interfaceGraphique.py : permet de lancer l'interface graphique

  - marker_ui.py : Gestion de classes spéciales de l'interface graphique

  - visitor_ui.py : visiteur spécifique à l'interface

  - xc_directory.py : gestion des dossier pour xcfilter.py

  - xcextract.py : permet d'extraire un morceau de template

  - xcfilter.py : permet d'appliquer des marqueurs à un template

     

## Installation

Il suffit d'exécuter la commande : 

```
make install
```

ou bien manuellement

```
pip3 install parsimonious z3-solver
```

La version de python utilisée est la 3.8.10.

La version pour la v3 est la 3.10.5

## Utilisation

#### Lancer les tests

```
make test
```



#### xcfilter

Génère un document à partir du template.

```
./xcfilter.py  [-h] [-m CHECK_FILE.marker] [-v VARIANT_FILE.var] [-f] [-i] [-dir] [TEMPLATE_FILE] [OUTPUT_FILE] +|-[MARKER_1]|@[VARIANT_1] ... +|-[MARKER_N]|@[VARIANT_N]
```

exemple : 

```
./xcfilter.py templates/afficher_entier.mako xcfilter_results/afficher_entier.adb +TABLEAU -CHAINEE -GENERIQUE
```

Les marqueurs qui n'ont pas été spécifiés seront conservés afin d'obtenir une version intermédiaire.



#### xcextract

Extrait le code entre les marqueurs // BEGIN EXTRACT marqueur  et // END EXTRACT marqueur 

```
./xcextract.py [INPUT_FILE] [OUTPUT_FILE] [MARKER]
```



#### migrate (version mako uniquement)

Migre les anciens templates vers la version mako

```
./migrate.py [INPUT_FILE] [OUTPUT_FILE]
```

exemple :

```
./migrate.py legacy_examples/afficher_entier.adb migration_results/afficher_entier.mako
```



## Template

Un template peut contenir les marqueurs suivants : 

- Marqueur "bloc":  
  Note le '//' peut être remplacé par n'importe quels caractères non blancs depuis la version 3
  - version classique :
   
    ```
    // <expression> START DELETE
    contenu à inclure/exclure
    // NOM_MARQUEUR STOP DELETE
    ```
  - version complète :

    ```
    // if <expresion1> START DELETE
    contenu à inclure si <expression1> exclure sinon
    // elif <expression2> START DELETE
    contenu à inclure si non <expression1> et si <expression2> exclure sinon
    // else START DELETE
    contenu à inclure si non (<expression1> et <expression2>) exclure sinon
    // NOM_MARQUEUR STOP DELETE
    ```

    **Remarque** : le `if` dans la première balise est optionel de mêmme pour `NOM_MARQUEUR` dans la dernière ligne.

- Marqueur "inline" :

  ```
  ...<(expression)>contenu<(/expression)>...
  ```



Une expression est un identifiant de marqueur éventuellement précédée de l'opérateur "not".



Exemple de template : 

```
// MARQUEUR1 START DELETE
contenu1
// MARQUEUR1 STOP DELETE
<(not MARQUEUR1)>contenu2<(/not MARQUEUR1)>
```


La commande ./xcfilter avec +MARQUEUR1 engendre "contenu1".

La commande avec -MARQUEUR1 engendre "contenu2".
## Utilisation de regroupements de marqueurs

Pour simplifier le traitement de grand fichiers on peut utiliser des variantes.

Pour créer une variante il faut la définir dans un fichier à part (muni de l'extension `.var`) de la manière suivante :
```
@NOM_VARIANTE :
  +|- NOM_MARQUEUR1 / @VARIANTE1
  ...
  +|- NOM_MARQUEURN / @VARIANTEN
```
### Usage

Pour utiliser une variante avec xcfilter.py il faut indiquer le nom du fichier la contenant dans la commande de la manière suivante :
```
./xcfilter.py -v VARIANT_FILE.var [TEMPLATE_FILE] [OUTPUT_FILE] @NOM_VARIANTE
``` 

## Vérification de la cohérence entre marqueurs

Il est probable que certains marqueurs nécessitent la présence d’autres marqueurs (implication), que
d’autres soient incompatibles (exclusion)...

### Options disponibles en ligne de commande

- "-m" : prend en argument le nom du fichier .marker ;
- "-f" : ignore toute vérification et déduction de marqueurs ;
- "-i" : ignore seulement la déduction de marqueurs

Si l’option -m n’est pas précisée, le programme cherchera le fichier default.marker dans le dossier du
programme.
On utilisera -i par exemple pour générer un fichier intermédiaire, après vérification de la cohérence,
strictement réduit aux marqueurs spécifiés par l’utilisateur.

### Format et contenu des fichiers de vérification

Le format du fichier doit être .marker, afin d’éviter les confusions avec le fichier de template fourni
également en ligne de commande.

#### Syntaxe et contraintes à respecter :
Le fichier .marker doit avoir la syntaxe exploitable par z3-python, et être formé d’implications, à savoir :

```
Implies(a, b)
Implies(c, d)
...
```

où a, b, c, d sont des marqueurs, ou bien des prédicats qui peuvent être sous la forme :

```
# Au moins 2 arguments pour chaque groupe
Or(e, f, g, ...)
And(e, f, g, ...)
Xor(e, f, g, ...)
Not(e) # Un seul argument
...
```

Exemple :
```
Implies(COULEUR, And(FIGURE, TRACE))
Implies(And(FIGURE, TRACE), INVARIANTS)
Implies(COULEUR, Xor(INVARIANTS, INSTRUMENTATION))
Implies(FIGURE, INSTRUMENTATION)
```

La première ligne signifie par exemple "Le marqueur COULEUR requiert la présence des marqueurs
FIGURE et TRACE". Si le marqueur COULEUR est spécifié, alors
- Si FIGURE ou TRACE sont indiqués comme désactivés, le solveur lèvera une incohérence ;
- Si FIGURE ou TRACE ne sont pas précisés, ils seront déduits, pour peu que cela soit cohérent avec
le reste des propriétés.

#### Exemple d'usage : 
```
./xcfilter.py -m verif.marker templates/afficher_entier.mako xcfilter_results/afficher_entier.adb +TABLEAU -CHAINEE -GENERIQUE
```
## Traitement de dossier
On peut parfois avoir besoin de traiter un ensemble de fichier utilisants les mêmes marqueurs, variantes et contraintes. Pour simplifer cette action on peut alors tous les mettre dans le même dossier avec les éventuels fichier .marker et .var.  
Le programme s'occupera alors d'ouvrir les .marker et .var et par défaut traitera tout les fichiers dont l'extension est majoritaire. Pour éviter cela il suffit d'ajouter un fichier .list qui contient à chaque ligne le nom d'un fichier à traiter.

### Usage
Pour traiter un dossier avec xcfilter il faut entrer une commande de ce type :
```
./xcfilter.py -dir nom_dossier [TEMPLATE_DIRECTORY] [OUTPUT_DIRECTORY] +|-[MARKER_1]|@[VARIANT_1] ... +|-[MARKER_N]|@[VARIANT_N]
```

## Bibliographie :

- Documentation de mako : https://docs.makotemplates.org/en/latest/
- Documentation de z3-solver : https://z3prover.github.io/api/html/classz3py_1_1_solver.html
