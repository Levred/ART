from exceptions import InvalidUsage,NoVariantFile,BadVariantFile
from tkinter import Text
def parse(markers:list,variantes: dict[list] = None,marqueurs: dict = {},dejavu: dict = {},variant_name: str = '',report : Text= None):
    """
    Parse les arguments donnés en ligne de commande                                                  
    Les arguments sont attendus au format                                               
    [TEMPLATE_FILE] [OUTPUT_FILE] +|-[MARQUEUR_1] ... +|-[MARQUEUR_N]          
    
    Returns
    ----------
    input_file
    output_file
    marqueurs
        {MARQUEUR_1: True/False, ... MARQUEUR_N: True/False}
    """
    for m in markers:
        name = m[1:]
        if m[0] == '+':
            if name not in marqueurs.keys():
                marqueurs[name] = True
            elif report != None:
                afficher_message(report, m, name)
            else :
                print(f'{m} has been ignored because {name} has been specified before')
        elif m[0] == '-':
            if name not in marqueurs.keys():
                marqueurs[name] = False
            elif report != None:
                afficher_message(report, m, name)
            else :
                print(f'{m} has been ignored because {name} has been specified before')
        elif m[0] == '@':
            if variantes != None:
                if name in dejavu.keys() :
                    raise BadVariantFile(f'\nReccursion error while reading variant,@{name} has already been called, but it\'s called in {variant_name}')
                else:
                    dejavu[name] = f'in @{variant_name}'
                    parse(variantes[name],variantes,marqueurs,dejavu,name)

            else :
                raise NoVariantFile
        else:
            raise InvalidUsage()
    return marqueurs

def afficher_message(report: Text, m:str, name:str) -> None:
    report.config(state='normal')
    report.insert('insert',f'{m} has been ignored because {name} has been specified before\n')
    report.yview('scroll',len(report.get('0.0','insert')),'units')
    report.config(state='disabled')
