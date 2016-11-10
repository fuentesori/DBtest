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

@app.route('/portfolio')
def portfolio():
    cursor = g.conn.execute("SELECT * FROM stock_transactions where uid=1")
    transactions = []
    for result in cursor:
        transactions.append(result)  # can also be accessed using result[0]
    cursor.close()
    return render_template("portfolio.html", transactions=transactions)

@app.route('/newuser')
def newuser():
    return render_template("add_user.html")


@app.route('/profile')
def profile():
    cursor = g.conn.execute("SELECT * FROM users where uid=1")
    names = []
    for result in cursor:
        names=result  # can also be accessed using result[0]
    cursor.close()
    return render_template("profile.html", names=names)

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ok@localhost/4111T'
# app.debug = True
# db = SQLAlchemy(app)
# DATABASEURI = "postgresql://postgres:ok@localhost/4111T"
# engine = create_engine(DATABASEURI)
# g.conn = engine.connect()


# class Users(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     email = db.Column(db.String(120), unique=True)
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(9))
#
#     def __init__(self, username, email):
#         self.username = username
#         self.email = email
#
#     def __repr__(self):
#         return '<User %r>' %self.username



#     cursor = g.conn.execute("SELECT UID FROM Users")
#     myUser = []
#     for result in cursor:
#           myUser.append(result['UID'])  # can also be accessed using result[0]
#     cursor.close()
#
#
#     # myUser = Users.query.all()
#     # oneItem = Users.query.filter_by(UID=1).all()
#     #return render_template('add_user.html', myUser = myUser, oneItem = oneItem)
#     return render_template('add_user.html', myUser = myUser)
     #return render_template('add_user.html')
#
# @app.route('/profile/<username>')
# def profile(username):
#     user = User.query.filter_by(username=username).first()
#     return render_template('profile.html', user=user)
#
#
#
# @app.route('/post_user', methods=['POST'])
# def post_user():
#     user = User(request.form['username'], request.form['email'])
#     db.session.add(user)
#     db.session.commit()
#     return redirect(url_for('index'))

# if __name__=="__main__":
#     app.run()


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
