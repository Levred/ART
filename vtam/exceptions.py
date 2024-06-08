#définition des exceptions

class InvalidUsage(Exception):
    pass

class IncorrectVerificationFile(Exception):
    pass

class InvalidTemplate(Exception):
    def __init__(self, value):
        self.value = value
 
    def __str__(self):
        return(repr(self.value))

class NoVariantFile(Exception):
    pass

class BadVariantFile(Exception):
    def __init__(self, value):
        self.value = value
 
    def __str__(self):
        return(repr(self.value))