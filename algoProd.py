import re
import json
import algov0


TEMPLATES_LIST = []
newQueriesBuffer = ["SELECT bcct FROM users WHERE login=OR AND pin='pw1';"]
DEBUG = True 


def buildLearntTemplates() :
    with open('learntTemplates.json') as json_file:
        templates = json.load(json_file)
    for e in templates :
        newTemplate = ""
        for k in range(len(e["tokens"])) :
            if k in e["holes"] :
                newTemplate += ".*"
            else :
                newTemplate += re.escape(e["tokens"][k][1]) # Echappement de certains caratères

        templateDictionary = {}
        templateDictionary["template"] = newTemplate
        templateDictionary["tokens"] = e["tokens"]
        templateDictionary["holes"] = e["holes"]
         
        TEMPLATES_LIST.append(templateDictionary)


def templateMatch(query, templatesList) :
    for k in range(len(templatesList)):
        #print(k, " template", templatesList[k]["template"])
        m = re.compile(templatesList[k]["template"])
        match = m.match(query)
        if (match and isQuerySafe(query,templatesList[k])) :
            print("Un template correspondant à cette requête a été trouvé : ", templatesList[k])
            return templatesList[k]
    print("Impossible de trouver un template appris correspondant à cette requête")
    return False
            

def isQuerySafe(query, template) :
    if DEBUG : 
        print("Vérification sur les injections SQL :")
        print("Query : ", query)
        print("template : ", template)

    queryTokens = list(algov0.tokenize_one_req(query))
    queryTokensString =[]
    for singleToken in queryTokens :
        queryTokensString.append([singleToken[0].__str__(), singleToken[1]])
    
    # 1er vérification sur la taille de la liste de tokens
    if(len(queryTokensString)!=len(template["tokens"])) :
        if DEBUG : print("Comparaison des taille de liste de token : les tailles ne correspondent pas")
        return False
    # 2nd vérification sur les type de tokens
    else :
        for k in range(len(queryTokensString)) :
            if (queryTokensString[k][0] != template["tokens"][k][0]) : #idée d'amélioration pour éviter comparaison de string : hash table sur les tables du lexer
                if DEBUG : 
                    print("Comparaison des types de token : les types de token ne correspondent pas")
                    print("Type de token attendu : ", template["tokens"][k][0])
                    print("Type de token trouvé : ", queryTokensString[k][0])
                return False
        return True
    
   

def main() :
    buildLearntTemplates()
    while (len(newQueriesBuffer) !=0 ) :
        templateMatch(newQueriesBuffer.pop(0), TEMPLATES_LIST)

    

main()
    

