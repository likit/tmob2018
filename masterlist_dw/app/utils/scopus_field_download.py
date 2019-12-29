import os
import requests


URL = 'https://api.elsevier.com/content/subject/scopus'
SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY')


def download_scopus_fields(db, model):
    res = requests.get(URL, params={
        'apiKey': SCOPUS_API_KEY,
        'httpAccept': 'application/json',
        'view': 'ENHANCED'
    })
    if res.status_code == 200:
        data = res.json()
        if data.get('subject-classifications'):
            for subj in data['subject-classifications'].get('subject-classification'):
                _field = model(code=int(subj['code']),
                               abbrev=subj['abbrev'],
                               description=subj['description'],
                               detail=subj['detail']
                               )
                db.session.add(_field)
            db.session.commit()
