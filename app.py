import os
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


@app.route('/')
def index():
    return render_template("login.html")

@app.route('/check_login', methods=['POST'])
def checklogin():
    link = 'badlog'
    uid = request.form['uid']
    checkuser = null
    cmd ="SELECT uid from users where uid=%s"
    cursor = g.conn.execute(cmd,uid)
    for result in cursor:
        checkuser = result
        print(type(uid),type(checkuser[0]))
        if checkuser[0] == float(uid):
            link = 'portfolio'
            #portfolio(checkuser)
    return redirect(url_for(link, uid=uid))

@app.route('/incorrectlogon/<uid>')
def badlog(uid):
    return render_template("incorrectlogon.html", uid=uid)


@app.route('/portfolio/<uid>')
def portfolio(uid):
    cmd ="SELECT * FROM stock_transactions where uid=%s"
    cursor = g.conn.execute(cmd, uid)
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
    return render_template("portfolio.html", transactions=transactions, user=userinfo)

@app.route('/newuser')
def newuser():
    return render_template("add_user.html")


@app.route('/profile')
def profile():
    cursor = g.conn.execute("SELECT * FROM users where uid=1")
    names = []
    for result in cursor:
        names=result
    cursor.close()
    return render_template("profile.html", names=names)


@app.route('/post_user', methods=['POST'])
def post_user():
    users = [request.form['uid'], request.form['fname'], request.form['lname'], request.form['address'], request.form['phone'], request.form['ssn']]
    cmd = 'INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)';
    g.conn.execute(cmd, (users[0], users[1], users[2], users[3], users[4], users[5]));
    return redirect('/newuser')





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
