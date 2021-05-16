import os
from flask import Flask, render_template, url_for, request, session, send_file, redirect
import pandas as pd
from markupsafe import escape
import tweepy
import json
import io
import re
import requests
import mysql.connector
# from flask_session import Session

import nltk
from nltk.corpus import stopwords

# run usi
# .\virtual\Scripts\activate.bat
# set FLASK_ENV=development
# flask run

# twitter keys
consumer_key = 'Ey08FlTmt72rChOt0hxg1f6Bu'
consumer_secret = 'sP28Af1rsNTklG9XzghMp48MIFj1GygYjXkcSjTfoA7LRWm987'
access_token = '2987342592-zptDUduhr1QhEQgVrmZRtCy6ER2Skas7yf2D5wj'
access_token_secret = 'NPXqErsaDxiJ5dpTsvYS07zurrPiLcjo9Zjvei30BY2SF'


mysql = mysql.connector


def FindMaxLength(lst):
    maxList = max(lst, key=len)
    maxLength = max(map(len, lst))
    return maxList, maxLength


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__, instance_relative_config=True)
    
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    # Session(app)

    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    # )

    # with app.app_context():
    #     return url_for('static', filename='style.css')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # # a simple page that says hello
    # @app.route('/hello')
    # def hello():
    #     return 'Whatsup Egghead!'

    # @app.route('/')
    # @app.route('/<name>')
    # def index(name=None):
    #     if name == None:
    #         return render_template('index.html', name='stevee')
    #     else:
    #         return render_template('index.html', name=name)

    @app.route("/download", methods=["POST"])
    def download():
        return 'Whatsup Egghead!'
        # csv = session.get("df") if "df" in session else ""

        # buf_str = io.StringIO(csv)

        # buf_byt = io.BytesIO(buf_str.read().encode("utf-8"))

        # return send_file(buf_byt,
        #                  mimetype="text/csv",
        #                  as_attachment=True,
        #                  attachment_filename="tweets.csv")

    @app.route('/home')
    def home():
        search = request.args.get('query')
        count = request.args.get('count')
        filter = request.args.get('filter')
        if(search == None or search == None or count == None or filter == None):
            return render_template('home.html')
        if(int(count) < 10):
            return render_template('home.html', error="Count cannot be less than 10!")
        if(filter == ''):
            return render_template('home.html', error="Filter cannot be null")

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # TODO: use nltk to split data and use 'word1 OR word2' on querys
        if(len(search.split(' ')) > 2):
            # print(stopwords.words('english'))
            # Cleaning Text
            # remove symbols
            search = re.sub("[^-9A-Za-z ]", "", search)
            # # remove stop words like is A the
            # stop_words = set(stopwords.words('english'))
            # word_tokens = nltk.word_tokenize(search)
            # search = [w for w in word_tokens if not w in stop_words]

            tokenized = nltk.word_tokenize(search)
            nouns = [word for (word, pos) in nltk.pos_tag(
                tokenized) if(pos[:2] == 'NN')]
            lst, searchText = FindMaxLength(nouns)
            print(lst)
            print(searchText)

        # public_tweets = api.user_timeline(search)
        public_tweets = api.search(
            search, count=int(count), result_type=filter, lang='en')

        '''
        https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline
        'author', 'contributors', 'coordinates', 'created_at', 'destroy', 'entities', 
        'favorite', 'favorite_count', 'favorited', 'geo', 'id', 'id_str', 'in_reply_to_screen_name', 
        'in_reply_to_status_id', 'in_reply_to_status_id_str', 'in_reply_to_user_id', 'in_reply_to_user_id_str', 
        'is_quote_status', 'lang', 'parse', 'parse_list', 'place', 'retweet', 'retweet_count', 'retweeted', 
        'retweeted_status', 'retweets', 'source', 'source_url', 'text', 'truncated', 'user'

        ['created_at', 'id', 'id_str', 'text', 'truncated', 'entities', 'source', 'in_reply_to_status_id', 
        'in_reply_to_status_id_str', 'in_reply_to_user_id', 'in_reply_to_user_id_str', 'in_reply_to_screen_name',
         'user', 'geo', 'coordinates', 'place', 'contributors', 'retweeted_status', 'is_quote_status', 
         'retweet_count', 'favorite_count', 'favorited', 'retweeted', 'lang'])
        '''
        # print('FC',public_tweets[0].retweeted_status.favorite_count)
        # public_tweets = json.dumps([status._json for status in public_tweets])
        # print(public_tweets)

        # df = pd.DataFrame(public_tweets)
        # session["df"] = df.to_csv(index=False, header=True, sep=";")

        # print(bool(session.get("df")))
        return render_template('home.html', tweets=public_tweets)

    @app.route('/', methods=['GET'])
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            mydb = mysql.connect(
                host="localhost",
                user="root",
                password="Steven@1996",
                database="bookstore",
                auth_plugin='mysql_native_password'
            )
            cursor = mydb.cursor()
            sql = "SELECT * FROM users WHERE username = '" + \
                username+"' AND password = '"+password+"'"
            # sql = "SELECT * FROM users WHERE username = '"+username+"'"
            # print(sql)
            cursor.execute(sql)
            users = cursor.fetchone()
            if users:
                session['loggedin'] = True
                session['id'] = users[0]
                session['username'] = users[1]
                # session['id'] = users['id']
                # session['username'] = users['username']
                msg = 'Logged in successfully !'
                return render_template('home.html', msg=msg)
            else:
                msg = 'Incorrect username / password !'
        return render_template('login.html', msg=msg)

    @app.route('/logout')
    def logout():
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            mydb = mysql.connect(
                host="localhost",
                user="root",
                password="Steven@1996",
                database="bookstore", auth_plugin='mysql_native_password'
            )
            cursor = mydb.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = %s', (username,))
            users = cursor.fetchone()
            if users:
                msg = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
            elif not username or not password or not email:
                msg = 'Please fill out the form !'
            else:
                cursor.execute(
                    'INSERT INTO users (user_id, username, password, email) VALUES ((SELECT MAX(user_id)+1 from users u1), %s, %s, %s )', (username, password, email))
                mydb.commit()
                msg = 'You have successfully registered !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('register.html', msg=msg)

    @app.route('/profile/')
    @app.route('/profile/<name>')
    def profile(name=None):
        print('name', name)
        if(name == None):
            return "No username is provided!!"
        url = 'https://api.twitter.com/2/users/by/username/'+name+'?user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
        headers = {'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAN7sLwEAAAAAYb0Ou2Mb8f3bgj264NY2Pp9nQjg%3DQDOdTGLcI01bnaMSEj57xQo4FQtr5UAw5priFvbFhva2gDmNLT'}
        r = requests.get(url, headers=headers)
        # print(r)
        json_string = r.json()['data']
        return render_template('profile.html', data=json_string)

    return app
