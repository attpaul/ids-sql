# Projet IDS Injection SQL

## Introduction

Projet de detection d'injections SQL

Paul ATTAL, Romain BLANC, Alexandre DE BEAUDRAP

Realise sous l'encadrement de Pierre-Francois GIMENEZ

## Installation

Ce projet necessite python 3.
Apres avoir clone le repo, executez : 

```
pip3 install sqlparse, flask, rich
```

Puis, pour lancer le serveur : 
```
cd Proxy
flask run
```

## Usage

Vous pouvez acceder au serveur via le port 5000.

Les routes disponibles sont pour l'instant : 

* /load (GET) : A query en premier, permet de load les quelques requetes pre-chargees dans le serveur (pour avoir un peu de matiere)

* /learn (POST) : Alogorithme de staging, permet de faire apprendre une nouvelle requete au serveur. 

* /query (POST) : Algorithme de prod, permet d'envoyer une requete au serveur qui decide de la laisser passer (ou non). Pour l'instant, avec ces requetes toutes faites, il n'est pas connecte a une vraie DB donc si la requete passe, vous aurez juste un status 200 et non une reponse de la DB.