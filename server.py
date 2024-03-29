
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


  cursor = g.conn.execute("""SELECT *
    FROM credit_cards c;
  """) #c.bank, c.creditcardtype
  creditcards = []
  for result in cursor:
    creditcards.append(result)  # can also be accessed using result[0]
  cursor.close()
  context.update(creditcard = creditcards)

  # cursor = g.conn.execute("""SELECT c.bank
  #   FROM credit_cards c;
  # """)
  # banks = set()
  # for result in cursor:
  #   banks.add(result)  # can also be accessed using result[0]
  # cursor.close()
  # context.update(bank = banks)

  return render_template("index.html", **context)

@app.route('/search', methods=['POST'])
def search():
  print('***********************')
  print(request.form)
  print('***********************')
  product = request.form['products']
  creditcard = request.form['creditcard']
  print('This is credit card input:', creditcard)
  # bank = request.form['bank']
  coupon = request.form['coupontype']

  if (product == ''):
      return redirect("/")

  if (coupon == "percentage"):
    cursor = g.conn.execute("""WITH Percent_Offers (provider, discountRate, coupon_from) AS (
      SELECT m.merchantName as Provider, pc.discountRate, 'Merchants'
      FROM Merchants m, merchant_offer mo, percentage_coupons pc
      WHERE m.merchantid = mo.merchantid AND mo.productid = %s AND mo.couponid = pc.couponid

      UNION

      SELECT tpo.thirdPartyName as Provider, pc.discountRate, 'Third Party'
      FROM Third_Party_Offer tpo, percentage_coupons pc
      WHERE tpo.productid = %s AND tpo.couponid = pc.couponid

      UNION

      SELECT ma.manufacturename as Provider, pc.discountRate, 'Manufacturers'
      FROM Manufacturers ma, Manufacturer_Offer mao, percentage_coupons pc
      WHERE ma.manufactureid = mao.manufactureid AND mao.productid = %s AND mao.couponid = pc.couponid
      )
      SELECT *
      FROM Percent_Offers AS po
      ORDER BY po.discountRate DESC;
      """, product, product, product)
  elif (coupon == "absval"):
    cursor = g.conn.execute("""WITH Value_Offers (provider, discountValue, coupon_from) AS (
      SELECT m.merchantName as Provider, avc.discountValue, 'Merchants'
      FROM Merchants m, merchant_offer mo, absolute_value_coupons avc
      WHERE m.merchantid = mo.merchantid AND mo.productid = %s AND mo.couponid = avc.couponid

      UNION

      SELECT tpo.thirdPartyName as Provider, avc.discountValue, 'Third Party'
      FROM Third_Party_Offer tpo, absolute_value_coupons avc
      WHERE tpo.productid = %s AND tpo.couponid = avc.couponid

      UNION

      SELECT ma.manufacturename as Provider, avc.discountValue, 'Manufacturers'
      FROM Manufacturers ma, Manufacturer_Offer mao, absolute_value_coupons avc
      WHERE ma.manufactureid = mao.manufactureid AND mao.productid = %s AND mao.couponid = avc.couponid
      )
      SELECT *
      FROM Value_Offers AS po
      ORDER BY po.discountValue DESC;
      """, product, product, product)
  else:
    cursor = g.conn.execute("""WITH Value_Offers (coupontype, provider, discount, coupon_from) AS (
      SELECT 'Absolute Value', m.merchantName as Provider, avc.discountValue, 'Merchants'
      FROM Merchants m, merchant_offer mo, absolute_value_coupons avc
      WHERE m.merchantid = mo.merchantid AND mo.productid = %s AND mo.couponid = avc.couponid

      UNION

      SELECT 'Absolute Value', tpo.thirdPartyName as Provider, avc.discountValue, 'Third Party'
      FROM Third_Party_Offer tpo, absolute_value_coupons avc
      WHERE tpo.productid = %s AND tpo.couponid = avc.couponid

      UNION

      SELECT 'Absolute Value', ma.manufacturename as Provider, avc.discountValue, 'Manufacturers'
      FROM Manufacturers ma, Manufacturer_Offer mao, absolute_value_coupons avc
      WHERE ma.manufactureid = mao.manufactureid AND mao.productid = %s AND mao.couponid = avc.couponid

      UNION
      SELECT 'Percentage', m.merchantName as Provider, pc.discountRate, 'Merchants'
      FROM Merchants m, merchant_offer mo, percentage_coupons pc
      WHERE m.merchantid = mo.merchantid AND mo.productid = %s AND mo.couponid = pc.couponid

      UNION

      SELECT 'Percentage', tpo.thirdPartyName as Provider, pc.discountRate, 'Third Party'
      FROM Third_Party_Offer tpo, percentage_coupons pc
      WHERE tpo.productid = %s AND tpo.couponid = pc.couponid

      UNION

      SELECT 'Percentage', ma.manufacturename as Provider, pc.discountRate, 'Manufacturers'
      FROM Manufacturers ma, Manufacturer_Offer mao, percentage_coupons pc
      WHERE ma.manufactureid = mao.manufactureid AND mao.productid = %s AND mao.couponid = pc.couponid
      )
      SELECT *
      FROM Value_Offers AS po
      ORDER BY po.coupontype DESC, po.discount DESC;
      """, product, product, product, product, product, product)


  output = []
  for result in cursor:
    output.append(result)  # can also be accessed using result[0]
  cursor.close()


 ## pick the credit card of interest ##
  if (creditcard != ''):
    print(creditcard, type(creditcard))
    bank_inp, card_inp = creditcard.split(";")
    card_inp = ' '.join(card_inp.split(','))
    bank_inp = ' '.join(bank_inp.split(','))
    print(bank_inp, card_inp, 'finally!!!!')
    cursor2 = g.conn.execute("""
      SELECT c.cashback, c.Bank, c.creditCardType
      FROM merchants m, sells s, card_offer_discount c
      WHERE s.productid=%s AND m.merchantid = s.merchantid AND c.merchantcategory = ANY(m.category) 
      AND c.creditCardType=%s AND c.BANK=%s
      ORDER BY c.cashback DESC;
      """,product, card_inp, bank_inp)
  else:
    cursor2 = g.conn.execute("""
      SELECT c.cashback, c.Bank, c.creditCardType
      FROM merchants m, sells s, card_offer_discount c
      WHERE s.productid=%s AND m.merchantid = s.merchantid AND c.merchantcategory = ANY(m.category)
      ORDER BY c.cashback DESC;
      """,product)
  output.append('Credit Cards with Cashback')
  output.append('Cashback (%), Bank, Card')
  for result in cursor2:
    output.append(result)
  cursor2.close()

  context = dict(data = output)
  # g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return render_template("index.html", **context)

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

  cursor = g.conn.execute("""SELECT *
    FROM third_party t;
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
  coupontype = request.form['coupontype']
  couponid = request.form['couponid']
  endtime = request.form['endtime']
  multiple = request.form['multiple']
  value = request.form['value']

  g.conn.execute('INSERT INTO Coupons VALUES (%s, %s, %s);', couponid, endtime, multiple)
  
  if (coupontype == 'percentage'):
    g.conn.execute('INSERT INTO Percentage_coupons VALUES ({}, {});'.format(value, couponid))
  else:
    g.conn.execute('INSERT INTO Absolute_Value_coupons VALUES ({}, {});'.format(value, couponid))

  providers = request.form['providers']
  if (providers != "merchants"):
    thirdpartyid = request.form['thirdpartyid']
    manuid = request.form['manuid']
  mercantid = request.form['merchantid']
  productid = request.form['productid']
  price = request.form['price']

  if(providers == 'thirdParty'):
    g.conn.execute('INSERT INTO third_party_offer VALUES (\'{}\', {}, {}, {}, {});'.format( 
      thirdpartyid, couponid, productid, mercantid, price))
  elif (providers == 'manufacturers'):
    g.conn.execute('INSERT INTO manufacturer_offer VALUES ({}, {}, {}, {}, {});'.format( 
      couponid, manuid, productid, mercantid, price))
  else:
    g.conn.execute('INSERT INTO merchant_offer VALUES ({}, {}, {}, {});'.format( 
      couponid, mercantid, productid, price))
  
  return redirect('/another')

@app.route('/delete', methods=['POST'])
def delete():
  couponid = request.form['couponid']
  g.conn.execute('DELETE FROM Coupons WHERE couponid = %s;', couponid)
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
