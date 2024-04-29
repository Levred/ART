import unittest
import warnings
from vtam import xcfilter

class TestInline(unittest.TestCase):

    def test_simple(self):
        with warnings.catch_warnings():
            # Ignore deprecation warnings
            warnings.simplefilter("ignore", category=DeprecationWarning)

            # Test
            template = "<(INLINE)><(/INLINE)>"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "")
            
            result = xcfilter.render(template, {"INLINE": False})
            self.assertEqual(result, "")

            result = xcfilter.render(template, {})
            self.assertEqual(result, "<(INLINE)><(/INLINE)>")

    def test_contenu(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = "<(INLINE)>contenu<(/INLINE)>"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "contenu")

            template = "<(INLINE)>contenu1<(/INLINE)> contenu2"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "contenu1 contenu2")

    def test_par(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = "<((INLINE))><(/(INLINE))>"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "")

    def test_imbrique(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = "<(INLINE1)>contenu1 <(INLINE2)>contenu2 <(/INLINE2)>contenu3<(/INLINE1)>"
            result = xcfilter.render(template, {"INLINE1": True, "INLINE2": True})
            self.assertEqual(result, "contenu1 contenu2 contenu3")


class TestBlock(unittest.TestCase):

    def test_simple(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = """// BLOCK START DELETE
block
// BLOCK STOP DELETE"""
            result = xcfilter.render(template, {"BLOCK": True})
            self.assertEqual(result, "block\n")

            result = xcfilter.render(template, {"BLOCK": False})
            self.assertEqual(result, "")

            result = xcfilter.render(template, {})
            self.assertEqual(result, template)

    def test_indent(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = """// BLOCK START DELETE
    block
// BLOCK STOP DELETE"""
            result = xcfilter.render(template, {"BLOCK": True})
            self.assertEqual(result, "    block\n")

            result = xcfilter.render(template, {})
            self.assertEqual(result, template)

    def test_imbrique(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = """
// NO_FIGURE START DELETE
// INVARIANTS START DELETE

	//@ private invariant getCouleur() != null;
	//@ private invariant getCouleur() == couleur;	// invariant de liaison
// INVARIANTS STOP DELETE
	private Color couleur;	// couleur du point
// NO_FIGURE STOP DELETE"""

            result = xcfilter.render(template, {"NO_FIGURE": True, "INVARIANTS": True})
            self.assertEqual(result, """

	//@ private invariant getCouleur() != null;
	//@ private invariant getCouleur() == couleur;	// invariant de liaison
	private Color couleur;	// couleur du point
""")

class TestLogic(unittest.TestCase):
    def test_not_inline(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = "<(not INLINE)>test<(/not INLINE)>"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "")

            result = xcfilter.render(template, {"INLINE": False})
            self.assertEqual(result, "test")

            template = "<(not not INLINE)>test<(/not not INLINE)>"
            result = xcfilter.render(template, {"INLINE": True})
            self.assertEqual(result, "test")

    def test_not_block(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=DeprecationWarning)

            template = """// not BLOCK START DELETE
block
// not BLOCK STOP DELETE"""
            result = xcfilter.render(template, {"BLOCK": True})
            self.assertEqual(result, "")

            result = xcfilter.render(template, {"BLOCK": False})
            self.assertEqual(result, "block\n")

            result = xcfilter.render(template, {})
            self.assertEqual(result, template)

            template = """// not not BLOCK START DELETE
block block
// not not BLOCK STOP DELETE"""

            result = xcfilter.render(template, {"BLOCK" : True})
            self.assertEqual(result, "block block\n")

            result = xcfilter.render(template, {"BLOCK" : False})
            self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()