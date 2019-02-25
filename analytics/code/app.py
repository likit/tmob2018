from flask import Flask, render_template
from ohec import ohec as ohec_blueprint

app = Flask(__name__)

app.register_blueprint(ohec_blueprint, url_prefix='/ohec')

@app.route('/')
def index():
    return render_template('main/index.html')
