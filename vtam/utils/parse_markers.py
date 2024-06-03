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
        action, name = m[0], m[1:]
        if action in '+-@':
            if name not in marqueurs:
                marqueurs[name] = (action == '+')
                if action == '@' and variantes:
                    if name in dejavu:
                        raise BadVariantFile(f'\nRecursion error while reading variant,@{name} has already been called, but it\'s called in {variant_name}')
                    dejavu[name] = f'in @{variant_name}'
                    parse(variantes[name], variantes, marqueurs, dejavu, name)
            else:
                if report:
                    afficher_message(report, m, name)
                else:
                    print(f'{m} has been ignored because {name} has been specified before')
        else:
            raise InvalidUsage()
    return marqueurs


def afficher_message(report: Text, m:str, name:str) -> None:
    report.config(state='normal')
    report.insert('insert',f'{m} has been ignored because {name} has been specified before\n')
    report.yview('scroll',len(report.get('0.0','insert')),'units')
    report.config(state='disabled')
