from flask import Flask, render_template, session,request, json, url_for, redirect
import pymysql
import hashlib

db = pymysql.connect("localhost", "root", "", "pyfarmer_db")


app = Flask(__name__)

app.secret_key = 'tawanda91'


@app.route("/")
def home():
	if session:
		return render_template('home.html')
	else:
		return render_template('index.html')
		
@app.route('/secure-login', methods=['POST'])
def signin():
	#adding a key to secure form against injection
	#can further encrypt this key
	form_secure = 'This$#is#$my#$Secret@#Key!@#'
	form_key = request.form['form_secure']
	#check if form security key is present
	if form_key and form_key==form_secure:
		#collect login-form inputs
		username = request.form['username']
		password = request.form['password']
		h = hashlib.md5(password.encode())
		password = h.hexdigest()
		#user_group from database
		if request.method == 'POST' and username  and password:
			# Check if account exists using MySQL
			cursor = db.cursor()
			sql = 'SELECT * FROM accounts WHERE username = %s'
			cursor.execute(sql, username)
			# Fetch one record and return result
			account = cursor.fetchone()
			# If account exists in accounts table in out database
			if account and password == account[2]:
				session['signin'] = True
				session['username'] = username
				session['sessionkey'] = password
				return render_template('home.html')
			else:
				msg = "Username/Password combination wrong!"
				return render_template('index.html', msg=msg)
		else:
			msg = "Something went wrong!"
			return render_template('index.html', msg=msg)
	else:
		msg = "Something went wrong!"
		return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
	session.pop('signin', None)
	session.pop('username', None)
	session.pop('sessionkey', None)
	return redirect(url_for('home'))
		
@app.route('/signup')
def signup():
	return render_template('signup.html')


@app.route('/register',  methods=['POST', 'GET'])
def register():
	#adding a key to secure form against injection
	#can further encrypt this key
	form_secure = 'This$#is#$my#$Secret@#Key!@#'
	form_key = request.form['form_secure']
	#check if form security key is present
	if form_key and form_key==form_secure:
		username = request.form['username']
		password = request.form['password']
		#encode our user submitted password
		h = hashlib.md5(password.encode())
		password = h.hexdigest()

		email = request.form['email']
		#check that all fields have been submitted
		if request.method == 'POST' and username and password and email:
			
			# Check if account exists using MySQL
			cursor = db.cursor()
			sql = 'SELECT * FROM accounts WHERE username = %s'
			cursor.execute(sql, username)
			# Fetch one record and return result
			account = cursor.fetchone()
			# If account exists in accounts table in out database
			if account:
				msg = 'Error! User account or email already exists!'
				return render_template('signup.html', msg=msg)
			else:
				cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)',(username, password, email))
				# the connection is not autocommited by default. So we must commit to save our changes.
				db.commit()
				msg = 'successfully registered!<a href="/"> Continue to Login..</a>'
				return username + ' ' + msg
		else:
			msg = 'something went wrong'
			return render_template('signup.html', msg = msg)

		#return 'successfully regestered user: '+ username
	else:
		msg = 'something went wrong'
		return render_template('signup.html', msg = msg)
		

@app.route('/profile')
def profile():
	username = session['username']
	sessionkey = session['sessionkey']
	# Check if account exists using MySQL
	cursor = db.cursor()
	sql = 'SELECT * FROM accounts WHERE username = %s'
	cursor.execute(sql, username)
	# Fetch one record and return result
	account = cursor.fetchone()
			# If account exists in accounts table in out database
	if account and sessionkey == account[2]:
		#return 'Your personal details:<br>Username: ' + account[1] + '<br>' + 'Email: '+ account[3] + '<br>Password: ' + account[2] + '<br>(session pwd: '+ password +')'
		return render_template('profile.html', userid = account[0], username = account[1],sessionkey = account[2],email = account[3])
		
	else:
		return 'No matching record found!'
	
		
@app.route('/farmer')
def farmer():
	return render_template('farmer.html')		


@app.route('/submit-ticket')
def farmerblogsubmit():
	msgsuccess = 'ticket has been submitted successfully'
	return render_template('farmer.html', msgsuccess = msgsuccess)


@app.route('/dealer')
def dealer():
	return render_template('dealer.html')	

@app.route('/admin')
def admin():
	cursor = db.cursor()
	cursor.execute("SELECT * FROM accounts")
	#Fetch all records and use a loop to print out
	result = cursor.fetchall()
	
	
	return render_template('admin.html', result=result)
