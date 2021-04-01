# importing the requests library 
import requests, json, io, time, sys, getopt
from Algos.algoStaging import load_json_data, load_in_req

from rich.console import Console
from rich.table import Table

#récupération du fichier de requête test
#print(testQueries[0]["query"])
API_ENDPOINT = "http://127.0.0.1:5000/query"
  
def testTime():
    responseTimeList = [] 

    tDebutTest = time.time()
    
    testQueries = load_json_data("sqlQueriesProd.json")[0]["queries"]

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

def testAccuracy() :
    console = Console()
    table = Table(show_header=True, header_style="bold")
    table.add_column("A\\R", style="bold")
    table.add_column("Positive")
    table.add_column("Negative")
    results = {
        "TP" : 0,
        "TN" : 0,
        "FP" : 0,
        "FN" : 0
    }
    queries = load_json_data("sqlQueriesProd.json")[0]["queries"]
    for query in queries :
        r = requests.post(
            url = API_ENDPOINT, 
            data = { "testing" : True, **query }
        ).json()
        results[r["result"]] += 1
        if r["result"]=="FP" :
            print("\nFP query : ",query)
    table.add_row("Positive", str(results['TP']), str(results['FP']))
    table.add_row("Negative", str(results['FN']), str(results['TN']))
    console.print(table)
    return results

if __name__ == "__main__" :
    try : 
        opts, _ = getopt.getopt(sys.argv[1:], 'ta', ['time', 'accuracy'])
        if not opts :
            print('Usage : python3 test.py [-at] [--time] [--accuracy]')
            sys.exit(2) 
        for opt,value in opts :
            if opt == '--accuracy' or opt == '-a' :
                testAccuracy()
            elif opt == '--time' or opt == '-t' :
                testTime()
    except getopt.GetoptError :
        print('Usage : python3 test.py [-at] [--time] [--accuracy]')
        sys.exit(2)