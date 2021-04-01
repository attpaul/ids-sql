import re
import json
import Algos.algoStaging



newQueriesBuffer = ["SELECT bcct FROM users WHERE login=OR AND pin='pw1';"]

def buildLearntTemplates() :
    TEMPLATES_LIST = []
    with open('data/learntTemplates.json') as json_file:
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
    return TEMPLATES_LIST


# Cette fonction retourne un template (isTemplateMatch, isQuerySafe).
# isTemplateMatch est True si la requete match au moins un template. 
# isQuerySafe vaut True si la requete est identifiee comme legitime.
def templateMatch(query, templatesList, debug=False) :
    isTemplateMatch = False
    for k in range(len(templatesList)):
        #print(k, " template", templatesList[k]["template"])
        m = re.compile(templatesList[k]["template"])
        match = m.match(query)
        if (match) :
            isTemplateMatch = True
            if debug :
                print("Un template correspondant à cette requête a été trouvé : ", templatesList[k])
            if isQuerySafe(query,templatesList[k]) :
                return (isTemplateMatch, templatesList[k])
    return (isTemplateMatch, False)
            

def isQuerySafe(query, template, debug=False) :
    if debug : 
        print("Vérification sur les injections SQL :")
        print("Query : ", query)
        print("template : ", template)

    queryTokens = list(Algos.algoStaging.tokenize_one_req(query))
    queryTokensString =[]
    for singleToken in queryTokens :
        queryTokensString.append([singleToken[0].__str__(), singleToken[1]])
    
    # 1er vérification sur la taille de la liste de tokens
    if(len(queryTokensString)!=len(template["tokens"])) :
        if debug : print("Comparaison des taille de liste de token : les tailles ne correspondent pas")
        return False
    # 2nd vérification sur les type de tokens
    else :
        for k in range(len(queryTokensString)) :
            if (queryTokensString[k][0] != template["tokens"][k][0]) : #idée d'amélioration pour éviter comparaison de string : hash table sur les tables du lexer
                if debug : 
                    print("Comparaison des types de token : les types de token ne correspondent pas")
                    print("Type de token attendu : ", template["tokens"][k][0])
                    print("Type de token trouvé : ", queryTokensString[k][0])
                return False
        return True
    
   

def main() :
    TEMPLATES_LIST = buildLearntTemplates()
    while (len(newQueriesBuffer) !=0 ) :
        templateMatch(newQueriesBuffer.pop(0), TEMPLATES_LIST)

if __name__ == "__main__":
    main()