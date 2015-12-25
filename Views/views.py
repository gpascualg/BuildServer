"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, session
from Views import app
from webhook import Webhook
import random
import string
import urllib

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/callback')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/register')
def register():
    session['state'] = ''.join(random.SystemRandom().choice(string.printable) for _ in range(256))

    client_id = app.user_config['client_id']
    scopes = ','.join(app.user_config['scopes'])
    state = urllib.quote(session['state'])

    return redirect('https://github.com/login/oauth/authorize?client_id=' + client_id + '&scope=' + scopes + '&state=' + state, code=302)


@app.route('/hooks', methods=('POST',))
def about():
    webhook = Webhook(request.data)

    print webhook
    print webhook.action
    print webhook.data
