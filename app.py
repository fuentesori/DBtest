import os
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template, g, Response
global Gportfolioid
Gportfolioid = 0
global uid
uid = 0

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
    password = request.form['password']
    checkuser = ""
    #SQL query the user login
    cmd ="SELECT uid from users where uid=%s"
    cursor = g.conn.execute(cmd,loginuid)
    for result in cursor:
        checkuser= result
    #check if loginuid is good in database
    if checkuser != "":
        cmd ="SELECT password from users where uid=%s"
        cursor = g.conn.execute(cmd,loginuid)
        for result in cursor:
            checkpassword= result
        if checkpassword[0]==password:
            link = 'portfolio'
            #set global uid if uid is good
            global uid
            uid = checkuser[0]
        else:
            link = 'badpw'
    else:
        link = 'badlog'
    return redirect(url_for(link, passuid=int(loginuid), portfolioid=0))

@app.route('/incorrectlogon/<passuid>/<portfolioid>')
def badlog(passuid, portfolioid):
    return render_template("incorrectlogon.html", baduid=passuid)

@app.route('/incorrectpw/<passuid>/<portfolioid>')
def badpw(passuid, portfolioid):
    return render_template("incorrectpw.html", baduid=passuid)

#User portfolio
@app.route('/portfolio/return')
def portfolioreturn():
    return redirect(url_for('portfolio', passuid=uid, portfolioid=Gportfolioid))

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
    cmd ="SELECT t1.ticker, t1.netshares, t1.netcost, t2.current_price, (t1.netshares * t2.current_price) AS currentvalue FROM (SELECT ticker, SUM(shares) As netshares, SUM(shares * open_position_price) AS netcost FROM stock_transactions WHERE uid=%s and portfolioid=%s GROUP BY ticker) AS t1, (SELECT ticker, current_price  FROM us_stock) AS t2 WHERE t1.ticker = t2.ticker;"
    cursor = g.conn.execute(cmd, float(uid), float(Gportfolioid))
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

    return render_template("portfolio.html", portfolioid=Gportfolioid, portfolios=portfolios, transactions=transactions, user=userinfo, tickers=tickers, bankaccountids=bankaccountids)

@app.route('/post_portfolio', methods=['POST'])
def post_portfolio():
    #find biggest primary key id and increment by 1
    cmd = 'SELECT MAX(portfolioid) FROM portfolio'
    cursor = g.conn.execute(cmd)
    for result in cursor:
        portfolioid = result[0] + 1
    portfolio = [portfolioid, uid, 0]
    cmd = 'INSERT INTO portfolio VALUES (%s, %s, %s)';
    g.conn.execute(cmd, (portfolio[0], portfolio[1], portfolio[2]));
    return redirect(url_for('portfolio', passuid=uid, portfolioid=Gportfolioid))

@app.route('/post_bankaccount', methods=['POST'])
def post_bankaccount():
    #find biggest primary key id and increment by 1
    cmd = 'SELECT MAX(bankaccountid) FROM bank_accounts'
    cursor = g.conn.execute(cmd)
    for result in cursor:
        bankaccountid = result[0] + 1

    bankaccount = [bankaccountid, request.form['aba'], request.form['accountnumber'], uid, request.form['directdeposit']]
    print(bankaccount)
    cmd = 'INSERT INTO bank_accounts VALUES (%s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (bankaccount[0], bankaccount[1], bankaccount[2], bankaccount[3], bankaccount[4]));
    return redirect(url_for('portfolio', passuid=uid, portfolioid=Gportfolioid))

#posting stock trades
@app.route('/post_trade', methods=['POST'])
def post_trade():
    #find biggest primary key id and increment by 1
    cmd = 'SELECT MAX(stockid) FROM stock_transactions'
    cursor = g.conn.execute(cmd)
    for result in cursor:
        stockid = result[0] + 1
    tdate = datetime.date.today()
    tdate = str(tdate)

    if request.form['order']=='buy':
        shares = int(request.form['shares'])
    else:
        shares = int(request.form['shares'])*-1
    transaction = [stockid, request.form['ticker'], uid, request.form['portfolio'], shares, "B", request.form['currentprice'], tdate, 0, 0, tdate]
    cmd = 'INSERT INTO stock_transactions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (transaction[0], transaction[1], transaction[2], transaction[3], transaction[4], transaction[5], transaction[6], transaction[7], transaction[8], transaction[9], transaction[10]));
    return redirect(url_for('portfolio', passuid=uid, portfolioid=request.form['portfolio']))

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
    cash = [transactionid, tdate, uid, float(request.form['bankaccountid']), request.form['portfolio'], amount]
    cmd = 'INSERT INTO cash_transactions VALUES (%s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (cash[0], cash[1], cash[2], cash[3], cash[4], cash[5]));
    return redirect(url_for('portfolio', passuid=uid, portfolioid=request.form['portfolio']))



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
    users = [uid, request.form['fname'], request.form['lname'], request.form['address'], request.form['phone'], request.form['ssn'], request.form['password'], request.form['email']]
    cmd = 'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (users[0], users[1], users[2], users[3], users[4], users[5], users[6], users[7]));
    return redirect(url_for('usercreated', uid=int(uid)))

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

@app.route('/update_user', methods=['POST'])
def update_user():
    #fill out user data and update in database
    users = [uid, request.form['fname'], request.form['lname'], request.form['address'], request.form['phone'], request.form['ssn'], request.form['password'], request.form['email']]
    cmd = 'UPDATE users SET (fname, lname, address, phone, ssn, password, email) = (%s, %s, %s, %s, %s, %s, %s) WHERE uid=%s';
    g.conn.execute(cmd, (users[1], users[2], users[3], users[4], users[5], users[6], users[7], users[0]));

    cmd = "SELECT * FROM users where uid=%s"
    cursor = g.conn.execute(cmd,uid)
    userdata = []
    for result in cursor:
        userdata=result
    cursor.close()
    return render_template("profile.html", userdata=userdata)





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
