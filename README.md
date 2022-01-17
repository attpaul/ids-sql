# Projet IDS Injection SQL

## Introduction

Projet de detection d'injections SQL

Paul ATTAL, Romain BLANC, Alexandre de BEAUDRAP

Realise sous l'encadrement de Pierre-Francois GIMENEZ

## Installation

Ce projet necessite python 3.
Apres avoir clone le repo, installez les dependencies : 

```
pip3 install -r requirements.txt
```

Puis, pour lancer le serveur : 
```
cd Proxy
python3 app.py [--debug=bool]
```

## Usage

Vous pouvez acceder au serveur via le port 5000.

Les routes disponibles sont pour l'instant : 

* /load (GET) : A query en premier, permet de load les quelques requetes pre-chargees dans le serveur (pour avoir un peu de matiere)

* /learn (POST) : Alogorithme de staging, permet de faire apprendre une nouvelle requete au serveur. 

* /query (POST) : Algorithme de prod, permet d'envoyer une requete au serveur qui decide de la laisser passer (ou non). Cette route n'est pas connecte a une vraie DB donc si la requete passe, vous aurez juste un status 200 et non une reponse de la DB.

* /test (POST) : Route utilisee par le fichier de test, pas utile en tant que telle.

* /register, /login (GET, POST), /user (GET) : Requetes utilisees par l'interface graphique, voir localhost:5000/login



## Testing
Vous pouvez tester le fonctionnement du proxy ainsi : 
 1. Lancer le serveur
 2. Faire une requete sur la route /load
 3. Utiliser le fichier test.py pour tester l'accuracy ou le temps de reponse : 
  - accuracy : python3 test.py -a [or --accuracy]
  - time : python3 test.py -t [or --time]
