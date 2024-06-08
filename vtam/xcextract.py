#!/usr/bin/env python3
"""
Permet d'extraire un morceau du template délimité par des marqueurs en commentaire
ex: // EXTRACT NOM_MARQUEUR ... code à extraire ... // EXTRACT NOM_MARQUEUR END
"""

import sys
import re

def usage():
    print("Invalid usage")
    print("Usage : xcextract [INPUT_FILE] [NOM_MARQUEUR]")

if (len(sys.argv) != 3):
    usage()
else:
    marqueur = sys.argv[2]
    input_file = open(sys.argv[1])
    lines = input_file.readlines()
    write_line = False

    for line in lines:
        # Commencer a extraire
        if re.match(".*BEGIN EXTRACT %s" % (marqueur), line):
            write_line = True
        # Arreter d'extraire
        elif re.match(".*END EXTRACT %s" % (marqueur), line):
            write_line = False
        # Continuer a extraire
        elif write_line:
            print(line)