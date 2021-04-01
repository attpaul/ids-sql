import os
import sys, getopt
import mysql.connector
import time
from math import floor

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from flask import Flask,render_template, request
from rich.console import Console
from rich.table import Table
from rich import inspect
from hashlib import sha1

from Algos.algoStaging import load_json_data, load_in_req, tokenize_one_req, tokenize_all_req, make_groups, find_hole_in_groups, display_holes, match_group, write_learnt_templates2json
from Algos.algoProd import templateMatch, buildLearntTemplates, isQuerySafe

try : 
  opts, _ = getopt.getopt(sys.argv[1:], '', ['debug='])
  debug = False
  for opt,value in opts :
    if opt == '--debug' :
      debug = bool(value)
except getopt.GetoptError :
  print('Usage : python3 app.py [--debug=...]')
  sys.exit(2)
 
app = Flask(__name__)

console = Console()

if debug : 
  console.print("[bold yellow]Debug Mode active.[/bold yellow]")

compteur = 0
seuil = 3
currentHash = ''
 
@app.route('/load', methods=["GET"])
def load() :
  global tokens
  global groups
  global templates
  req_from_json = load_json_data("../sqlQueriesLearn.json")

  REQ = load_in_req(req_from_json)

  tokens = tokenize_all_req(REQ)

  groups = make_groups(tokens)

  if debug :
    console.print(groups)

  templates = find_hole_in_groups(groups, tokens)
  
  if debug :
    display_holes(templates)

  write_learnt_templates2json(templates)

  console.print('[bold yellow] Loading successful. [/bold yellow]')

  return 'successfully loaded'

@app.route('/learn', methods=['POST'])
def learn() :
  global tokens
  global groups
  global templates
  global compteur
  global seuil

  q = request.form['query']

  console.print("\n[bold green]Learning :[/bold green]", q, "\n")

  console.print("Tokenizing req...")

  token = list(tokenize_one_req(q))

  console.print("Matching group...")

  match_group(token, groups, tokens)

  console.print(groups)

  compteur +=1 

  if compteur >= seuil :
    compteur = 0
    console.print("Regenerating templates...")
    templates = find_hole_in_groups(groups, tokens)
    display_holes(templates)
    write_learnt_templates2json(templates)

  return "success !"

@app.route('/query', methods=['POST'])
def query() :
  q = request.form['query']
  isInjection = request.form.get("SQLia") == "true" or False
  isTest = request.form.get("testing") or False
  
  console.print("\n[bold red]Query :[/bold red]", q)

  executeQuery = verifyQuery(q)
  
  if isTest :
    return {
      "isSQLia" : isInjection,
      "isExecuted" : executeQuery,
      "result" : ((isInjection and not executeQuery) and "TP") or ((not isInjection and executeQuery) and "TN") or ((isInjection and executeQuery) and "FN") or ((not isInjection and not executeQuery) and "FP")
    }
  elif executeQuery :
    return {
      "status" : 200,
      "message" : "success"
    }
  else :
    return {
      "status" : 403,
      "message" : "Unauthorized request"
    }


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == "POST":
      details = request.form
      userName = details['fname']
      userPassword = details['lname']
      query = "INSERT INTO users (user_name, user_password) VALUES ('%s', '%s')" %(userName, userPassword)
      executeQueries(query)
      return 'success'
  return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == "POST":
      details = request.form
      userName = details['fname']
      userPassword = details['lname']
      if 'use-ids' in details :
        useIds = True
      else :
        useIds = False
      query = "SELECT * FROM users WHERE user_name='%s' AND user_password='%s';" %(userName,userPassword)
      startTime = time.time()
      serverResponse = executeQueries(query, idsRunning=useIds)
      totalTime = time.time() - startTime
      if serverResponse == False :
        return render_template("SQLiaDetected.html", invalidQuery = query)
      if debug :
        print("DB response :\n%s" %(serverResponse or "No matching user in DB"))
      return render_template('loginResponse.html', tupleResults = serverResponse, time=floor(totalTime*1000))
  return render_template('login.html')

@app.route('/user')
def userProfile() :   
  username = request.args.get('id')
  password = request.args.get('pwd')
  query = "SELECT * FROM users WHERE user_name='%s' AND user_password='%s';" %(username,password)
  serverResponse = executeQueries(query)
  if serverResponse == False :
    return render_template("SQLiaDetected.html", invalidQuery = query)
  if debug : 
    print("DB response :\n%s" %(serverResponse or "No matching user in DB"))
  return render_template('loginResponse.html', tupleResults = serverResponse)
  

def verifyQuery(query) :
  global currentHash
  global templatesList

  if debug : 
    console.print('Comparing hashes...')
  newHash = hashFile('data/learntTemplates.json')
  if currentHash != newHash :
    if debug :
      console.print('Hashes are different, file has been updated, regenerating...')
    templatesList = buildLearntTemplates()
    currentHash = newHash
  else : 
    if debug :
      console.print('hashes identical, continuing...')

  executeQuery = False

  matchedTemplate, isQuerySafe = templateMatch(query, templatesList, debug=debug)

  if not matchedTemplate :
    console.print(console.print("\n[bold red]Request doesn't match any template. Request denied.[/bold red]\n"))

  elif not isQuerySafe :
    console.print("\n[bold red]Request has been detected as unsafe. Request denied.[/bold red]\n")

  else :
    if debug :
      console.print("\n[bold green]Request matched template :[/bold green]\n")
      console.print(matchedTemplate)
    console.print("\n[bold green]Request approved.[/bold green]\n")
    executeQuery = True

  return executeQuery

def hashFile(fileToHash, BLOCKSIZE=65536) :
  sha = sha1()

  with open(fileToHash, 'rb') as file :
    buf = file.read(BLOCKSIZE)
    while len(buf) > 0 :
      sha.update(buf)
      buf = file.read(BLOCKSIZE)
  
  return sha.hexdigest()

def executeQueries(query, idsRunning=True) :
  config = {
        'user': 'root',
        'password': '',
        'host': '127.0.0.1',
        'database': 'ids_test',
        'raise_on_warnings': True
        }
  
  if idsRunning and not verifyQuery(query) :
    return False

  results = []
  cnx = mysql.connector.connect(**config)
  cursor = cnx.cursor()
  if debug :
    print("\nStatement : "+query)
  for result in cursor.execute(query, multi=True) :
    results.append(cursor.fetchall())
  cnx.commit()
  cursor.close()
  cnx.close()
  return results



if __name__ == "__main__":
  app.run(host='localhost', port=5000, debug=True)


