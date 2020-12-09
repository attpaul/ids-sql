
# -*-coding:utf-8 -*
# Hypotheses :

#- les requêtes qu'on voit ne contiennent pas d'attaque
#- les injections sont composées d’un seul token et c'est toujours le même type de token pour un template (si un template demande un nombre, on ne verra jamais de chaîne de caractère)
#- il y a entre zéro et deux trous dans une requête. S'il y en a deux, ils sont séparés par au moins un token.
#- NEW chaque injection n’est pas unique mais le panel d’injection est exhaustif


#########################
######  IMPORT  #########
#########################


import sqlparse

#########################
######  CONSTANT  #######
#########################

REQ1 = 'select * FROM table WHERE user = 2 and id = 5'
REQ2 = "SELECT * FROM table WHERE user=9"
REQ3 = "SELECT * FROM table3 WHERE id=13"
REQ4 = "SELECT * FROM table WHERE user=2 AND password=truc"

def main():
    print('\n')
    print(REQ3)
    print('\n')
    token_re = sqlparse.tokenize(REQ3,'utf-8')
    #token_re = sqlparse.parse(REQ1)[0]
    
    token3 = sqlparse.parse(REQ3)[0]
    print(list(token_re))
    print('\n')
    print(token3.tokens)
    print('\n')

    


if __name__ == '__main__':
    main()
