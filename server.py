
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://sk4865:7210@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("""SELECT m.merchantname, p.productname, p.productid, s.price
    FROM merchants m, products p, sells s
    WHERE m.merchantid = s.merchantid AND p.productid = s.productid;
  """)
  sells = []
  for result in cursor:
    sells.append(result)  # can also be accessed using result[0]
  cursor.close()

  context = dict(data = sells)

  cursor = g.conn.execute("""SELECT *
    FROM products p;
  """)
  products = []
  for result in cursor:
    products.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(product = products)

  cursor = g.conn.execute("""SELECT c.creditcardtype
    FROM credit_cards c;
  """)
  creditcards = []
  for result in cursor:
    creditcards.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(creditcard = creditcards)

  cursor = g.conn.execute("""SELECT c.bank
    FROM credit_cards c;
  """)
  banks = []
  for result in cursor:
    banks.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(bank = banks)

  return render_template("index.html", **context)

@app.route('/search', methods=['POST'])
def search():
  product = request.form['products']
  creditcard = request.form['creditcard']
  bank = request.form['bank']
  coupon = request.form['coupontype']
  # g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  cursor = g.conn.execute("""SELECT m.merchantname, m.merchantid, p.productname, p.productid, s.price
    FROM merchants m, products p, sells s
    WHERE m.merchantid = s.merchantid AND p.productid = s.productid;
  """)

  offers = []
  for result in cursor:
    offers.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = offers)

  cursor = g.conn.execute("""SELECT t.thirdpartyname
    FROM thirdparty t;
  """)
  thirdparty = []
  for result in cursor:
    thirdparty.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(thirdParty = thirdparty)

  cursor = g.conn.execute("""SELECT *
    FROM manufacturers;
  """)
  manu = []
  for result in cursor:
    manu.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(manufacturers = manu)

  return render_template("another.html", **context)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  couponid = request.form['couponid']
  endtime = request.form['endtime']
  multiple = request.form['multiple']

  providers = request.form['providers']
  if (providers != "merchants"):
    providerid = request.form['providerid']
  mercantid = request.form['merchantid']
  productid = request.form['productid']
  price = request.form['price']

  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/another')

@app.route('/delete', methods=['POST'])
def delete():
  couponid = request.form['couponid']
  g.conn.execute('DELETE FROM Coupons WHERE couponid = (%s);', couponid)
  return redirect('/another')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
