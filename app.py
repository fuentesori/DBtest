import os
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template, g, Response


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.debug = True
DATABASEURI = "postgresql://postgres:ok@localhost/4111T"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
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
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

#login page and and handling login errors
@app.route('/')
def index():
    return render_template("login.html")

@app.route('/check_login', methods=['POST'])
def checklogin():
    #set up variables
    link = []
    loginuid = request.form['uid']
    checkuser = null
    #SQL query the user login
    cmd ="SELECT uid from users where uid=%s"
    cursor = g.conn.execute(cmd,loginuid[0])
    for result in cursor:
        checkuser = result

        #check if loginuid is good in database
        if int(checkuser[0]) == int(loginuid):
            link = 'portfolio'
            #set global uid if uid is good
            global uid
            uid = int(checkuser[0])
        else:
            link = 'badlog'
    return redirect(url_for(link, passuid=int(loginuid), portfolioid=0))

@app.route('/incorrectlogon/<passuid>/<portfolioid>')
def badlog(passuid, portfolioid):
    return render_template("incorrectlogon.html", baduid=passuid)

#User portfolio
@app.route('/portfolio/<passuid>/<portfolioid>', methods=['POST'])
def populateportfolio(passuid,portfolioid):
    global Gportfolioid
    Gportfolioid = float(request.form['portfolio'])
    return redirect(url_for('portfolio', passuid=uid, portfolioid=Gportfolioid))

@app.route('/portfolio/<passuid>/<portfolioid>')
def portfolio(passuid, portfolioid):
    #obtain user's list of portfolios
    cmd ="SELECT portfolioid FROM portfolio where uid=%s"
    cursor = g.conn.execute(cmd, uid)
    portfolios = []
    for result in cursor:
        portfolios.append(result[0])
    cursor.close()
    #render user's portfoliodata
    cmd ="SELECT * FROM stock_transactions where uid=%s and portfolioid=%s"
    cursor = g.conn.execute(cmd, uid, portfolioid)
    transactions = []
    for result in cursor:
        transactions.append(result)
    cursor.close()
    cmd = "SELECT * FROM users where uid=%s"
    cursor = g.conn.execute(cmd,uid)
    userinfo = []
    for result in cursor:
        userinfo=result
    cursor.close()

    cmd = "SELECT ticker, current_price FROM us_stock ORDER BY ticker"
    cursor = g.conn.execute(cmd)
    tickers = []
    for result in cursor:
        tickers.append(result)
    cursor.close()

    cmd = "SELECT bankaccountid FROM bank_accounts WHERE uid=%s ORDER BY bankaccountid"
    cursor = g.conn.execute(cmd,uid)
    bankaccountids = []
    for result in cursor:
        bankaccountids.append(result[0])
    cursor.close()

    return render_template("portfolio.html", portfolios=portfolios, transactions=transactions, user=userinfo, tickers=tickers, bankaccountids=bankaccountids)

@app.route('/post_trade', methods=['POST'])
def post_trade():
    users = [request.form['uid'], request.form['fname'], request.form['lname'], request.form['address'], request.form['phone'], request.form['ssn']]
    cmd = 'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (users[0], users[1], users[2], users[3], users[4], users[5], users[6], users[7], users[8], users[9], users[10]));
    return redirect(url_for('portfolio', uid=uid))

@app.route('/post_cash', methods=['POST'])
def post_cash():
    amount=[]
    tdate = ""
    #find biggest primary key id and increment by 1
    cmd = 'SELECT MAX(transactionid) FROM cash_transactions'
    cursor = g.conn.execute(cmd)
    for result in cursor:
        transactionid = result[0] + 1
    #set transfer data
    tdate = datetime.date.today()
    tdate = str(tdate)
    #determine whether amount is positive or negative
    if request.form['order']=='In':
        amount = float(request.form['amount'])
    else:
        amount = float(request.form['amount'])*-1
    #insert transaction into database
    cash = [transactionid, tdate, uid, float(request.form['bankaccountid']), Gportfolioid, amount]
    cmd = 'INSERT INTO cash_transactions VALUES (%s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (cash[0], cash[1], cash[2], cash[3], cash[4], cash[5]));
    return redirect(url_for('portfolio', passuid=uid, portfolioid=Gportfolioid))



#New User page and adding new user to database
@app.route('/newuser')
def newuser():
    return render_template("add_user.html")

@app.route('/usercreated/<uid>')
def usercreated(uid):
    return render_template("usercreated.html", uid=uid)

@app.route('/post_user', methods=['POST'])
def post_user():
    #find biggest primary key id and increment by 1
    cmd = 'SELECT MAX(uid) FROM users'
    cursor = g.conn.execute(cmd)
    for result in cursor:
        uid = result[0] + 1
    #fill out user data and store in database
    users = [uid, request.form['fname'], request.form['lname'], request.form['address'], request.form['phone'], request.form['ssn']]
    cmd = 'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (users[0], users[1], users[2], users[3], users[4], users[5]));
    return redirect(url_for('usercreated', uid=uid))

#Existing user profile, view and update user data
@app.route('/profile')
def profile():
    cmd = "SELECT * FROM users where uid=%s"
    cursor = g.conn.execute(cmd,uid)
    userdata = []
    for result in cursor:
        userdata=result
    cursor.close()
    return render_template("profile.html", userdata=userdata)

#@app.route('/profile/successfulupdate')
#def update_user():






if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='localhost')
  @click.argument('PORT', default=5000, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
