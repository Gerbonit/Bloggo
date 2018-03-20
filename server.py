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

def check_user(username, password):
  from os import listdir
  users = listdir('user/')
  if username not in users:
    return 'wrong username'
  password_hash = eval(open('user/' + username + '/info.json', 'rt').read())['password_hash']
  from Crypto.Hash import SHA256
  hashing = SHA256.new()
  hashing.update(bytes(password, 'ascii'))
  print(password_hash)
  print(password)
  print(str(hashing.digest()))
  if str(hashing.digest()) != password_hash:
    return 'wrong password'
  return None

@app.route('/signin/', methods=['GET', 'POST'])
def signin():
  if request.method == 'POST':
    session['username'] = request.form['username']
    error = check_user(request.form['username'], request.form['password'])
    if error == None:
      return redirect(url_for('show_user_profile', username = request.form['username']))
    else:
      return render_template('signin.html', error = error)
  return render_template('signin.html' )

@app.route('/logout')
def logout():
  session.pop('username', None)
  return redirect('/')

if __name__ == '__main__':
	app.run(debug = True)