from flask import Flask, render_template, url_for, redirect
from ohec import ohec as ohec_blueprint

app = Flask(__name__)

app.register_blueprint(ohec_blueprint, url_prefix='/ohec')

@app.route('/')
def index():
    return redirect(url_for('ohec.index'))
