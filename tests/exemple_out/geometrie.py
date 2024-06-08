# -*- coding: iso-8859-1 -*-
# Constructeur
# Les accesseurs
# �galit� physique et logique
# h�ritage et red�finition
# en montrer un exemple
# faire un groupe
# classes abstraites ou interfaces ? voir abc Abstract Base (?) Class

# if ObjetGeometrique START DELETE
# if ABSTRACT START DELETE
import abc
# ABSTRACT STOP DELETE
class ObjetGeometrique<(ABSTRACT)>(metaclass=abc.ABCMeta)<(/ABSTRACT)>:
# if ABSTRACT START DELETE
	@abc.abstractmethod
# ABSTRACT STOP DELETE
	def translater(self, dx, dy):
# if LEVE_EXCEPTION START DELETE
		raise NotImplementedError
# else START DELETE
		pass
# LEVE_EXCEPTION STOP DELETE
# if ABSTRACT START DELETE
	@abc.abstractmethod
# ABSTRACT STOP DELETE
	def __str__(self):
# if LEVE_EXCEPTION START DELETE
		raise NotImplementedError
# else START DELETE
		pass
# LEVE_EXCEPTION STOP DELETE
# ObjetGeometrique STOP DELETE

# if Point START DELETE
import math
class Point<(OG)>(ObjetGeometrique)<(/OG)>:
# if DOC START DELETE
	"""
	D�finition d'un point dans le plan, avec une abscisse x et une ordonn�e y.
	"""
# DOC STOP DELETE
	def __init__(self, x=0, y=0):
# if DOC START DELETE
		""" initialiser un point
		Args:
			self: le point � initialiser
			x: sa nouvelle abscisse
			y: sa nouvelle ordonn�e

		>>> Point(2, 4)
		Point(2.0, 4.0)
		"""
# DOC STOP DELETE
		self.x = float(x)
		self.y = float(y)

# if REPR START DELETE
	def __repr__(self):
		return f"Point({self.x}, {self.y})"

# REPR STOP DELETE
	def __str__(self):
		return f"({self.x} ; {self.y})"

# if DOC START DELETE
	def __eq__(self, autre):
		return self.x == autre.x and self.y == autre.y

# DOC STOP DELETE
	def translater(self, dx, dy):
		self.x += dx
		self.y += dy

	def distance(self, autre):
		dx2 = (self.x - autre.x) ** 2
		dy2 = (self.y - autre.y) ** 2
		return math.sqrt(dx2 + dy2)
# Point STOP DELETE

# if Segment START DELETE
class Segment<(OG)>(ObjetGeometrique)<(/OG)>:
	def __init__(self, e1: Point, e2: Point):
		self.extremite1 = e1
		self.extremite2 = e2

# if REPR START DELETE
	def __repr__(self):
		return f"Segment({repr(self.extremite1)}, {repr(self.extremite2)})"

# REPR STOP DELETE
	def __str__(self):
		return f"[{self.extremite1} - {self.extremite2}]"

	def translater(self, dx: float, dy: float):
		self.extremite1.translater(dx, dy)
		self.extremite2.translater(dx, dy)

	def longueur(self):
		return self.extremite1.distance(self.extremite2)
# Segment STOP DELETE

# if PointNomme START DELETE
class PointNomme(Point):	# La classe PointNomm� h�rite de Point
	def __init__(self, nom, x=0, y=0):
		super().__init__(x, y)	# initialiser la partie Point du PointNomm�
		self.nom = nom				# un nouvel attribut

# if REPR START DELETE
	def __repr__(self):	
		return f"PointNomme({repr(self.nom)}, {self.x}, {self.y})"

# REPR STOP DELETE
	def __str__(self):				# red�finition
		return f"{self.nom}:{super().__str__()}"
									# utilisation de la version de __str__ dans Point

	def nommer(self, nouveau_nom):		# une nouvelle m�thode
		self.nom = nouveau_nom
# PointNomme STOP DELETE

# if PointNommeDelegation START DELETE
class PointNommeDelegation:
	def __init__(self, nom, x=0, y=0):
		self.pt = Point(x, y)	# le Point du PointNomm�
		self.nom = nom			# le nom
# if not REPR START DELETE
	def __repr__(self):	
		return f"PointNomme({repr(self.nom)}, {self.x}, {self.y})"

# else START DELETE
	def __repr__(self):	
		return f"PointNomme({repr(self.nom)}, {self.x}, {self.y})"

# REPR STOP DELETE


	def __str__(self):				# adaptation
		return f"{self.nom}:{self.pt}"

	def nommer(self, nouveau_nom):		# une nouvelle m�thode
		self.nom = nouveau_nom

	def __getattr__(self, name):
		return getattr(self.pt, name)
# PointNommeDelegation STOP DELETE

# if test_PointNommeDelegation START DELETE
def test_PointNommeDelegation():
	pn = PointNommeDelegation('A', 10, 20)
	assert pn.nom == 'A'
	assert pn.x == 10
	assert pn.y == 20
	assert str(pn) == 'A:(10.0 ; 20.0)'
	assert Point.__str__(pn) == '(10.0 ; 20.0)'
# if REPR START DELETE
	assert Point.__repr__(pn) == 'Point(10.0, 20.0)'
# REPR STOP DELETE
	assert isinstance(pn, PointNommeDelegation)
	assert not isinstance(pn, Point)
# test_PointNommeDelegation STOP DELETE


def nsqrt(x, n):
	""" compute n times the square root of x """
	r = x
	for i in range(n):
		r = math.sqrt(r)
	return r

def nsquare(x, n):
	""" compute n times the square of x """
	r = x
	for i in range(n):
		r = r ** 2
	return r

def essai2():
	n = 20
	sq = nsqrt(2.0, n)
	print('nsqrt(2.0, ', n, ') = ', sq)
	sq2 = nsquare(sq, n)
	print('nsquare --> ', sq2)

p1 = None
def setup_func():
	global p1
	p1 = Point(0, 2)

def precision_test():
	assert 2 == nsquare(nsqrt(2, 20), 20)


# @with_setup(setup_func)
def translater_test():
	p1 = Point(0, 2)
	print('p1 = ', p1)
	p1.translater(2, 6)
	assert p1.x == 2
	assert p1.y == 8

def translater2_test():
	p1 = Point(0, 2)
	print('p1 = ', p1)
	p1.translater(2.5, 6.1)
	print('p1 = ', p1)
	assert p1.x == 2.5
	assert p1.y == 8.1


# if exemple START DELETE
def exemple():
	# cr�er les points sommets du triangle
# if AVEC_NOMS START DELETE
	p1 = PointNomme("A", 3, 2)
	p2 = PointNomme("S", 6, 9)
# else START DELETE
	p1 = Point(3, 2)
	p2 = Point(6, 9)
# AVEC_NOMS STOP DELETE
	p3 = Point(11, 4)

	# cr�er les trois segments
	s12 = Segment(p1, p2)
	s23 = Segment(p2, p3)
	s31 = Segment(p3, p1)

	# cr�er le barycentre
	sx = (p1.x + p2.x + p3.x) / 3.0
	sy = (p1.y + p2.y + p3.y) / 3.0
# if AVEC_NOMS START DELETE
	barycentre = PointNomme("G", sx, sy)
# else START DELETE
	barycentre = Point(sx, sy)
# AVEC_NOMS STOP DELETE

	# construire le sch�ma
	schema = [s12, s23, s31, barycentre];

	# afficher le sch�ma
	for elt in schema:
		print(elt)
# exemple STOP DELETE

def essai():
	p1 = Point(1, 2)
	print(p1)

	# Il y a bien composition entre Point et les r�els repr�sentants les attributs
	p1bis = Point(p1.x, p1.y)
	print(p1bis)
	print('Notation imp�rative : ', Point.__str__(p1))
	p1bis.x = 2
	print(p1)
	print(p1bis)

	p2 = Point(4, 6)
	print(p2)
	s12 = Segment(p1, p2)
	print("s12 = {}, longueur = {}".format(s12, s12.longueur()))
	print("distance(p1, p2) = {}" .format(p1.distance(p2)))
	p2.translater(-3, 6)
	print(p2)
	print("s12 = {}, longueur = {}".format(s12, s12.longueur()))
	print("distance(p1, p2) = {}" .format(p1.distance(p2)))
	pn1 = PointNomme("A", 1, 2)
	print("pn1 = {}".format(pn1))

	s12bis = Segment(pn1, p2)
	print('s12bis :', repr(s12bis))
	print("s12bis = {}, longueur = {}".format(s12bis, s12bis.longueur()))
	pn1.x = 5;
	print("s12bis = {}, longueur = {}".format(s12bis, s12bis.longueur()))
	s12bis.translater(0, 0);

	q1 = Point(1, 2)
	print("p1 == q1 : ", p1 == q1)
	pn1 = PointNomme("A", 1, 2)
	print("pn1 == q1 : ", pn1 == q1)
	print("q1 == pn1 : ", q1 == pn1)
	exemple()
	og = ObjetGeometrique()


if __name__ == "__main__":
	import doctest
	doctest.testmod()
	exemple()
	if False:
		s = Segment(PointNomme('A', 1.0, 2.0), Point(1.0, 12.0))
		print(s)
		essai()
