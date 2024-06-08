# POLITE START DELETE
def hello_w():
    print('<(not SAD)>Hello World !! :-D<(/not SAD)><(SAD)>Hello World ... :-(<(/SAD)>')
# POLITE STOP DELETE


def hello(interlocuteurs):
    # not POLITE START DELETE
    print('Non')
    # not POLITE STOP DELETE

    for interlocuteur in interlocuteurs:
        print(f'Hello {interlocuteur} !')

    if interlocuteurs == [] :
        print('Alone... <(SAD)> As always <(/SAD)>')


# POLITE START DELETE
hello_w()
# POLITE STOP DELETE
interlocuteurs = []
# IHM START DELETE
fini = False
while not fini :
    recu = str(input('Qui est là ?'))
    if recu != '' :
        interlocuteurs.append(recu)
    else:
        fini = True
# IHM STOP DELETE

hello(interlocuteurs)