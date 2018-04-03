#!/usr/bin/python3

from flask import Flask, render_template, url_for, request, session, redirect
from os import listdir, makedirs

def jsdump(dct, filename):
  from json import dump
  dump(dct, open(filename, 'wt'), indent = 2)

def jsload(filename):
  from json import load
  return load(open(filename, 'rt'))

app = Flask('Bloggo')

app.secret_key = open('secret_key', 'rb').read()

@app.route('/')
def index():
  return redirect(url_for('show_profile'))

@app.route('/profile/')
def show_profile():
  if 'username' not in session:
    return redirect(url_for('signin'))
  return show_user_profile(session['username'], True)

@app.route('/user/<username>/')
def show_user_profile(username, my = False):
  if not my and 'username' in session and username == session['username']:
    return redirect(url_for('show_profile'))

  info = jsload('user/{username}/info.json'.format(username = username))
  name = info['name']
  surname = info['surname']
  profile_picture_link = info['profile_picture_link']
  userbio = info['bio']

  files = [ (int(file[:-len('.json')]), file) for file in listdir('user/' + username + '/post/') ]
  files.sort()
  posts = [ (pair[0], jsload('user/' + username + '/post/' + pair[1])) for pair in files ][::-1]
  picture = url_for('static', filename = profile_picture_link)

  return render_template('profile.html', picture  = picture,
                                         username = username,
                                         name     = name,
                                         surname  = surname,
                                         userbio  = userbio,
                                         posts    = posts)

@app.route('/post/<int:post_id>/')
def show_post(post_id):
  if 'username' not in session:
    return redirect(url_for('signin'))
  return show_user_post(session['username'], post_id, True)

@app.route('/user/<username>/post/<int:post_id>/')
def show_user_post(username, post_id, my = False):
  if not my and 'username' in session and username == session['username']:
    return redirect(url_for('show_post', post_id = post_id))
  post = jsload('user/{username}/post/{post_id}.json'.format(username = username, post_id = post_id))
  head = post['head']
  text = post['text'].replace('\r\n', '(%br%)')
  return render_template('post.html', username = username,
                                      head = head,
                                      text = text,
                                      post_id = post_id,
                                      editable = ('username' in session and username == session['username'])).replace('(%br%)', '<br>')

@app.route('/new_post/', methods = ['GET', 'POST'])
def add_post():
  if 'username' not in session:
    return redirect('/signin')
  if request.method == 'POST':
    head = request.form['head']
    text = request.form['text']
    n = len(listdir('user/{username}/post/'.format(username = session['username'])))
    jsdump({ 'head': head, 'text': text }, 'user/{username}/post/{n}.json'.format(username = session['username'], n = n))
    return redirect(url_for('show_user_profile', username = session['username']))
  return render_template('new_post.html', where = '/new_post/')

@app.route('/edit/post/<int:post_id>/', methods = ['GET', 'POST'])
def edit_post(post_id):
  if 'username' not in session:
    return redirect('/signin')
  if request.method == 'POST':
    head = request.form['head']
    text = request.form['text']
    import json
    jsdump({ 'head': head, 'text': text }, 'user/{username}/post/{n}.json'.format(username = session['username'], n = post_id))
    return redirect(url_for('show_user_profile', username = session['username']))
  info = jsload('user/{username}/post/{n}.json'.format(username = session['username'], n = post_id))
  head = info['head']
  text = info['text']
  return render_template('new_post.html', where = '/edit/post/{post_id}/'.format(post_id = post_id),
                                          head = head, text = text)

def check_user(username, password):
  users = listdir('user/')
  if username not in users:
    return 'wrong username'
  password_hash = jsload('user/{username}/info.json'.format(username = username))['password_hash']
  from Crypto.Hash import SHA256
  hashing = SHA256.new()
  hashing.update(bytes(password, 'ascii'))
  if str(hashing.digest()) != password_hash:
    return 'wrong password'
  return None

@app.route('/signin/', methods = ['GET', 'POST'])
def signin():
  if request.method == 'POST':
    error = check_user(request.form['username'], request.form['password'])
    if error == None:
      session['username'] = request.form['username']
      return redirect(url_for('show_user_profile', username = request.form['username']))
    else:
      return render_template('signin.html', error = error)
  return render_template('signin.html' )

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    if username.find(' ') != -1:
      return render_template('signup.html', error = 'Username mustn\'t contain spaces')
    if username.find('/') != -1:
      return render_template('signup.html', error = 'Username mustn\'t contain "/" symbols')
    if username in listdir('user/'):
      return render_template('signup.html', error = 'Username already exists!')
    password = request.form['password']
    password_repeat = request.form['password_repeat']
    if password != password_repeat:
      return render_template('signup.html', error = 'Passwords don\'t match')
    name = request.form['name']
    surname = request.form['surname']
    bio = request.form['bio']
    if 'profile_pic' in request.files:
      f = request.files['profile_pic']
      profile_picture_link = 'profile_picture/{username}.{typo}'.format(username = username, typo = f.mimetype.split('/')[1])
      f.save('static/{profile_picture_link}'.format(profile_picture_link = profile_picture_link))
    else:
      profile_picture_link = 'profile_picture/default.jpg'
    import json
    from Crypto.Hash import SHA256
    hashing = SHA256.new()
    hashing.update(bytes(password, 'ascii'))
    makedirs('user/{username}/post'.format(username = username))
    jsdump({ 'password_hash': str(hashing.digest()),
             'name': name,
             'surname': surname,
             'profile_picture_link': profile_picture_link,
             'bio': bio },
           'user/{username}/info.json'.format(username = username))
    return redirect(url_for('signin'))
  return render_template('signup.html')

@app.route('/edit_profile/')
def edit_profile():
  pass

@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect('/')

if __name__ == '__main__':
	app.run(debug = True, host = '0.0.0.0')