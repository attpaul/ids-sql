
# -*-coding:utf-8 -*
# Hypotheses :

#- les requêtes qu'on voit ne contiennent pas d'attaque
#- les injections sont composées d’un seul token et c'est toujours le même type de token pour un template (si un template demande un nombre, on ne verra jamais de chaîne de caractère)
#- il y a entre zéro et deux trous dans une requête. S'il y en a deux, ils sont séparés par au moins un token.
#- NEW chaque injection n’est pas unique mais le panel d’injection est exhaustif


#########################
######  IMPORT  #########
#########################

import json
import io

from io import TextIOBase

from sqlparse import tokens
from sqlparse.keywords import SQL_REGEX
from sqlparse.utils import consume

#########################
######  GLOBALES  #######
#########################




#########################
######  CONSTANT  #######
#########################["select *", "select 2"] # 

req_from_json = []

REQ = []

"""
    "select * FROM table WHERE user = 2", 
    "SELECT * FROM table WHERE user = 9", 
    "SELECT * FROM table3 WHERE id=13", 
    "SELECT * FROM table WHERE user=2 AND password=truc"]

"""
token= []
groupes= []



########################
######  CLASS   ########
########################

#https://github.com/andialbrecht/sqlparse/blob/master/sqlparse/lexer.py
# This code is based on the SqlLexer in pygments.
# http://pygments.org/
# It's separated from the rest of pygments to increase performance
# and to allow some customizations.



class Lexer:
    """Lexer
    Empty class. Leaving for backwards-compatibility
    """

    @staticmethod
    def get_tokens(text, encoding=None):
        """
        Return an iterable of (tokentype, value) pairs generated from
        `text`. If `unfiltered` is set to `True`, the filtering mechanism
        is bypassed even if filters are defined.
        Also preprocess the text, i.e. expand tabs and strip it if
        wanted and applies registered filters.
        Split ``text`` into (tokentype, text) pairs.
        ``stack`` is the initial stack (default: ``['root']``)
        """
        if isinstance(text, TextIOBase):
            text = text.read()

        if isinstance(text, str):
            pass
        elif isinstance(text, bytes):
            if encoding:
                text = text.decode(encoding)
            else:
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    text = text.decode('unicode-escape')
        else:
            raise TypeError("Expected text or file-like object, got {!r}".
                            format(type(text)))

        iterable = enumerate(text)
        for pos, char in iterable:
            for rexmatch, action in SQL_REGEX:
                m = rexmatch(text, pos)

                if not m:
                    continue
                elif isinstance(action, tokens._TokenType):
                    yield action, m.group()
                elif callable(action):
                    yield action(m.group())

                consume(iterable, m.end() - pos - 1)
                break
            else:
                yield tokens.Error, char



########################
######  FUNCTION  ######
########################




def tokenize_one_req(sql, encoding=None):
    """Tokenize sql.
    Tokenize *sql* using the :class:`Lexer` and return a 2-tuple stream
    of ``(token type, value)`` items.
    """
    return Lexer().get_tokens(sql, encoding)


def tokenize_all_req():
    #transformation en token de toutes les requetes
    for i in range(len(REQ)):
        token.insert(i,list(tokenize_one_req(REQ[i])))


def is_token_equal(token1,token2):
    if len(token1) != len(token2):
        return False
    for i in range(len(token1)):
        if token1[i][0] != token2[i][0]:
            return False
    return True


def makes_groupes():
    #regroupement des groupes de token identique
    alreadygone = []
    for i in range(len(REQ)):
        if alreadygone.count(i)==0:
            groupecreated = []
            groupecreated.append(i)
            for j in range(i+1,len(REQ)):
                if is_token_equal(token[i] , token[j]):
                    groupecreated.append(j)
                    alreadygone.append(j)
            groupes.append(groupecreated)





def load_json_data(filename,liste_de_req):
    with io.open(filename, encoding='utf-8') as read_file:
        liste_de_req.append(json.load(read_file))
    #print(liste_de_req)
      
def load_in_req():
    for i in range(len(req_from_json[0]['queries'])):
        REQ.append( req_from_json[0]['queries'][i]['query'].encode('utf-8'))
   

def display_req_dataset():
    #Affichage des requetes de test
    for i in range(len(REQ)):
        print(REQ[i])

def display_req_dataset_json():
    #print(req_from_json)
    for i in range(len(req_from_json[0]['queries'])):
        print(req_from_json[0]['queries'][i]['query'])
        

def display_token_dataset():
    #affichage de tout les requetes tranformé en token
    for i in range(len(REQ)):
        print("\n")
        print(token[i])

def display_groupes_dataset():
    #affichage de tout les requetes tranformé en token
    print("\n")
    for i in range(len(groupes)):
        print(groupes[i])

################################################################################################################
################################################################################################################

#########################
######  PROGRAMME  ######
#########################

def main():

   load_json_data("sqlQueries.json",req_from_json)
   load_in_req()
   #display_req_dataset()
   #display_req_dataset_json()
   tokenize_all_req()
   #display_token_dataset()
   makes_groupes()
   display_groupes_dataset()




if __name__ == '__main__':
    main()



