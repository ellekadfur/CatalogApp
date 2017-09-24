#!/usr/bin/env python3


from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from catalogdb import Base, User, Category, Item
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from flask import make_response
from io import StringIO

import random
import httplib2
import json
import requests
import string

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('google_client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Login Page"""
    # Creating random token then saving it to state key in login_session
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    print("Login called with state - {}".format(state))
    return render_template('login.html', STATE=state)


@app.route('/disconnect')
def disconnect():
    """Disconnect Based on Provider"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Facebook Login Functions


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Facebook Login"""
    # the user is not a valid user, meaning they did not arrive here from the
    # /login page so respond with 401 error meaning, Unauthorized.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # else user is valid
    # obtain authorization code
    code = request.data.decode(encoding='UTF-8')
    print("access token received: {}".format(code))
    # ljc - might crash?

    app_id = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open(
        'fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_'
    url += 'exchange_token&client_id'
    url += '={}&client_secret={}&fb_exchange_token={}'.format(
        app_id, app_secret, code)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # variable = ["hello", "dude"]
    # print("url:--%s--" % url)
    # print("variable:--%s--" % variable)
    # print("result:--%s--" % result.decode(encoding='UTF-8'))

    decoded_result = result.decode(encoding='UTF-8')
    theData = json.loads(decoded_result)
    # print("theData:--%s--" % theData)

    token = theData['access_token']

    # Use token to get user info from Facebook Graph API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    url = '%s?access_token=%s&fields=name,id,email' % (userinfo_url, token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print("url sent for API access:%s" % url)
    print("API JSON result: %s" % result)
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    # The token is stored in the login_session so we can properly logout
    login_session['access_token'] = token

    # Get user picture
    url = (
        '%s/picture?access_token=%s&redirect=0&height=200&width=200'
        % (userinfo_url, token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcom, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style - "width: 300px height:300px;border-radius:150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;">'

    flash('Now logged in as %s' % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    """Facebook logout"""
    facebook_id = login_session['facebook_id']
    # Must use access token to log output
    access_token = login_session['access_token']
    url = (
        'https://graph.facebook.com/%s/permission?access_token=%s'
        % (facebook_id, access_token))
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have logged out'


# Google Login Functions


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Google Login"""
    # the user is not a valid user, meaning they did not arrive here from the
    # /login page so respond with 401 error, Unauthorized.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid State Parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # else user is valid
    # obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(
            'google_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        # Return 401 error, Unauthorized
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, return 500,
    # Internal Server Error.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        # Return 401 error, Unauthorized
        response = make_response(
            json.dumps('Token\'s client ID does not match user ID.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        # Return 401 error, Unauthorized
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
    return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        # Return 200 success, Request Fulfilled
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # else user is not already logged in
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected User.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # return 400 error, Bad request
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        reponse.heaers['Content-type'] = 'application/json'
        return response


# User Helper Funcations


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        photo=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Routing methods


@app.route('/')
@app.route('/catalog/')
@app.route('/categories/')
def showCategories():
    """Home Page & View All Categories/Catalog"""
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(Item.created_date)
    if 'username' not in login_session:
        login_session.clear()
    return render_template(
        'categories.html', categories=categories, items=items)


@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newItem():
    """Create New Item"""
    categories = session.query(Category).order_by(asc(Category.name))
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] != category.user_id:
        output = "<script>function myFunction(){alert('You are not "
        output += "able to add items to a category.');}</script><body "
        output += "onload='myFuncation()''>"
        return output
    if request.method == 'POST':
        # print("request.form:{}".format(request.form));
        newItem = Item(
            name=request.form.get('title', None),
            description=request.form.get('desc', None),
            user_id=login_session['user_id'],
            category_id=request.form.get('category_id', None))
        session.add(newItem)
        session.commit()
        flash('New Item %s Successfully Created' % newItem.name)
        # return render_template('categories.html', categories=categories, )
        return redirect(url_for('showCategories'))
    else:
        return render_template('new_item.html', categories=categories)


@app.route('/cataglog/item/<int:item_id>/view/', methods=['GET'])
def viewItem(item_id):
    """Edit an Item"""
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('view_item.html', item=item)


@app.route('/cataglog/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(item_id):
    """Edit an Item"""
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item.user_id:
        output = "<script>function myFunction(){alert('You are not "
        output += "able to edit this item.');}</script><body "
        output += "onload='myFuncation()''>"
        return output
    if request.method == 'POST':
        if request.form['title']:
            item.name = request.form['title']
        if request.form['desc']:
            item.description = request.form['desc']
        if request.form['category_id']:
            item.category_id = request.form['category_id']
        session.add(item)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template(
            'edit_item.html', item=item, categories=categories)


@app.route('/catalog/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(item_id,):
    """Delete an Item"""
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item.user_id:
        output = "<script>function myFunction(){alert('You are not "
        output += "able to delete this item.');}</script><body "
        output += "onload='myFuncation()''>"
        return output
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        return render_template('delete_item.html', item=item)


@app.route('/categories/JSON')
def restaurantsJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # app.run(host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', port=8000)
