
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
from Lexer import Lexer

#########################
######  GLOBALES  #######
#########################

templates = []

"""
    "select * FROM table WHERE user = 2", 
    "SELECT * FROM table WHERE user = 9", 
    "SELECT * FROM table3 WHERE id=13", 
    "SELECT * FROM table WHERE user=2 AND password=truc"]

"""

########################
######  FUNCTION  ######
########################


def tokenize_one_req(sql, encoding=None):
    """Tokenize sql.
    Tokenize *sql* using the :class: `Lexer` and return a 2-tuple stream
    of ``(token type, value)`` items.
    """
    return Lexer().get_tokens(sql, encoding)


def tokenize_all_req(REQ, display=False):
    '''
    transformation en token de toutes les requetes
    '''
    tokens = []
    for i in range(len(REQ)):
        tokens.insert(i,list(tokenize_one_req(REQ[i])))
    if display :
        display_token_dataset(REQ, tokens)
    return tokens


def is_token_equal(token1,token2):
    '''
    determine si deux tokens sont identiques
    '''
    if len(token1) != len(token2):
        return False
    for i in range(len(token1)):
        if token1[i][0] != token2[i][0]:
            return False
    return True


def makes_groups(REQ, tokens, display=False):
    '''
    regroupement des groupes de token identique
    '''
    groups = []
    alreadygone = []
    for i in range(len(REQ)-1):
        if alreadygone.count(i)==0:
            groupecreated = []
            groupecreated.append(i)
            for j in range(i+1,len(REQ)):
                if is_token_equal(tokens[i] , tokens[j]):
                    groupecreated.append(j)
                    alreadygone.append(j)
            groups.append(groupecreated)
    if display :
        display_groups_dataset(groups)
    return groups

def find_hole_in_groups(groups, tokens):
    for i in range(len(groups)):
        if len(groups[i])>1:
            make_sub_groups_template(groups[i], tokens)
    

def make_sub_groups_template(group, tokens):
    tested_holes=[]
    created_templates = []
    for i in range(len(group)-1):
        for j in range(i+1,len(group)):
            tested_holes.append(find_hole(tokens[group[i]] ,tokens[group[j]]))
    #print(tested_holes)

    if tested_holes[0]!=[] :
        if len(tested_holes)<2 :
            created_templates.append(tested_holes[0])
        else:
            hole_liste = []
            for i in range(len(tested_holes)):
                for j in range(len(tested_holes[i])):
                    if(tested_holes[i][j] not in hole_liste):
                        hole_liste.append(tested_holes[i][j])
            hole_liste.sort()
            created_templates.append(hole_liste)

        created_templates.append(tokens[group[0]])
        templates.append(created_templates)
        
           


#print(find_hole(list(tokenize_one_req("select * FROM table WHERE user = 2")),list(tokenize_one_req("SELECT * FROM table WHERE user = 9"))))
def find_hole(req1,req2):
    holes = []
    for i in range(len(req1)):
        if req1[i][1] != req2[i][1]:
            holes.append(i)
    return holes



def load_json_data(filename, display=False):
    liste_de_req = []
    with io.open(filename, encoding='utf-8') as read_file:
        liste_de_req.append(json.load(read_file))
    if display :
        display_req_dataset_json(liste_de_req)
    return liste_de_req
      
def load_in_req(req_from_json, display=False):
    REQ = []
    for i in range(len(req_from_json[0]['queries'])):
        REQ.append( req_from_json[0]['queries'][i]['query'].encode('utf-8'))
    if display :
        display_req_dataset(REQ)
    return REQ

def display_req_dataset(REQ):
    #Affichage des requetes de test
    for i in range(len(REQ)):
        print(REQ[i])

def display_req_dataset_json(req_from_json):
    #print(req_from_json)
    for i in range(len(req_from_json[0]['queries'])):
        print(req_from_json[0]['queries'][i]['query'])
        

def display_token_dataset(REQ, tokens):
    #affichage de tout les requetes tranformé en token
    for i in range(len(REQ)):
        print("\n")
        print(tokens[i])

def display_groups_dataset(groups):
    #affichage de tout les requetes tranformé en token
    print("\n")
    for i in range(len(groups)):
        print(groups[i])

def display_templates():
    #affichage de tout les templates (paire liste de positions trous + liste de token)
    print("\n")
    for i in range(len(templates)):
        print(templates[i])

def write_learnt_templates2json() :
    jsonTemplates = []
    for i in range(len(templates)):
        template = {}
        template["holes"] = templates[i][0]
        tokens = []
        for singleToken in templates[i][1] :
            tokens.append([singleToken[0].__str__(),singleToken[1]]) #Conversion des types de token en string pour pouvoir les écrire dans le json
        template["tokens"] = tokens
        jsonTemplates.append(template)
    with open('learntTemplates.json', 'w') as outfile:
        json.dump(jsonTemplates, outfile)


#########################
######  PROGRAMME  ######
#########################


def main():
    
    #print(find_hole(list(tokenize_one_req("select * FROM table WHERE user = 2")),list(tokenize_one_req("SELECT * FROM table WHERE user = 9"))))
    req_from_json = load_json_data("sqlQueries.json")

    REQ = load_in_req(req_from_json)

    tokens = tokenize_all_req(REQ)

    groups = makes_groups(REQ, tokens)
    print("groupes : ",groups)

    find_hole_in_groups(groups, tokens)

    display_templates()

    write_learnt_templates2json()
    #print(list(tokenize_one_req(REQ[0])))
    #print(list(tokenize_one_req(REQ[1])))
    #print(find_hole(list(tokenize_one_req(REQ[0])),list(tokenize_one_req(REQ[1]))))
    # print(REQ[10])
    # print(REQ[11])
    # print(REQ[13])
    # print(REQ[14])

if __name__ == '__main__':
    main()
