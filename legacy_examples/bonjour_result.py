def hello_w():
    print('Hello World ... :-(')


def hello(interlocuteurs):

    for interlocuteur in interlocuteurs:
        print(f'Hello {interlocuteur} !')

    if interlocuteurs == [] :
        print('Alone...  As always ')


hello_w()
interlocuteurs = []
fini = False
while not fini :
    recu = str(input('Qui est là ?'))
    if recu != '' :
        interlocuteurs.append(recu)
    else:
        fini = True

hello(interlocuteurs)