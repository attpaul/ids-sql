from flask import Flask,render_template, request
from flask_mysqldb import MySQL
from rich.console import Console
from rich.table import Table
from rich import inspect

from algoStaging import load_json_data, load_in_req, tokenize_one_req, tokenize_all_req, make_groups, find_hole_in_groups, display_holes, match_group, write_learnt_templates2json
from algoProd import templateMatch, buildLearntTemplates, isQuerySafe
 
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'SQL_POC'

mysql = MySQL(app)

console = Console()

compteur = 0
seuil = 3
 
@app.route('/config', methods=["POST"])
def config() :
  global mysql

  print(request.form)

  app.config['MYSQL_HOST'] = request.form['host']
  app.config['MYSQL_USER'] = request.form['user']
  app.config['MYSQL_PASSWORD'] = request.form['password']
  app.config['MYSQL_DB'] = request.form['db']
 
  mysql = MySQL(app)

  return 'ok'

@app.route('/load', methods=["GET"])
def load() :
  global tokens
  global groups
  global templates
  req_from_json = load_json_data("../sqlQueries.json")

  REQ = load_in_req(req_from_json)

  tokens = tokenize_all_req(REQ)

  groups = make_groups(tokens)

  console.print(groups)

  templates = find_hole_in_groups(groups, tokens)
  
  display_holes(templates)

  write_learnt_templates2json(templates)

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
    console.print("Regenerating templates...")
    templates = find_hole_in_groups(groups, tokens)
    display_holes(templates)
    write_learnt_templates2json(templates)

  return "success !"

@app.route('/query', methods=['POST'])
def query() :

  templatesList = buildLearntTemplates()

  q = request.form['query']

  console.print("\n[bold red]Query :[/bold red]", q, "\n")

  executeQuery = False

  matchedTemplate = templateMatch(q, templatesList)

  if not matchedTemplate :
    console.print(console.print("\n[bold red]Request doesn't match any template. Request denied.[/bold red]\n"))

  else :
    console.print("\n[bold green]Request matched template :[/bold green]\n")
    console.print(matchedTemplate)
    isSafe = isQuerySafe(q, matchedTemplate)
    if not isSafe :
      console.print("\n[bold red]Request has been detected as unsafe. Request denied.[/bold red]\n")
    else :
      console.print("\n[bold green]Request approved.[/bold green]\n")
      executeQuery = True
  
  if executeQuery :
    return {
      "status" : 200,
      "message" : "success"
    }
  else :
    return {
      "status" : 403,
      "message" : "Unauthorized request"
    }
  
  """ if executeQuery :

    cursor = mysql.connection.cursor()
    cursor.execute(q)
    mysql.connection.commit()
    result = cursor.fetchall()
    cursor.close()

    table = Table(title=('Results : {}'.format(cursor.rowcount)))

    columns = []

    for _, (x, *_) in enumerate(cursor.description) :
      table.add_column(x)
      columns.append(x)

    for _, (x,y) in enumerate(result) :
      table.add_row(x,y)

    console.print(table)

    console.print(result)

    return {
      "status": 200, 
      "columns" : columns,
      "result": list(result)
    }
 """


if __name__ == "__main__":
  app.run(host='localhost', port=8000, debug=True)
