from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import random
import sqlite3
from helpers import login_required, get_connexion1,get_content, imdb_api_caller, change_500, send_a_verification_code,api_key_required
import json
import math


#        I'm sorry the code is messy and unreadable but i didn't have time to clean it up



# Configure application
app = Flask(__name__)


with open("static/titles.txt", 'r') as fp:
    titles_list = fp.readlines()
titles = ''
for e in range(len(titles_list)):
    titles_list[e] = titles_list[e].strip('\n')
    titles += titles_list[e] + ','

# Ensure templates are auto-reloaded
app.config['TRAP_HTTP_EXCEPTIONS']=True
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


votes = 0

@app.errorhandler(404)
def page_not_found_404(e):
    parameters = ['404',"We can't find the page you're looking for","Reasons: Most likelly because the page simply doesn't exist or the page is curently private or deleted","Solutions: Press the go home button to refrech the site and try again"]
    return render_template('errorpage.html',parameters=parameters), 404

@app.errorhandler(500)
def page_not_found_500(e):
    return redirect(url_for('errorpage'))


@app.route("/errorpage")
def errorpage():
    from helpers import parameter_500
    return render_template('errorpage.html',parameters=parameter_500)


@app.route("/")
def index():
    session["user_email"] = ''
    if request.method == "GET": 
        if session.get("user_name") is None:
            name = "Please Log-in!"
        else:
            name = session["user_name"]

        if session.get("imdb_key") is None:
            was_it_set = ["Set IMDB-api key",'/setimdbkey']
        else:
            was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

        return render_template("index.html",name=name,was_it_set=was_it_set,titles=titles)
    else:
        return redirect("/")


@app.route('/searchresult')
@login_required
@api_key_required
def searchresult():
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    title_ = request.args.get('title')
    
    if title_ is None:
        return redirect("/")

    title = title_.replace(" ", "%20")
    con = get_connexion1()
    connection = con[0]
    cursor = con[1]
    command1 = """Create Table IF NOT EXISTS search_data(search_string TEXT KEY, result TEXT, choice_acc TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT result FROM search_data WHERE search_string = '{title}'")
    results_query = cursor.fetchall()

    if results_query == []:
        response = imdb_api_caller(f'/{title}','Search')

        all_data = []
        current_e = []
        for e in response['results']:
            current_e.append(e['id'])
            current_e.append(e['title'])
            if e['image'] == "":
                current_e.append("/static/no_cover.jpg")
            else:
                current_e.append(e['image'])
            current_e.append(e['description'])
            all_data.append(current_e)
            current_e = []
        str_all_data = json.dumps(all_data)
        cursor.execute("INSERT INTO search_data Values (?, ?, ?)", (title,str_all_data,'none'))
        connection.commit()
    else:
        ol = results_query[0][0]
        all_data = json.loads(ol)
    
    connection.close()
    return render_template('searchresult.html',name=name,was_it_set=was_it_set,titles=titles,all_data=all_data,searchterm=title_)


@app.route('/searchitem')
@login_required
@api_key_required
def searchitem():
    print(request.args.get('id'))
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    title_id = request.args.get('id')
    
    if title_id is None:
        return redirect("/")

    con = get_connexion1()
    connection = con[0]
    cursor = con[1]

    command1 = """Create Table IF NOT EXISTS content_data(id TEXT KEY, data TEXT, choice_acc TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT data FROM content_data WHERE id = '{title_id}'")
    results_query = cursor.fetchall()

    if results_query == []:
        all_data = get_content(title_id,cursor,connection)
    else:
        ol = results_query[0][0]
        all_data = json.loads(ol)

    list = []
    for e in range(len(all_data[0])):
        list.append(e)
    list.append(list[-1] +1)
    connection.close()
    return render_template('searchitem.html',name=name,was_it_set=was_it_set,titles=titles,all_data=all_data,list=list)
    

@app.route('/bestofthebest')
@login_required
@api_key_required
def bestofthebest():
    param = ['BoxOfficeAllTime','MostPopularMovies','MostPopularTVs','Top250TVs','Top250Movies','ComingSoon','BoxOffice','InTheaters']
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    type_class = request.args.get('class')
    if type_class not in param:
        return redirect('/')

    page = request.args.get('page')
    
    # if title_id is None:
    #     return redirect("/")


    con = get_connexion1()
    connection = con[0]
    cursor = con[1]

    command1 = """Create Table IF NOT EXISTS search_data(search_string TEXT KEY, result TEXT, choice_acc TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT * FROM search_data WHERE search_string = '{type_class}'")
    results_query = cursor.fetchall()
    if results_query == []:
        response = imdb_api_caller('',type_class)
        data = []
        all_data = []
        for e in response['items']:
            data.append(e['id'])
            data.append(e['title'])
            data.append(e['image'].replace("UX128_CR0,12,128,176_AL_.jpg", "Ratio0.6837_AL_.jpg"))
            all_data.append(data)
            data = []
        str_all_data = json.dumps(all_data)
        cursor.execute("INSERT INTO search_data Values (?, ?, ?)", (type_class,str_all_data,'none'))
        connection.commit()
    else:
        ol = results_query[0][1]
        all_data = json.loads(ol)
        print('from db')

    lenght = math.ceil(len(all_data)/10)
    all_data = all_data[int(page)*10-10:int(page)*10]
    connection.close()
    return render_template('bestofthebest.html',name=name,was_it_set=was_it_set,titles=titles,all_data=all_data,lenght=lenght,type_class=type_class)



@app.route('/topgenres')
@login_required
@api_key_required
def topgenres():
    param = ['biography','animation','adventure','thriller','history','romance','horror','family','comedy','action','drama','crime','top_1000']
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    type_class = request.args.get('genre')
    if type_class not in param:
        return redirect('/')

    page = request.args.get('page')
    
    # if title_id is None:
    #     return redirect("/")


    con = get_connexion1()
    connection = con[0]
    cursor = con[1]

    command1 = """Create Table IF NOT EXISTS search_data(search_string TEXT KEY, result TEXT, choice_acc TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT * FROM search_data WHERE search_string = '{type_class}'")
    results_query = cursor.fetchall()
    if results_query == []:
        if type_class != "top_1000":
            response = imdb_api_caller(f"?genres={type_class}&count=250","AdvancedSearch")
        else:
            response = imdb_api_caller(f"?groups=top_1000&count=250","AdvancedSearch")

        data = []
        all_data = []
        for e in response['results']:
            data.append(e['id'])
            data.append(e['title'])
            data.append(e['image'])
            data.append(e['plot'])
            all_data.append(data)
            data = []
        str_all_data = json.dumps(all_data)
        cursor.execute("INSERT INTO search_data Values (?, ?,?)", (type_class,str_all_data,'none'))
        connection.commit()
    else:
        ol = results_query[0][1]
        all_data = json.loads(ol)

    lenght = math.ceil(len(all_data)/10)
    all_data = all_data[int(page)*10-10:int(page)*10]
    connection.close()
    return render_template('topgenres.html',name=name,was_it_set=was_it_set,titles=titles,all_data=all_data,lenght=lenght,type_class=type_class)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        errors = 'Please fill up the following box(s): '

        # Ensure username was submitted
        if not request.form.get("username"):
            errors += 'username ,'

        # Ensure password was submitted
        if not request.form.get("password"):
            errors += 'password ,'

        if errors != 'Please fill up the following box(s): ':
            errors = errors[:-2]
            errormessage = [errors,request.form.get("username"),request.form.get("password")]
            return render_template("login.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        connection2 = sqlite3.connect('users_data.db')
        cursor2 = connection2.cursor()

        command1 = """Create Table IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, imdb_code TEXT DEFAULT "not set" , password TEXT)"""
        cursor2.execute(command1)
        # # Query database for username
        rows = cursor2.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))

        # # Ensure username exists and password is correct
        resul = rows.fetchall()

        try:
            if len(resul) != 1:
                errormessage = ["Username doesn't exist, check if you have a typo",request.form.get("username"),request.form.get("password")]
                return render_template("login.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
        except:
            errormessage = ["Username doesn't exist, check if you have a typo",request.form.get("username"),request.form.get("password")]
            return render_template("login.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        if check_password_hash(resul[0][4], request.form.get("password")) == False:
            errormessage = ["Password incorrect, check if you have a typo or recover it if you can't remember it",request.form.get("username"),request.form.get("password")]
            return render_template("login.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
    
        session.clear()
        # # Remember which user has logged in
        session["user_id"] = resul[0][0]
        session["user_name"] = resul[0][2]
        if resul[0][3] != "not set":
            session["imdb_key"] = resul[0][3]
        # # Redirect user to home page
        connection2.close()
        flash("logged-in successfully!", 'error')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        errormessage = ["",'','']
        return render_template("login.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":


        errors = 'Please fill up the following box(s): '

        if not request.form.get("username"):
            errors += 'username, '

        if not request.form.get("email"):
            errors += 'email, '

        if not request.form.get("password"):
            errors += 'password, '

        if errors != 'Please fill up the following box(s): ':
            errors = errors[:-2]
            errormessage = [errors,request.form.get("username"),request.form.get("email"),request.form.get("password")]
            return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        connection2 = sqlite3.connect('users_data.db')
        cursor2 = connection2.cursor()
        command1 = """Create Table IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, imdb_code TEXT DEFAULT "not set" , password TEXT)"""
        cursor2.execute(command1)

        username = request.form.get("username")
        rows = cursor2.execute("SELECT username FROM users WHERE username = ?", (username,))
        if rows.fetchall():
            errormessage = ["Username is already taken please choose another one",request.form.get("username"),request.form.get("email"),request.form.get("password")]
            return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        email = request.form.get("email")
        rows = cursor2.execute("SELECT email FROM users WHERE email = ?", (email,))
        if rows.fetchall():
            errormessage = ["That email is already used in another account",request.form.get("username"),request.form.get("email"),request.form.get("password")]
            return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        api_key = "6545aa5b-3793-45da-9e1f-be155d4d4a3a" 
        email_address = request.form.get("email")
        response = requests.get(
            "https://isitarealemail.com/api/email/validate",
            params = {'email': email_address},
            headers = {'Authorization': "Bearer " + api_key })

        status = response.json()['status']
        if status == "valid":
            email_status = "email is valid"
        elif status == "invalid":
            email_status = "email is invalid"
        else:
            email_status = "email was unknown"

        if email_status != 'email is valid':
            errormessage = [email_status,request.form.get("username"),request.form.get("email"),request.form.get("password")]
            return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        
        password_hashed = generate_password_hash(request.form.get("password"))
        try:
            cursor2.execute("INSERT INTO users ('email','username','password') VALUES (?,?,?)", (request.form.get("email"),request.form.get("username"), password_hashed))
        except:
            errormessage = ["An error has occured when registering your account",request.form.get("username"),request.form.get("email"),request.form.get("password")]
            return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        connection2.commit()
        connection2.close()

        flash("Registered! please log-in now and set an IMDB API key later", 'error')
        return redirect("/login")
    else:
        errormessage = ["",'']
        return render_template("register.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)


@app.route("/changeinfo", methods=["GET", "POST"])
def changeinfo():
    """Register user"""
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    connection2 = sqlite3.connect('users_data.db')
    cursor2 = connection2.cursor()
    command1 = """Create Table IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, imdb_code TEXT DEFAULT "not set" , password TEXT)"""
    cursor2.execute(command1)
    try:
        id_key = int(session["user_id"])
        rows = cursor2.execute(f"SELECT * FROM users WHERE id = ?",(id_key,))
        res = rows.fetchall()[0]
        name_db = res[1]
        username = res[2]
        password = res[4]

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            errors = 'Please fill up the following box(s): '
            if not request.form.get("username"):
                errors += 'username, '

            if not request.form.get("email"):
                errors += 'email, '

            if errors != 'Please fill up the following box(s): ':
                errors = errors[:-2]
                errormessage = [errors,request.form.get("email"),request.form.get("username"),request.form.get("password")]
                return render_template("changeinfo.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
            
            
            if request.form.get("username") != username:
                user = request.form.get("username")
                rows = cursor2.execute("SELECT username FROM users WHERE username = ?", (user,))
                if rows.fetchall():
                    errormessage = ["Username is already taken please choose another one",request.form.get("email"),request.form.get("username"),request.form.get("password")]
                    return render_template("changeinfo.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
                
            password_hashed = generate_password_hash(request.form.get("password"))
            if check_password_hash(password,request.form.get("password")) == True:
                errormessage = ["Try using a diffrent password if you want to change this current one, cause you're already using this one",request.form.get("email"),request.form.get("username"),request.form.get("password")]
                return render_template("changeinfo.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

            try:
                if not request.form.get("password"):
                    cursor2.execute("UPDATE users SET email = ?,username= ? WHERE id = ?", (request.form.get("email"),request.form.get("username"),id_key))
                else:
                    cursor2.execute("UPDATE users SET email = ?,username= ?,password= ? WHERE id = ?", (request.form.get("email"),request.form.get("username"),password_hashed,id_key))
            except:
                return render_template("changeinfo.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

            # Redirect user to home page
            connection2.commit()
            connection2.close()
            session["user_name"] = request.form.get("username")

            flash("Your data/info has been changed successfully.", 'error')
            return redirect("/")
        else:
            errormessage = ["",name_db,username]
            return render_template("changeinfo.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
    except IndexError:
        param = ['500',"User Not Found","Reasons: It's most likely because of a problem in our database or a bug in our server.",
            "Solutions: Press the button below and try again multiple times if this page comes over and over again than we're sorry contact the dev if you know him (chakib) or try later."]
        change_500(param)



@app.route("/sendverification", methods=["GET", "POST"])
def sendverification():
    to = session["user_email"][0]
    code = send_a_verification_code(to)
    session["user_email"] = session["user_email"][0],session["user_email"][1],code
    return ('', 204)


@app.route("/emailverification", methods=["GET", "POST"])
def emailverification():
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    user_data = session["user_email"]

    if request.method == "POST":
        # input_code = request.form.get("code")
        if not request.form.get("code"):
            errormessage = ["Please enter the verification code",request.form.get('code')]
            return render_template("emailverification.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        if str(request.form.get("code")) != str(user_data[2]):
            errormessage = ["Verification code incorrect",request.form.get('code')]
            return render_template("emailverification.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        connection2 = sqlite3.connect('users_data.db')
        cursor2 = connection2.cursor()
        command1 = """Create Table IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, imdb_code TEXT DEFAULT "not set" , password TEXT)"""
        cursor2.execute(command1)

        password_hashed = generate_password_hash(session['user_email'][1])
        cursor2.execute("UPDATE users SET password = ? WHERE email = ?", (password_hashed ,session['user_email'][0]))

        session['user_email'] = ''
        connection2.commit()
        connection2.close()
        flash("Your password has been changed successfully, please log-in now.", 'error')
        return redirect('/login')
    else:
        try:
            if len(user_data) != 3:
                code = send_a_verification_code(user_data[0])
                session["user_email"] = session["user_email"][0],session["user_email"][1],code
        except IndexError:
            pass
        
        errormessage = ["",'']
        return render_template("emailverification.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles,email=session['user_email'][0])


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpassword():
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]


    try:
        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":

            errors = 'Please fill up the following box(s): '
            if not request.form.get("email"):
                errors += 'email, '

            if not request.form.get("password"):
                errors += 'new password, '

            if errors != 'Please fill up the following box(s): ':
                errors = errors[:-2]
                errormessage = [errors,request.form.get("email"),request.form.get("password")]
                return render_template("forgotpassword.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
      

            connection2 = sqlite3.connect('users_data.db')
            cursor2 = connection2.cursor()
            command1 = """Create Table IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, username TEXT, imdb_code TEXT DEFAULT "not set" , password TEXT)"""
            cursor2.execute(command1)

            rows = cursor2.execute("SELECT * FROM users where email = ?", (request.form.get("email"),))
            res = rows.fetchall()
            if res == []:
                errormessage = ["No user found with that email",request.form.get("email"),request.form.get("password")]
                return render_template("forgotpassword.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
                
            # flash("Registered!", 'error')
            try:
                session["user_email"] = request.form.get("email"),request.form.get("password"),session['user_email'][2]
            except:
                session["user_email"] = request.form.get("email"),request.form.get("password")
            # ?email='+request.form.get("email")+'&password='+request.form.get("password")
            return redirect('/emailverification')
        else:
            try:
                errormessage = ["",session["user_email"][0],session["user_email"][1]]
            except:
                errormessage = ["",'']
            return render_template("forgotpassword.html",name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)
    except IndexError:
        param = ['500',"User Not Found","Reasons: It's most likely because of a problem in our database or a bug in our server.",
            "Solutions: Press the button below and try again multiple times if this page comes over and over again than we're sorry contact the dev if you know him (chakib) or try later."]
        change_500(param)


@app.route("/redirect_to_login")
def redirect_to_login():
    return render_template('redirect.html')


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("You logged-out successfully.", 'error')
    return redirect("/")


@app.route("/apicallsleft")
@login_required
@api_key_required
def apicallsleft():
    res = imdb_api_caller('','Usage')
    count = res['count']
    max = res['maximum']
 
    flash(f"You've got {count}/{max} API calls left.", 'error')
    return redirect('/')



@app.route("/deleteaccount")
@login_required
def deleteaccount():
    # Forget any user_id

    id_key = session.get("user_id")
    connection2 = sqlite3.connect('users_data.db')
    cursor2 = connection2.cursor()
    cursor2.execute("DELETE FROM users WHERE id=?", (id_key,))

    connection2.commit()
    connection2.close()
    session.clear()
    flash("Your account has been deleted successfully.", 'error')
    # Redirect user to login form
    return redirect("/")


@app.route("/setimdbkey", methods=["GET", "POST"])
@login_required
def setimdbkey():
    if session.get("user_name") is None:
        name = "Please Log-in!"
    else:
        name = session["user_name"]

    if session.get("imdb_key") is None:
        was_it_set = ["Set IMDB-api key",'/setimdbkey']
    else:
        was_it_set = ["Remove IMDB key",'/removeimdbkey',session.get("imdb_key")]

    if request.method == "POST":
        if not request.form.get("apikey"):
            errormessage = ["Please entre a valid IMDB api key",request.form.get("apikey")]
            return render_template('imdbkeyset.html',name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)

        api_key = request.form.get("apikey")
        id_key = session.get("user_id")

        # payload = {}
        # headers= {}
        # response = requests.request("GET", f'https://imdb-api.com/API/Usage/{api_key}', headers=headers, data = payload).json()

        # if response['errorMessage'] == 'Invalid API Key':
        #     errormessage = ["Invalid Api key, maybe it's incorrect or banned by IMDB",request.form.get("apikey")]
        #     return render_template('imdbkeyset.html',name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)


        connection2 = sqlite3.connect('users_data.db')
        cursor2 = connection2.cursor()

        cursor2.execute("UPDATE users SET imdb_code = ? WHERE id = ?", (api_key,id_key))

        connection2.commit()
        connection2.close()

        session["imdb_key"] = api_key
        flash("Your IMDB API key was successfully set, thank you for your collaboration we hope you enjoy our website :).", 'error')
        return redirect('/')
    else:
        errormessage = ["",'']
        return render_template('imdbkeyset.html',name=name,was_it_set=was_it_set, errormessage=errormessage,titles=titles)



@app.route("/removeimdbkey", methods=["GET", "POST"])
@login_required
def removeimdbkey():
    # Forget any user_id

    id_key = session.get("user_id")
    connection2 = sqlite3.connect('users_data.db')
    cursor2 = connection2.cursor()
    cursor2.execute("UPDATE users SET imdb_code = 'not set' WHERE id = ?", (id_key,))

    connection2.commit()
    connection2.close()

    session["imdb_key"] = None

    flash("Your IMDB API key was successfully removed.", 'error')
    # Redirect user to login form
    return redirect("/")




@app.route('/question1')
@login_required
@api_key_required
def question1():
    return render_template('question1.html')

@app.route('/question2')
@login_required
@api_key_required
def question2():
    data = [['TV Special','tv_special'],['TV Series','tv_series'],['Mini-Series','tv_miniseries'],['TV Movie','tv_movie'],['Short Film','short'],['TV Short','tv_short'],['Documentary','documentary'],['Podcast Series','podcast_series']]
    return render_template('question2.html',data=data)

@app.route('/question3')
@login_required
@api_key_required
def question3():
    data = [ ['adventure', 'Adventure'], ['animation', 'Animation'], ['biography', 'Biography'], ['comedy', 'Comedy'], ['crime', 'Crime'],['documentary','Documentary'],
     ['sport', 'Sport'], ['talk_show', 'Talk-Show'], ['news', 'News'], ['reality_tv', 'Reality-TV'], ['music', 'Music']]

    data_2 = [['family', 'Family'], ['fantasy', 'Fantasy'], ['game_show', 'Game-Show'], ['history', 'History'], ['horror', 'Horror'], ['mystery', 'Mystery'],
  ['romance', 'Romance'], ['sci_fi', 'Sci-Fi'], ['thriller', 'Thriller'], ['war', 'War'], ['western', 'Western']]
    return render_template('question3.html',data=data,data_2=data_2)

@app.route('/question4')
@login_required
@api_key_required
def question4():
    
    return render_template('question4.html')

@app.route('/question5')
@login_required
@api_key_required
def question5():
    data = ['NC-17','R' ,'PG-13' ,'PG' ,'G']
    return render_template('question5.html', data=data)
    
@app.route('/question6')
@login_required
@api_key_required
def question6():
    data = [['Super new','2020-2022','',''],['New','2015-2020','<br>','padding-top: 5px;'],['Getting new','2010-2015','',''],['Kinda new','2005-2010','',''],['Old','2000-2005','<br>','padding-top: 5px;'],['90s','1990-2000','<br>','padding-top: 5px;'],['Super old','1940-1990','','']]
    return render_template('question6.html', data=data)

@app.route('/question7')
@login_required
@api_key_required
def question7():
    languages = [['ab', 'Abkhazian'], ['qac', 'Aboriginal'], ['guq', 'Aché'], ['qam', 'Acholi'], ['af', 'Afrikaans'], ['qas', 'Aidoukrou'], ['ak', 'Akan'], ['sq', 'Albanian'], ['ale', 'Aleut'], ['alg', 'Algonquin'], ['ase', 'American Sign Language'], ['am', 'Amharic'], ['apa', 'Apache languages'], ['ar', 'Arabic'], ['an', 'Aragonese'], ['arc', 'Aramaic'], ['arp', 'Arapaho'], ['aqc', 'Archi'], ['hy', 'Armenian'], ['as', 'Assamese'], ['asb', 'Assiniboine'], ['aii', 'Assyrian Neo-Aramaic'], ['ath', 'Athapascan languages'], ['asf', 'Australian Sign Language'], ['awa', 'Awadhi'], ['ay', 'Aymara'], ['az', 'Azerbaijani'], ['ast', 'Bable'], ['qbd', 'Baka'], ['ban', 'Balinese'], ['bm', 'Bambara'], ['ba', 'Bashkir'], ['eu', 'Basque'], ['bsc', 'Bassari'], ['be', 'Belarusian'], ['bem', 'Bemba'], ['bn', 'Bengali'], ['ber', 'Berber languages'], ['bho', 'Bhojpuri'], ['qbi', 'Bicolano'], ['qbh', 'Bodo'], ['bfw', 'Bonda'], ['bs', 'Bosnian'], ['bzs', 'Brazilian Sign Language'], ['br', 'Breton'], ['bfi', 'British Sign Language'], ['bg', 'Bulgarian'], ['my', 'Burmese'], ['bsk', 'Burushaski'], ['yue', 'Cantonese'], ['ca', 'Catalan'], ['km', 'Central Khmer'], ['ccp', 'Chakma'], ['qax', 'Chaozhou'], ['ce', 'Chechen'], ['chr', 'Cherokee'], ['chy', 'Cheyenne'], ['hne', 'Chhattisgarhi'], ['zh', 'Chinese'], ['ckt', 'Chukchi'], ['kw', 'Cornish'], ['co', 'Corsican'], ['cr', 'Cree'], ['mus', 'Creek'], ['hr', 'Croatian'], ['cro', 'Crow'], ['cs', 'Czech'], ['da', 'Danish'], ['prs', 'Dari'], ['dso', 'Desiya'], ['din', 'Dinka'], ['qaw', 'Djerma'], ['doi', 'Dogri'], ['nl', 'Dutch'], ['dyu', 'Dyula'], ['dz', 'Dzongkha'], ['qbc', 'East-Greenlandic'], ['frs', 'Eastern Frisian'], ['egy', 'Egyptian (Ancient)'], ['en', 'English'], ['eo', 'Esperanto'], ['et', 'Estonian'], ['ee', 'Ewe'], ['qbg', 'Faliasch'], ['fo', 'Faroese'], ['fil', 'Filipino'], ['fi', 'Finnish'], ['qbn', 'Flemish'], ['fon', 'Fon'], ['fr', 'French'], ['fsl', 'French Sign Language'], ['fur', 'Friulian'], ['ff', 'Fulah'], ['fvr', 'Fur'], ['gd', 'Gaelic'], ['gl', 'Galician'], ['ka', 'Georgian'], ['de', 'German'], ['gsg', 'German Sign Language'], ['grb', 'Grebo'], ['el', 'Greek'], ['grc', 'Greek, Ancient (to 1453)'], ['kl', 'Greenlandic'], ['gn', 'Guarani'], ['gu', 'Gujarati'], ['gnn', 'Gumatj'], ['gup', 'Gunwinggu'], ['gbj', 'Gutob'], ['ht', 'Haitian'], ['hai', 'Haida'], ['hak', 'Hakka'], ['bgc', 'Haryanvi'], ['qav', 'Hassanya'], ['ha', 'Hausa'], ['haw', 'Hawaiian'], ['he', 'Hebrew'], ['hi', 'Hindi'], ['hmn', 'Hmong'], ['hoc', 'Ho'], ['qab', 'Hokkien'], ['hop', 'Hopi'], ['hu', 'Hungarian'], ['iba', 'Iban'], ['qag', 'Ibo'], ['is', 'Icelandic'], ['icl', 'Icelandic Sign Language'], ['ins', 'Indian Sign Language'], ['id', 'Indonesian'], ['iu', 'Inuktitut'], ['ik', 
'Inupiaq'], ['ga', 'Irish Gaelic'], ['iru', 'Irula'], ['it', 'Italian'], ['ja', 'Japanese'], ['jsl', 'Japanese Sign Language'], ['dyo', 'Jola-Fonyi'], ['ktz', 'Ju hoan'], ['qbf', 'Kaado'], ['kea', 'Kabuverdianu'], ['kab', 'Kabyle'], ['xal', 'Kalmyk-Oirat'], ['kn', 'Kannada'], ['kpj', 'Karajá'], ['mjw', 'Karbi'], ['kar', 'Karen'], ['kk', 'Kazakh'], ['kca', 'Khanty'], ['kha', 'Khasi'], ['ki', 'Kikuyu'], ['rw', 'Kinyarwanda'], ['qar', 'Kirundi'], ['tlh', 'Klingon'], ['kfa', 'Kodava'], ['trp', 'Kokborok'], ['kok', 'Konkani'], ['ko', 'Korean'], ['kvk', 'Korean Sign Language'], ['khe', 'Korowai'], ['qaq', 'Kriolu'], ['kro', 'Kru'], ['kyw', 'Kudmali'], ['qbb', 'Kuna'], ['ku', 'Kurdish'], ['kgg', 'Kusunda'], ['kwk', 'Kwakiutl'], ['ky', 'Kyrgyz'], ['lbj', 'Ladakhi'], ['lad', 'Ladino'], ['lo', 'Lao'], ['la', 'Latin'], ['lv', 'Latvian'], ['lif', 'Limbu'], ['ln', 'Lingala'], ['lt', 'Lithuanian'], ['nds', 'Low German'], ['lb', 'Luxembourgish'], ['mk', 'Macedonian'], ['qbm', 'Macro-Jê'], ['mag', 'Magahi'], ['mai', 'Maithili'], ['mg', 'Malagasy'], ['ms', 'Malay'], ['ml', 'Malayalam'], ['pqm', 'Malecite-Passamaquoddy'], ['qap', 'Malinka'], ['mt', 'Maltese'], ['mnc', 'Manchu'], ['cmn', 'Mandarin'], ['man', 'Mandingo'], ['mni', 'Manipuri'], ['mi', 'Maori'], ['arn', 'Mapudungun'], ['mr', 'Marathi'], ['mh', 'Marshallese'], ['mas', 'Masai'], ['mls', 'Masalit'], ['myn', 'Maya'], ['men', 'Mende'], ['mic', 'Micmac'], ['enm', 'Middle English'], ['nan', 'Min Nan'], ['min', 'Minangkabau'], ['mwl', 'Mirandese'], ['qmt', 'Mixtec'], ['lus', 'Mizo'], ['moh', 'Mohawk'], ['mn', 'Mongolian'], ['moe', 'Montagnais'], ['qaf', 'More'], ['mfe', 'Morisyen'], ['qbl', 'Nagpuri'], ['nah', 'Nahuatl'], ['qba', 'Nama'], ['nv', 'Navajo'], ['nbf', 'Naxi'], ['nd', 'Ndebele'], ['nap', 'Neapolitan'], ['yrk', 'Nenets'], ['ne', 'Nepali'], ['ncg', 'Nisga a'], ['zxx', 'None'], ['non', 'Norse, Old'], ['nai', 'North American Indian'], ['no', 'Norwegian'], ['qbk', 'Nushi'], ['nyk', 'Nyaneka'], ['ny', 'Nyanja'], ['oc', 'Occitan'], ['oj', 'Ojibwa'], ['qaz', 'Ojihimba'], ['ang', 'Old English'], ['or', 'Oriya'], ['pap', 'Papiamento'], ['qaj', 'Parsee'], ['ps', 'Pashtu'], ['paw', 'Pawnee'], ['fa', 'Persian'], ['qai', 'Peul'], ['myp', 'Pirahã'], ['pl', 'Polish'], ['qah', 'Polynesian'], ['pt', 'Portuguese'], ['fuf', 'Pular'], ['pa', 'Punjabi'], ['tsz', 'Purepecha'], ['qu', 'Quechua'], ['qya', 'Quenya'], ['raj', 'Rajasthani'], ['qbj', 'Rawan'], ['xrr', 'Rhaetian'], ['ro', 'Romanian'], ['rm', 'Romansh'], ['rom', 'Romany'], ['rtm', 'Rotuman'], ['ru', 'Russian'], ['rsl', 'Russian Sign Language'], ['qao', 'Ryukyuan'], ['qae', 'Saami'], ['sm', 'Samoan'], ['sa', 'Sanskrit'], ['sat', 'Santali'], ['sc', 'Sardinian'], ['qay', 'Scanian'], ['sr', 'Serbian'], ['qbo', 'Serbo-Croatian'], ['srr', 'Serer'], ['qad', 'Shanghainese'], ['qau', 'Shanxi'], ['shp', 'Shipibo'], ['sn', 'Shona'], ['shh', 'Shoshoni'], ['scn', 'Sicilian'], ['qsg', 'Silbo Gomero'], ['sjn', 'Sindarin'], ['sd', 'Sindhi'], 
['si', 'Sinhala'], ['sio', 'Sioux'], ['sk', 'Slovak'], ['sl', 'Slovenian'], ['so', 'Somali'], ['son', 'Songhay'], ['snk', 'Soninke'], ['wen', 'Sorbian languages'], ['st', 'Sotho'], ['qbe', 'Sousson'], ['es', 'Spanish'], ['ssp', 'Spanish Sign Language'], ['srn', 'Sranan'], ['sw', 'Swahili'], ['sv', 'Swedish'], ['gsw', 'Swiss German'], ['syl', 'Sylheti'], ['nmn', 'Taa'], ['tl', 'Tagalog'], ['tg', 'Tajik'], ['tmh', 'Tamashek'], ['ta', 'Tamil'], ['tac', 'Tarahumara'], ['tt', 'Tatar'], ['te', 'Telugu'], ['qak', 'Teochew'], ['th', 'Thai'], ['bo', 'Tibetan'], ['qan', 'Tigrigna'], ['tli', 'Tlingit'], ['tpi', 'Tok Pisin'], ['to', 'Tonga (Tonga Islands)'], ['ts', 'Tsonga'], ['tsc', 'Tswa'], ['tn', 'Tswana'], ['tcy', 'Tulu'], ['tup', 'Tupi'], ['tr', 'Turkish'], ['tk', 'Turkmen'], ['tyv', 'Tuvinian'], ['tue', 'Tuyuca'], ['tzo', 'Tzotzil'], ['uk', 'Ukrainian'], ['ukl', 'Ukrainian Sign Language'], ['qat', 'Ungwatsi'], ['ur', 'Urdu'], ['uz', 'Uzbek'], ['vi', 'Vietnamese'], ['qaa', 'Visayan'], ['was', 'Washoe'], ['cy', 'Welsh'], ['wo', 'Wolof'], ['xh', 'Xhosa'], ['sah', 'Yakut'], ['yap', 'Yapese'], ['yi', 'Yiddish'], ['yo', 'Yoruba'], ['ypk', 'Yupik'], ['zu', 'Zulu']]
    
    country = [['af', 'Afghanistan'], ['ax', 'Åland Islands'], ['al', 'Albania'], ['dz', 'Algeria'], ['as', 'American Samoa'], ['ad', 'Andorra'], ['ao', 'Angola'], ['ai', 'Anguilla'], ['aq', 'Antarctica'], ['ag', 'Antigua and Barbuda'], ['ar', 'Argentina'], ['am', 'Armenia'], ['aw', 'Aruba'], ['au', 'Australia'], ['at', 'Austria'], ['az', 'Azerbaijan'], ['bs', 'Bahamas'], ['bh', 'Bahrain'], ['bd', 'Bangladesh'], ['bb', 'Barbados'], ['by', 'Belarus'], ['be', 'Belgium'], ['bz', 'Belize'], ['bj', 'Benin'], ['bm', 'Bermuda'], ['bt', 'Bhutan'], ['bo', 'Bolivia'], ['bq', 'Bonaire, Sint Eustatius and Saba'], ['ba', 'Bosnia and Herzegovina'], ['bw', 'Botswana'], ['bv', 'Bouvet Island'], ['br', 'Brazil'], ['io', 'British Indian Ocean Territory'], ['vg', 
'British Virgin Islands'], ['bn', 'Brunei Darussalam'], ['bg', 'Bulgaria'], ['bf', 'Burkina Faso'], ['bumm', 'Burma'], ['bi', 'Burundi'], ['kh', 'Cambodia'], ['cm', 'Cameroon'], ['ca', 'Canada'], ['cv', 'Cape Verde'], ['ky', 'Cayman Islands'], ['cf', 'Central African Republic'], ['td', 'Chad'], ['cl', 'Chile'], ['cn', 'China'], ['cx', 'Christmas Island'], ['cc', 'Cocos (Keeling) Islands'], ['co', 'Colombia'], ['km', 'Comoros'], ['cg', 'Congo'], ['ck', 'Cook Islands'], ['cr', 'Costa Rica'], ['ci', 'Côte d*Ivoire'], ['hr', 'Croatia'], ['cu', 'Cuba'], ['cy', 'Cyprus'], ['cz', 'Czech Republic'], ['cshh', 'Czechoslovakia'], ['cd', 'Democratic Republic of the Congo'], ['dk', 'Denmark'], ['dj', 'Djibouti'], ['dm', 'Dominica'], ['do', 'Dominican Republic'], ['ddde', 'East Germany'], ['ec', 'Ecuador'], ['eg', 'Egypt'], ['sv', 'El Salvador'], ['gq', 'Equatorial Guinea'], ['er', 'Eritrea'], ['ee', 'Estonia'], ['et', 'Ethiopia'], ['fk', 'Falkland Islands'], ['fo', 'Faroe Islands'], ['yucs', 'Federal Republic of Yugoslavia'], ['fm', 'Federated States of Micronesia'], ['fj', 'Fiji'], ['fi', 'Finland'], ['fr', 'France'], ['gf', 'French Guiana'], ['pf', 'French Polynesia'], ['tf', 'French Southern Territories'], ['ga', 'Gabon'], ['gm', 'Gambia'], ['ge', 'Georgia'], ['de', 'Germany'], ['gh', 'Ghana'], ['gi', 'Gibraltar'], ['gr', 'Greece'], ['gl', 'Greenland'], ['gd', 'Grenada'], ['gp', 'Guadeloupe'], ['gu', 'Guam'], ['gt', 'Guatemala'], ['gg', 'Guernsey'], ['gn', 'Guinea'], 
['gw', 'Guinea-Bissau'], ['gy', 'Guyana'], ['ht', 'Haiti'], ['hm', 'Heard Island and McDonald Islands'], ['va', 'Holy See (Vatican City State)'], ['hn', 'Honduras'], ['hk', 'Hong Kong'], ['hu', 'Hungary'], ['is', 'Iceland'], ['in', 'India'], ['id', 'Indonesia'], ['ir', 'Iran'], ['iq', 'Iraq'], ['ie', 'Ireland'], ['im', 'Isle of Man'], ['il', 'Israel'], ['it', 'Italy'], ['jm', 'Jamaica'], ['jp', 'Japan'], ['je', 'Jersey'], ['jo', 'Jordan'], ['kz', 'Kazakhstan'], ['ke', 'Kenya'], ['ki', 'Kiribati'], ['xko', 'Korea'], ['xkv', 'Kosovo'], ['kw', 'Kuwait'], ['kg', 'Kyrgyzstan'], ['la', 'Laos'], ['lv', 'Latvia'], ['lb', 'Lebanon'], ['ls', 'Lesotho'], ['lr', 'Liberia'], ['ly', 'Libya'], ['li', 'Liechtenstein'], ['lt', 'Lithuania'], ['lu', 
'Luxembourg'], ['mo', 'Macao'], ['mg', 'Madagascar'], ['mw', 'Malawi'], ['my', 'Malaysia'], ['mv', 'Maldives'], ['ml', 'Mali'], ['mt', 'Malta'], ['mh', 'Marshall Islands'], ['mq', 'Martinique'], ['mr', 'Mauritania'], ['mu', 'Mauritius'], ['yt', 'Mayotte'], ['mx', 'Mexico'], ['md', 'Moldova'], ['mc', 'Monaco'], ['mn', 'Mongolia'], ['me', 'Montenegro'], ['ms', 'Montserrat'], ['ma', 'Morocco'], ['mz', 'Mozambique'], ['mm', 'Myanmar'], ['na', 'Namibia'], ['nr', 'Nauru'], ['np', 'Nepal'], ['nl', 'Netherlands'], ['an', 'Netherlands Antilles'], ['nc', 'New Caledonia'], ['nz', 'New Zealand'], ['ni', 'Nicaragua'], ['ne', 'Niger'], ['ng', 'Nigeria'], ['nu', 'Niue'], ['nf', 'Norfolk Island'], ['kp', 'North Korea'], ['vdvn', 'North Vietnam'], 
['mp', 'Northern Mariana Islands'], ['no', 'Norway'], ['om', 'Oman'], ['pk', 'Pakistan'], ['pw', 'Palau'], ['xpi', 'Palestine'], ['ps', 'Palestinian Territory'], ['pa', 'Panama'], ['pg', 'Papua New Guinea'], ['py', 'Paraguay'], ['pe', 'Peru'], ['ph', 'Philippines'], ['pl', 'Poland'], ['pt', 'Portugal'], ['pn', 'Pitcairn'], ['pr', 'Puerto Rico'], ['qa', 'Qatar'], ['mk', 'Republic of Macedonia'], ['re', 'Réunion'], ['ro', 'Romania'], ['ru', 'Russia'], ['rw', 'Rwanda'], ['bl', 'Saint Barthélemy'], ['sh', 'Saint Helena'], ['kn', 'Saint Kitts and Nevis'], ['lc', 'Saint Lucia'], ['mf', 'Saint Martin (French part)'], ['pm', 'Saint Pierre and Miquelon'], ['vc', 'Saint Vincent and the Grenadines'], ['ws', 'Samoa'], ['sm', 'San Marino'], ['st', 'Sao Tome and Principe'], ['sa', 'Saudi Arabia'], ['sn', 'Senegal'], ['rs', 'Serbia'], ['csxx', 'Serbia and Montenegro'], ['sc', 'Seychelles'], ['xsi', 'Siam'], ['sl', 'Sierra Leone'], ['sg', 'Singapore'], ['sk', 'Slovakia'], ['si', 'Slovenia'], ['sb', 'Solomon Islands'], ['so', 'Somalia'], ['za', 'South Africa'], ['gs', 'South Georgia and the South Sandwich Islands'], ['kr', 'South Korea'], ['suhh', 'Soviet Union'], ['es', 'Spain'], ['lk', 'Sri Lanka'], ['sd', 'Sudan'], ['sr', 'Suriname'], ['sj', 'Svalbard and Jan Mayen'], ['sz', 'Swaziland'], ['se', 'Sweden'], ['ch', 'Switzerland'], ['sy', 'Syria'], ['tw', 'Taiwan'], ['tj', 'Tajikistan'], ['tz', 'Tanzania'], ['th', 'Thailand'], ['tl', 'Timor-Leste'], ['tg', 'Togo'], ['tk', 'Tokelau'], ['to', 'Tonga'], ['tt', 'Trinidad and Tobago'], ['tn', 'Tunisia'], ['tr', 'Turkey'], ['tm', 'Turkmenistan'], ['tc', 'Turks and Caicos Islands'], ['tv', 'Tuvalu'], ['vi', 'U.S. Virgin Islands'], ['ug', 'Uganda'], ['ua', 'Ukraine'], ['ae', 'United Arab Emirates'], ['gb', 'United Kingdom'], ['us', 'United States'], ['um', 'United States Minor Outlying Islands'], ['uy', 'Uruguay'], ['uz', 'Uzbekistan'], ['vu', 'Vanuatu'], ['ve', 'Venezuela'], ['vn', 'Vietnam'], ['wf', 'Wallis and Futuna'], ['xwg', 'West Germany'], ['eh', 'Western Sahara'], ['ye', 'Yemen'], ['xyu', 'Yugoslavia'], ['zrcd', 'Zaire'], ['zm', 'Zambia'], ['zw', 'Zimbabwe']]

    companies =  [['20th Century Fox','fox' ],['Sony','columbia'], ['DreamWorks','dreamworks'], ['MGM','mgm'], ['Paramount','paramount'] ,['Universal','universal'] ,['Walt Disney','disney'] ,['Warner Bros.','warner']]

    awards = [['top_100', 'IMDb "Top 100"'], ['top_250', 'IMDb "Top 250"'], ['top_1000', 'IMDb "Top 1000"'], ['oscar_winners', 'Oscar-Winning'], ['emmy_winners', 'Emmy Award-Winning'], ['golden_globe_winners', 'Golden Globe-Winning'],
 ['oscar_nominees', 'Oscar-Nominated'], ['emmy_nominees', 'Emmy Award-Nominated'], ['golden_globe_nominees', 'Golden Globe-Nominated'], ['oscar_best_picture_winners', 'Best Picture-Winning'], ['oscar_best_director_winners', 
 'Best Director-Winning'], ['oscar_best_director_nominees', 'Best Director-Nominated'],  ['razzie_nominees', 'Razzie-Nominated'] , ['now-playing-us', 'Now-Playing'],
 ['national_film_registry', 'National Film Board Preserved'], ['razzie_winners', 'Razzie-Winning'], ['bottom_100', 'IMDb "Bottom 100"'], ['bottom_250', 'IMDb "Bottom 250"'], ['bottom_1000', 'IMDb "Bottom 1000"']] 

    return render_template('question7.html', languages=languages, country=country, companies=companies, awards=awards)


@app.route('/getmethod/<jsdata>')
def get_javascript_data(jsdata):
    global choices
    if jsdata != "new_request":
        choices = jsdata.split(",")
        choices.pop(0)
        string_ = ''
        for e in choices:
            string_ += f'{e},'
        choices = string_[:-1]
    return jsdata


@app.route("/target_endpoint")
def target():
	some_data = ""	# This is where the loading screen will be.
	return render_template('loading.html', my_data = some_data)


@app.route("/processing")
@login_required
@api_key_required
def processing():
    global choices 
    api_key = session.get("imdb_key")
    con = get_connexion1()
    connection = con[0]
    cursor = con[1]
    command1 = """Create Table IF NOT EXISTS search_data(search_string TEXT KEY, result TEXT, choice_acc TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT * FROM search_data WHERE search_string = '{choices}'")
    results_query = cursor.fetchall()

    if results_query == []:
        data = choices.split(",")
        data = ['neutral'] + data
        new_data = []
        settt = False
        
        # process the data collected by the question and format it
        for e in data:
            if e != '|' and settt == False:
                new_data.append(e)
                if new_data.index(e) == 5 and e != 'doesnt_matter':
                    if e == "2022":
                        new_data[5] = f"{e}-01-01,"
                    else:
                        formated_date = e.split("-")
                        formated_date_str = ''
                        for i in formated_date:
                            formated_date_str += f'{i}-01-01'
                            if formated_date.index(i) == 0:
                                formated_date_str += ','
                        new_data[5] = formated_date_str

                elif new_data.index(e) == 3 and e != 'doesnt_matter':
                    formated_date = e.split("-")
                    formated_date_str = ''
                    for i in formated_date:
                        formated_date_str += i
                        if formated_date.index(i) == 0:
                            formated_date_str += ','
                    new_data[3] = formated_date_str

            elif e == '|' and settt == False:
                settt = True
                sub = []
            elif e!= '|' and settt == True:
                sub.append(e)
            elif e == '|' and settt == True:
                settt = False
                new_data.append(sub)
                sub = []
        if new_data[6] == 'doesnt_matter':
            new_data[6] = 'en'
        parameters = ['keywords=','title_type=','genres=','user_rating=','certificates=','release_date=','languages=','countries=','companies=','groups=']
        users_choices = new_data
        
        com = f'?'
        for e in range(len(parameters)):
            if users_choices[e] != 'doesnt_matter' and users_choices[e] != 'neutral':
                if type(users_choices[e]) != list:
                    com += f'{parameters[e]}{users_choices[e]}'
                else:
                    if users_choices[e][0] != 'doesnt_matter':
                        com += f'{parameters[e]}'
                        for i in users_choices[e]:
                            com += f'{i},'
                        com = com[:-1]
                com += '&'
        com = com[:-1]
        com+= '&count=250'
        choice_acc = 'accurate'
        print(com)
        response = imdb_api_caller(com,'AdvancedSearch')

        if response['results'] == []:
            choice_acc = 'some_neglected'
            com = f'?'
            if users_choices[1][0] != 'doesnt_matter':
                com += f'{parameters[1]}'
                for i in users_choices[1]:
                    com += f'{i},'
                com = com[:-1]
                com += '&'
            if users_choices[2][0] != 'doesnt_matter':
                com += f'{parameters[2]}'
                for i in users_choices[2]:
                    com += f'{i},'
                com = com[:-1]
                com += '&'
            if users_choices[3] != 'doesnt_matter':
                com += f"{parameters[3]}{users_choices[3]}&"
            if users_choices[5] != 'doesnt_matter':
                com += f"{parameters[5]}{users_choices[5]}&"
            if com[-1] != '?':
                com = com[:-1]
            com+= '&count=250'
            if com == f'?':
                com = f'?groups=top_100'
            
            response = imdb_api_caller(com,'AdvancedSearch')
            
        else:
            pass

        if response['results'] == []:
            choice_acc = 'not_accurate'
            com = f'?groups=top_100'
            response = imdb_api_caller(com,'AdvancedSearch')
            
        all_data = []
        for e in response['results']:
            all_data.append(e['id'])
        str_all_data = json.dumps(all_data)
        session["all_data"] = str_all_data
        cursor.execute("INSERT INTO search_data Values (?, ?, ?)", (choices,str_all_data, choice_acc))
        connection.commit()
    else:
        ol = results_query[0]
        session["all_data"] = ol[1]
        choice_acc = ol[2]
    if choice_acc == 'some_neglected':
        flash("Some of your parameters were neglected cause no content matches your parameters.", 'error')
    elif choice_acc == 'not_accurate':
        flash("We didn't find any content that matches your parameters, so we'll give you IMDB top-100 content.", 'error')

    print(choice_acc)
    session["item_number"] = '0'

    connection.close()
    return procgetnewrecommendationessing()


@app.route("/getnewrecommendation")
@login_required
@api_key_required
def procgetnewrecommendationessing():
    all_data = json.loads(session.get("all_data"))
    # item_choosen = random.randint(0,len(all_data)-1)
    # numm = int(session["item_number"])
    # session["item_number"] = str(int(session["item_number"]) + 1)
    # item_choosen = numm

    len_of_data = len(all_data)
    choices = []
    for e in range(len_of_data):
        choices.append(e)

    for e in choices:
        choices.append(e)
        if len(choices) > len_of_data + len_of_data / 2:
            break

    for e in choices:
        choices.append(e)
        if len(choices) > len_of_data * 1.5 + len_of_data / 2:
            break

    item_choosen = random.choice(choices)


    con = get_connexion1()
    connection = con[0]
    cursor = con[1]
    command1 = """Create Table IF NOT EXISTS content_data(id TEXT KEY, data TEXT)"""
    cursor.execute(command1)

    cursor.execute(f"SELECT data FROM content_data WHERE id='{all_data[item_choosen]}'")
    results_query = cursor.fetchall()

    if results_query:
        ol = results_query[0][0]
        data = json.loads(ol)
    else:
        data = get_content(all_data[item_choosen],cursor,connection)
        if data == 'failed':
            procgetnewrecommendationessing()

    connection.close()
    list = []
    for e in range(len(data[0])):
        list.append(e)
    list.append(list[-1] +1)
    return render_template('success.html',data=data,list=list)


