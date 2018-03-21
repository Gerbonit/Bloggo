#!/usr/bin/python3

from flask import Flask, render_template, url_for, request, session, redirect

app = Flask('Bloggo')

app.secret_key = open('secret_key', 'rb').read()

@app.route('/user/<username>/')
def show_user_profile(username):
  from os import listdir

  info = eval(open('user/' + username + '/info.json', 'rt').read())
  name = info['name']
  surname = info['surname']
  site = info['site']
  profile_picture_link = info['profile_picture_link']
  userbio = info['bio']

  files = [ (int(file[:-len('.json')]), file) for file in listdir('user/' + username + '/post/') ]
  files.sort()
  posts = [ (pair[0], eval(open('user/' + username + '/post/' + pair[1], 'rt').read())) for pair in files ][::-1]
  picture = url_for('static', filename = profile_picture_link)

  return render_template('profile.html', picture  = picture,
                                         username = username,
                                         name     = name,
                                         surname  = surname,
                                         userbio  = userbio,
                                         posts    = posts)

@app.route('/user/<username>/post/<post_id>/')
def show_user_post(username, post_id):
  post = eval(open('user/' + username + '/post/' + post_id + '.json', 'rt').read())
  head = post['head']
  text = post['text']
  return render_template('post.html', username = username,
                                      head = head,
                                      text = text)

@app.route('/new_post/', methods = ['GET', 'POST'])
def add_post():
  if 'username' not in session:
    return redirect('/signin')
  if request.method == 'POST':
    head = request.form['head']
    text = request.form['text']
    from os import listdir
    n = len(listdir('user/{username}/post/'.format(username = session['username'])))
    import json
    with open('user/{username}/post/{n}.json'.format(username = session['username'], n = n), 'wt') as file:
      file.write(json.dumps({ 'head': head, 'text': text }, indent = 2))
    return redirect(url_for('show_user_profile', username = session['username']))
  return render_template('new_post.html')

def check_user(username, password):
  from os import listdir
  users = listdir('user/')
  if username not in users:
    return 'wrong username'
  password_hash = eval(open('user/' + username + '/info.json', 'rt').read())['password_hash']
  from Crypto.Hash import SHA256
  hashing = SHA256.new()
  hashing.update(bytes(password, 'ascii'))
  if str(hashing.digest()) != password_hash:
    return 'wrong password'
  return None

@app.route('/signin/', methods = ['GET', 'POST'])
def signin():
  if request.method == 'POST':
    session['username'] = request.form['username']
    error = check_user(request.form['username'], request.form['password'])
    if error == None:
      return redirect(url_for('show_user_profile', username = request.form['username']))
    else:
      return render_template('signin.html', error = error)
  return render_template('signin.html' )

@app.route('/signup/', methods = ['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form('username')
    password = request.form('password')
    password_repeat = request.form('password_repeat')
    return redirect(url_for('signin'))
  return render_template('signup.html')

@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect('/')

if __name__ == '__main__':
	app.run(debug = True, host = '0.0.0.0')