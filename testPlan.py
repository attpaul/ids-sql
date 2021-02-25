# importing the requests library 
import requests, json, io, time

#Parametres :
debug = True

#import de fonctions de algoStaging
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

#récupération du fichier de requête test
testQueries = load_json_data("sqlQueries.json")[0]["queries"]
#print(testQueries[0]["query"])

  
def testProd():
    responseTimeList = []
    # defining the api-endpoint  
    API_ENDPOINT = "http://127.0.0.1:5000/query"

    tDebutTest = time.time()
    
    for query in testQueries :

        # data to be sent to api 
        data = {'query':query["query"]} 

        #Lancement du chrono :
        t0 = time.time()
        # sending post request and saving response as response object 
        r = requests.post(url = API_ENDPOINT, data = data)
        #On stoppe le chrono à la reception de la réponse du serveur :
        t1 = time.time()
        delta = t1-t0
        responseTimeList.append(delta) 

        # extracting response text  
        pastebin_url = r.text
        print("Requête malveillante : %s"%query["SQLia"])
        print("Nombre de trous : %d"%query["numberOfInputs"]) 
        print("Requête envoyée au serveur :\n%s"%query["query"])
        print("\n")
        print("Temps de réponse : %f"%delta)
        print("Réponse du serveur :%s"%pastebin_url)
        print(" ---------------------------------------------------- \n")

    tFinTest = time.time()
    tTotal = tFinTest-tDebutTest

    print("******************************* Résumé du test *****************************")
    print("Temps total du test pour %d requêtes : %f"%(len(testQueries), tTotal))
    print("Temps de réponse moyen : %f"%(sum(responseTimeList)/len(responseTimeList)))
    print("Temps de réponse max : %f"%max(responseTimeList))
    print("Requête correspondante :\n %s\n"%testQueries[responseTimeList.index(max(responseTimeList))])
    print("Temps de réponse min : %f"%min(responseTimeList))
    print("Requête correspondante :\n %s\n"%testQueries[responseTimeList.index(min(responseTimeList))])


testProd() 