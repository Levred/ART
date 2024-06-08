from vtam import xcfilter as xcf
import os
import difflib
def test_fichier(input :str,output:str,verif:str,marqueurs:dict) :
    xcf.main(input,output,marqueurs,[''],True,True)
    with open(output,'r',encoding='utf-8') as f1:
        f1_text = f1.read()
    with open(verif,'r',encoding='utf-8') as f2:
        f2_text = f2.read()
    # Find and print the diff:
    diff = ''
    try:
        for line in difflib.unified_diff(f1_text, f2_text, fromfile='file1', tofile='file2', lineterm=''):
            if line != '':
                diff += line + '\n'
        assert diff == ''
    finally :
        print(diff)