import unittest
from tests import test_diff as td
else_src = 'src/tests/fichiers_tests/else.txt'
else_out = 'src/tests/fichiers_tests/else_result.txt'

elif_src = 'src/tests/fichiers_tests/elif.txt'
elif2_src = 'src/tests/fichiers_tests/elif2.txt'
elif_out = 'src/tests/fichiers_tests/elif_result.txt'

class test_else_simple(unittest.TestCase):
    def test_True(self):
        td.test_fichier(else_src,else_out,'src/tests/fichiers_tests/else_1.txt',{'A': True})
    def test_False(self):
        td.test_fichier(else_src,else_out,'src/tests/fichiers_tests/else_2.txt',{'A': False})
    def test_None(self):
        td.test_fichier(else_src,else_out,else_src,{})

class test_else_emplie(unittest.TestCase):
    def test_False_False(self):
        td.test_fichier(else_src,else_out,'src/tests/fichiers_tests/else_3.txt',{'A':False,'C':False})
    def test_True_True(self):
        td.test_fichier(else_src,else_out,'src/tests/fichiers_tests/else_4.txt',{'A':True,'B':True})

class test_elif_simple(unittest.TestCase):    
    def test_True(self):
        td.test_fichier(elif_src,elif_out,'src/tests/fichiers_tests/elif_1.txt',{'A': True,'B': False})
    def test_False_True(self):
        td.test_fichier(elif_src,elif_out,'src/tests/fichiers_tests/elif_2.txt',{'A': False,'B': True})
    def test_False_False(self):
        td.test_fichier(elif_src,elif_out,'src/tests/fichiers_tests/elif_3.txt',{'A': False,'B': False,'C' : True})  
    def test_inter(self):
        td.test_fichier(elif_src,elif_out,'src/tests/fichiers_tests/elif_4.txt',{'A': False}) 

class test_elif_empile(unittest.TestCase):
    def test_empile1(self) :
        td.test_fichier(elif2_src,elif_out,'src/tests/fichiers_tests/elif2_1.txt',{'A':False,'B':True,'C':True})
    def test_empile2(self) :
        td.test_fichier(elif2_src,elif_out,'src/tests/fichiers_tests/elif2_2.txt',{'A':False,'B':True,'C':False,'D':True})