from email.message import EmailMessage
import smtplib
import requests
import json
from flask import redirect, render_template, request, session, abort, url_for
from functools import wraps
import sqlite3
import random


global parameter_500
parameter_500 = ['500',"Internal server crash","Reasons: Maybe because the site was overloaded with too many visiters or because of a bug",
                "Solutions: Press the button below and try again multiple times if this page comes over and over again than we're sorry you should try again later when there isn't many visiters or the bug is fixed"]


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("imdb_key") is None:
            return redirect("/setimdbkey")
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/redirect_to_login")
        return f(*args, **kwargs)
    return decorated_function



def get_connexion1():
    connection = sqlite3.connect('site_data.db', check_same_thread=False)
    cursor = connection.cursor()
    return [connection,cursor]

def change_500(param):
    global parameter_500
    parameter_500 = param
    abort(500)
    

def imdb_api_caller(values,parameter):
    global parameter_500
    api_key = session.get("imdb_key")
    payload = {}
    headers= {}
    response = requests.request("GET", f'https://imdb-api.com/en/API/{parameter}/{api_key}{values}', headers=headers, data = payload).json()
    if response['errorMessage'] == 'Server busy':
        parameter_500 = ['500',"Server busy","Reasons: It's most likely because IMDB's server is busy or down.",
                "Solutions: Press the button below and try again multiple times if this page comes over and over again than we're sorry please try again later when IMDB fixes their server or after 5 minutes."]
        abort(500)

    elif response['errorMessage'] == 'Year is empty':
        parameter_500 = ['500',"Data corrupted or missing","Reasons: It's most likely because the data retrieved from IMDB is corrupted or missing.",
                "Solutions: Press the button below and try again multiple times if this page comes over and over again than we're sorry it might be a bug in the site or from IMDB."]
        abort(500)

    elif response['errorMessage'] == 'Invalid API Key':
        parameter_500 = ['500',"Invalid API Key","Reasons: It's most likely because your IMDB api key got banned by imdb or blocked or even lost in our database.",
                "Solutions: Press the button below and try again multiple times if this page comes over and over again than try to reset your api key by making a new one and replacing this current one with the new one."]
        abort(500)

    elif response['errorMessage'] == 'Email not confirmed':
        parameter_500 = ['500',"Email not confirmed","Reasons: It's most likely because you didn't confirm your email when creating your IMDB account/api key.",
                "Solutions: Press the button below and go confirm your IMDB account by clicking on the confirmation email."]
        abort(500)

    elif response['errorMessage'] == 'Your API Key has expired':
        parameter_500 = ['500',"Your API Key has expired","Reasons: It's most likely because Your API Key has expired.",
                "Solutions: Press the button below and go renew your api key or get a new one."]
        abort(500)

    elif response['errorMessage'] == 'Bad Request':
        parameter_500 = ['500',"Bad Request","Reasons: It's most likely because of a bug or a corrupted request.",
                "Solutions: Press the button below and try again multiple times if this page comes over and over again than please contact the dev aka chakib."]
        abort(500)

    elif response['errorMessage'] == 'Deleted for copyright':
        parameter_500 = ['500',"Deleted for copyright","Reasons: It's most likely because the content you requested was deleted by IMDB because of copyright.",
                "Solutions: Press the button below and try again with different parameters."]
        abort(500)
    
    elif response['errorMessage'] == 'List is empty':
        parameter_500 = ['500',"List is empty","Reasons: It's most likely because the content you requested was null aka empty/nothing.",
                "Solutions: Press the button below and try again with different parameters."]
        abort(500)
    
    elif response['errorMessage'] == 'Invalid Id':
        parameter_500 = ['500',"Invalid Id","Reasons: It's most likely because you've modified the url/link or because of an internal bug.",
                "Solutions: Press the button below and try again with different parameters or don't modify the url."]
        abort(500)

    elif response['errorMessage'] == '404 Not Founded Error':
        parameter_500 = ['500',"404 Not Founded Error","Reasons: It's most likely because the request returned a missing response/data.",
                "Solutions: Press the button below and try again or try different parameters."]
        abort(500)
   
    try:
        if 'Your account has been suspended' in response['errorMessage']:
            parameter_500 = ['500',"Your account has been suspended","Reasons: It's most likely because your IMDB api key got banned by imdb or blocked.",
                    "Solutions: Press the button below and try again multiple times if this page comes over and over again than try to reset your api key by making a new one and replacing this current one with the new one."]
            abort(500)
        elif 'It is mandatory to enter at least one filter' in response['errorMessage']:
            parameter_500 = ['500',"It is mandatory to enter at least one filter","Reasons: It's most likely because your request was bad.",
                    "Solutions: Press the button below and try again multiple times if this page comes over and over again than try to choose other options."]
            abort(500)

        elif 'Maximum usage' in response['errorMessage']:
            parameter_500 = ['500',"Surpassed maximum IMDB api usage","Reasons: Imdb only provides 100 api calls a day, so it's most likely you've surpassed those 100 api calls.",
                    "Solutions: I'm sorry to say it but the only solution is to wait until tomorrow so imdb can restart your api call count."]
            abort(500)
    except TypeError:
        pass

    # if response['errorMessage'] != None or response['errorMessage'] != '':
    #     parameter_500 = ['500',"An unknown error occured","Reasons: We are sorry but we coudn't figure out what exactly triggered this error.",
    #             "Solutions: We're sorry but we don't know the reason for the error, but you can try clicking the button below and try again."]
    #     abort(500)

    return response



def get_content(title_id,cursor,connection):
    response = imdb_api_caller(f'/{title_id}/Trailer,Wikipedia,','Title')
    current_e = []

    e = response

    current_e.append(e['image'])
    current_e.append(e['releaseDate'])
    current_e.append(e['imDbRating'])
    current_e.append(e['contentRating'])
    if e['type'] == "TVSeries":
        current_e.append(f"{e['tvSeriesInfo']['seasons'][-1]} seasons")
    else:
        current_e.append(e['runtimeStr'])
    stars = ''
    for i in e['starList']:
        if e['starList'].index(i) < 3:
            stars += f"{i['name']}, "
        elif e['starList'].index(i) == 3:
            stars += f"{i['name']}"
    stars = stars[:-1]
    current_e.append(stars)
    try:
        current_e.append(e['writerList'][0]['name'])
    except:
        current_e.append("None")

    current_e.append(e['title'])
    current_e.append(e['plot'])
    current_e.append(e['wikipedia']['url'])
    current_e.append(e['trailer']['videoId'])
    current_e.append(e['type'])
    current_e.append(e['id'])
    data = current_e
    str_all_data = json.dumps(data)
    cursor.execute("INSERT INTO content_data Values (?, ?)",(title_id , str_all_data))
    connection.commit()
    print('new data')
    return data



def send_a_verification_code(to):
    code = int(random.randint(100000, 999999))
    subject = f"{code} is your verification code"
    body = "There's one quick step you need to complete before creating your MovCommender account. Let's "\
                "make sure this is your real email address , if you didn't request any verification code and you don't know what is this just ignore this message.\n\n"\
                "Please enter this verification code to get started on Caura:\n\n"\
                f"{code}\n\n"
    msg = EmailMessage()
    msg.set_content(body)
    msg["subject"] = subject
    msg["to"] = to
    user = "realCaura@gmail.com"
    password = "nhefflqitrdssdpb"  
    msg["from"] = user
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)
    server.quit()
    return code 