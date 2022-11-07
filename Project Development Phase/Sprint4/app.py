from flask import Flask, render_template, request, redirect, session 
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
app = Flask(__name__)
app.secret_key = 'a'  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'D2DxDUPBii'
mysql = MySQL(app)

@app.route("/home")
def home():
    return render_template("homepage.html")
@app.route("/")
def add():
    return render_template("home.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE username = % s', (username, ))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            cursor.execute('INSERT INTO register VALUES ( % s, % s, % s)', (username, email,password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('signup.html', msg = msg)
    
@app.route("/signin")
def signin():
    return render_template("login.html")       
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''     
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register WHERE username = % s AND password = % s', (username, password ),)
        account = cursor.fetchone()
        print (account)       
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]           
            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route("/add")
def adding():
    return render_template('add.html')
@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']    
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO expenses VALUES ( % s, % s, % s, % s, % s, % s)', (session['id'] ,date, expensename, amount, paymode, category))
    mysql.connection.commit()
    print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
    
    return redirect("/display")

@app.route("/display")
def display():
    print(session["username"],session['id'])
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC'.format(str(session['id'])))
    expense = cursor.fetchall()       
    return render_template('display.html' ,expense = expense)   

@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM expenses WHERE  userid = %s', (id,))
    row = cursor.fetchall()  
    print(row[0])
    return render_template('edit.html', expenses = row[0])
@app.route('/update/<id>', methods = ['POST'])
def update(id):
  if request.method == 'POST' :   
      date = request.form['date']
      expensename = request.form['expensename']
      amount = request.form['amount']
      paymode = request.form['paymode']
      category = request.form['category']   
      cursor = mysql.connection.cursor()       
      cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`userid` = % s ",(date, expensename, amount, str(paymode), str(category),id))
      mysql.connection.commit()
      print('successfully updated')
      return redirect("/display")            

@app.route("/limit" )
def limit():
       return redirect('/limitn')
@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
         number= request.form['number']
         cursor = mysql.connection.cursor()
         cursor.execute('INSERT INTO limits VALUES (% s, % s) ',(session['id'], number))
         mysql.connection.commit()
         return redirect('/limitn')         
@app.route("/limitn") 
def limitn():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT limits FROM limits ORDER BY `limits`.`id` DESC LIMIT 1')
    x= cursor.fetchone()
    s = x#[0]    
    return render_template("limit.html" , y= s)

@app.route("/today")
def today():
      cursor = mysql.connection.cursor()
      print ("HI")
      #cursor.execute('SELECT TIME(date)   , amount FROM expenses  WHERE userid = {0} AND DATE(date) = DATE(NOW()) '.format(str(session['id'])))
      cursor.execute('SELECT TIME(date)   , amount FROM expenses  WHERE userid = %s AND DATE(date) = DATE(NOW()) ',(id,)) 
      
      texpense = cursor.fetchall()
      print(texpense)
      
      cursor = mysql.connection.cursor()
      print("HIII")
      #cursor.execute('SELECT * FROM expenses WHERE userid = {0} AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC'.format(str(session['id'])))
      cursor.execute('SELECT * FROM expenses WHERE userid = %s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(id,))
      
      expense = cursor.fetchall()
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in expense:
          total += x[4]
          if x[6] == "food":
              t_food += x[4]
            
          elif x[6] == "entertainment":
              t_entertainment  += x[4]
        
          elif x[6] == "business":
              t_business  += x[4]
          elif x[6] == "rent":
              t_rent  += x[4]
           
          elif x[6] == "EMI":
              t_EMI  += x[4]
         
          elif x[6] == "other":
              t_other  += x[4]     
      return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

#log-out
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')
if __name__ == "__main__":
    app.run(debug=True)