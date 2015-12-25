"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import Views.views
import eenum
import switch
import webhook
