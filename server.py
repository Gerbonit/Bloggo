#!/usr/bin/python3

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, make_response

app = Flask('Blog')

@app.route('/blank/')
def return_blank_page():
  return '\0'

@app.route('/user/<username>/')
def setup_layout(username):
  return render_template('layout.html', main = '/user/' + username + '/main/')

@app.route('/user/<username>/main/')
def show_user_profile(username):
  from os import listdir
  return render_template('/profile.html', user_profile_pic = '/user/' + username + '/profile_picture/',
                                          username = username,
                                          userbio = open('users/' + username + '/posts/0', 'rt').read(),
                                          posts = [ open('users/' + username + '/posts/' + file, 'rt').read()
                                                    for file in listdir('users/' + username + '/posts') ][1:])

@app.route('/user/<username>/profile_picture/')
def return_profile_picture(username):
  from os import listdir
  items = listdir('users/' + username + '/')
  for item in items:
    if item.find('profile_picture') != -1:
      resp = make_response(open('users/' + username + '/' + item, 'rb').read(), 200)
      resp.headers['Content-Type'] = 'image/' + item[len('profile_picture') + 1:]
      return resp
  return ('', 404)

if __name__ == '__main__':
  app.run(debug = True)