import os
from flask import Flask, render_template, url_for, redirect
from sqlalchemy import create_engine, MetaData, Table, select

POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

app = Flask(__name__)

engine = create_engine('postgresql+psycopg2://postgres:{}@postgres_db/scopuspubs'.format(POSTGRES_PASSWORD))
metadata = MetaData()
conn = engine.connect()

from ohec import ohec as ohec_blueprint
from domain_scan import domain as domain_blueprint

app.register_blueprint(ohec_blueprint, url_prefix='/ohec')
app.register_blueprint(domain_blueprint, url_prefix='/domain')

@app.route('/')
def index():
    return redirect(url_for('ohec.index'))
