#!/usr/bin/python3

from flask import Flask, render_template, url_for

app = Flask('Bloggo')

@app.route('/user/<username>/')
def show_user_profile(username):
  from os import listdir

  info = eval(open('user/' + username + '/info.json', 'rt').read())
  name = info['name']
  surname = info['surname']
  site = info['site']
  profile_picture_type = info['profile_picture_type']

  files = [ (int(file), file) for file in listdir('user/' + username + '/post/') ]
  files.sort()
  userbio, *posts = [ (pair[1], *open('user/' + username + '/post/' + pair[1], 'rt').read().split('::=', 1)) for pair in files ]

  userbio = userbio[1]
  posts = posts[::-1]
  picture = url_for('static', filename = 'profile_picture/' + username + '.' + profile_picture_type)

  return render_template('profile.html', picture  = picture,
                                         username = username,
                                         name     = name,
                                         surname  = surname,
                                         userbio  = userbio,
                                         posts    = posts)

if __name__ == '__main__':
	app.run(debug = True)
