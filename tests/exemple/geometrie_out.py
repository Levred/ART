# -*- coding: iso-8859-1 -*-
# Constructeur
# Les accesseurs
#  galit  physique et logique
# h ritage et red finition
# en montrer un exemple
# faire un groupe
# classes abstraites ou interfaces ? voir abc Abstract Base (?) Class

# ObjetGeometrique START DELETE
# ABSTRACT START DELETE
import abc
# ABSTRACT STOP DELETE
class ObjetGeometrique<(ABSTRACT)>(metaclass=abc.ABCMeta)<(/ABSTRACT)>:
# ABSTRACT START DELETE
	@abc.abstractmethod
# ABSTRACT STOP DELETE
	def translater(self, dx, dy):
# LEVE_EXCEPTION START DELETE
		raise NotImplementedError
# LEVE_EXCEPTION STOP DELETE
# if not LEVE_EXCEPTION START DELETE
# 		pass
# else START DELETE
# 		raise NotImplementedError
# LEVE_EXCEPTION STOP DELETE
# if not LEVE_EXCEPTION START DELETE
# 		pass
# else START DELETE
# LEVE_EXCEPTION STOP DELETE
