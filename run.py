
from flask import Flask, render_template, redirect, request, url_for, session,g,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import date
from flask_mysqldb import MySQL
from datetime import date
from flask_session import Session



app = Flask(__name__)
app.secret_key='project'
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
app.config['MYSQL_HOST'] = 'database-1.ciwuzoyj0xa2.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'csaproject'
app.config['MYSQL_DB'] = 'project'

Session(app)



mysql=MySQL(app)

@app.route('/')
def index():
   return redirect(url_for("login"))

@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        com="SELECT * FROM accounts WHERE username = %s AND password = %s"
        data=(username, password)
        cursor.execute(com,data)
        account=cursor.fetchone()
        cursor.close()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['name']=account['name']
            return redirect(url_for("success", name = username))
        else:
            return redirect(url_for('error'))
    return render_template('login.html')

@app.route('/success/<name>')
def success(name):
    user = session.get('username')
    return redirect(url_for("home"))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/home/')
def home():
    # Number of times to repeat the HTML element
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM blogs')
    a=cur.fetchall()
    n=len(a)
    repeat_count = n 
    cur.close()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from blogs order by blog_id DESC')

# HTML element to repeat
    element_to_repeat = "<section><h2>%s</h2><p class>%s</p><p>%s</p></section>"

# Initialize an empty HTML string
    html_code = ""

# Use a for loop to repeat the element and concatenate it to the HTML string
    
    for _ in range(repeat_count):
        posts = cur.fetchone()
        posttitle=posts['title']
        date=posts['date']
        content=posts['content']
        author=posts['name']
        html_code += "<div style='font-family:'Tahoma';margin: 20px' ><div style='background-color: #f8f8f8;border: 1px solid #ddd;margin-bottom: 20px;padding: 20px;'><h1 align='center' style='margin-top: 0; font-size: 50px'>%s</h1><h4 align='center' style='margin-top:-20px;'>By %s</h4><h3 align='right'>%s</h3><p style='margin-left:50px; margin-right:50px; font-size:22px;'>%s</p></div></div>"%(posttitle,author,date,content)
# Print the generated HTML code
    cur.close()
    return render_template('index.html',htmlf=html_code)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'name' in request.form :
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        com2="SELECT * FROM accounts WHERE name='%s'" %(name)
        cursor.execute(com2)
        account = cursor.fetchone()
        cursor.close()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email or not name:
            msg = 'Please fill out the form !'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            com3="INSERT INTO accounts(username,name,email,password) VALUES (% s, % s, % s, %s)"
            data3=(username, name, email, password)
            cursor.execute(com3,data3)
            mysql.connection.commit()
            cursor.close()
            msg = 'You have successfully registered !'
            return redirect(url_for("login"))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
        
    return render_template('register.html', msg = msg)

@app.route('/createblog/', methods =['GET', 'POST'])
def createblog():
    if request.method == 'POST' and 'title' in request.form and 'category' in request.form and 'content' in request.form:
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        datenew=date.today()
        userid=session.get('id')
        name=session.get('name')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO blogs (title,category,content,date,user_id,name) VALUES (%s, %s, %s, %s, %s, %s)', (title, category, content, datenew, userid, name))
        mysql.connection.commit()
        flash('blog created successfully')
    return render_template('blogs.html')
@app.route('/createblog/success', methods =['GET', 'POST'])
def blogsuccess():
    return render_template('popup.html')

@app.route('/user')
def user():
    id2=session.get('id')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    com5="SELECT * FROM accounts WHERE id=%s" %id2
    data5=(id2)
    cursor.execute(com5)
    acc=cursor.fetchone()
    username=acc['username']
    email=acc['email']
    name=acc['name']
    dob=acc['dob']
    gender=acc['gender']

    return render_template('user.html',username=username,email=email,name=name,dob=dob,gender=gender)

@app.route('/edit', methods =['GET', 'POST'])
def edit():
    username=session.get('username')
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        email = request.form['email']
        gender = request.form['gender']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        com3="UPDATE accounts SET name='%s',email='%s',dob='%s',gender='%s' WHERE username='%s'" %(name,email,dob,gender,username)
        cursor.execute(com3)
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('user'))
    return render_template('edit.html',user=username)

if __name__ == '__main__':
    app.run(debug=True)