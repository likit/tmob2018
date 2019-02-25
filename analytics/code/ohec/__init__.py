from flask import Blueprint

ohec = Blueprint('ohec', __name__)

from . import views