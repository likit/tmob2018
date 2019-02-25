from . import ohec
from flask import jsonify, render_template
import pandas as pd

YEARS = [2559, 2560, 2561, 2562]
BACKGROUND_COLORS = [
    "#194887",
    "#0587bf",
    "#7f7b77",
    "#e07808",
                     ]

df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='AAA')
unis = {}
for idx, row in df.iterrows():
    unis[row['University']] = row['Fullname']

@ohec.route('/api/v0.1/oper-budget')
def get_operating_budget():
    df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='operationBudget')
    data = []
    for i, yr in enumerate(YEARS):
        _d = {}
        _d['label'] = str(yr)
        _d['backgroundColor'] = []
        _d['data'] = []
        for v in df[yr]:
            _d['backgroundColor'].append(BACKGROUND_COLORS[i])
            if pd.isnull(v):
                _d['data'].append(0.0)
            else:
                _d['data'].append(v)
        data.append(_d)
    labels = [unis[u] for u in df['University']]
    return jsonify({'data': data, 'labels': labels})


@ohec.route('/api/v0.1/train-budget')
def get_training_budget():
    df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='trainingBudget')
    data = []
    for i, yr in enumerate(YEARS[:-1]):
        _d = {}
        _d['label'] = str(yr)
        _d['backgroundColor'] = []
        _d['data'] = []
        for v in df[yr]:
            _d['backgroundColor'].append(BACKGROUND_COLORS[i])
            if pd.isnull(v):
                _d['data'].append(0.0)
            else:
                _d['data'].append(v)
        data.append(_d)
    labels = [unis[u] for u in df['University']]
    return jsonify({'data': data, 'labels': labels})


@ohec.route('/api/v0.1/projects')
def get_projects():
    df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='projects')
    data = []
    for i, yr in enumerate(YEARS[:-1]):
        _d = {}
        _d['label'] = str(yr)
        _d['backgroundColor'] = []
        _d['data'] = []
        for v in df[yr]:
            _d['backgroundColor'].append(BACKGROUND_COLORS[i])
            if pd.isnull(v):
                _d['data'].append(0.0)
            else:
                _d['data'].append(v)
        data.append(_d)
    labels = [unis[u] for u in df['University']]
    return jsonify({'data': data, 'labels': labels})


@ohec.route('/api/v0.1/researchers')
def get_researchers():
    df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='researchers')
    data = []
    for i, yr in enumerate(YEARS[:-1]):
        _d = {}
        _d['label'] = str(yr)
        _d['backgroundColor'] = []
        _d['data'] = []
        for v in df[yr]:
            _d['backgroundColor'].append(BACKGROUND_COLORS[i])
            if pd.isnull(v):
                _d['data'].append(0.0)
            else:
                _d['data'].append(v)
        data.append(_d)
    labels = [unis[u] for u in df['University']]
    return jsonify({'data': data, 'labels': labels})


@ohec.route('/api/v0.1/students')
def get_students():
    df = pd.read_excel('static/data/TM_OHEC.xlsx', sheet_name='students')
    data = []
    for i, yr in enumerate(YEARS[:-1]):
        _d = {}
        _d['label'] = str(yr)
        _d['backgroundColor'] = []
        _d['data'] = []
        for v in df[yr]:
            _d['backgroundColor'].append(BACKGROUND_COLORS[i])
            if pd.isnull(v):
                _d['data'].append(0.0)
            else:
                _d['data'].append(v)
        data.append(_d)
    labels = [unis[u] for u in df['University']]
    return jsonify({'data': data, 'labels': labels})


@ohec.route('/')
def index():
    return render_template('ohec/index.html')
