import requests
from datetime import datetime
from app.wsgi import db
from app.models import (DimScopusFieldGroup, DimScopusAuthorDetail, BridgeScopusFieldGroup, DimScopusField)
AUTHOR_SEARCH_URL = 'https://api.elsevier.com/content/search/author'
SCOPUS_API_KEY = '871232b0f825c9b5f38f8833dc0d8691'


def fetch_author_initial(firstname, lastname, affil='Thailand'):
    if not lastname or not firstname:
        raise ValueError('Firstname and lastname must be specified.')
    else:
        query = 'AUTHFIRST ({}) AUTHLASTNAME ({}) AFFIL ({})'.format(firstname[0], lastname, affil)

    res = requests.get(AUTHOR_SEARCH_URL, params={
        'apiKey': SCOPUS_API_KEY,
        'httpAccept': 'application/json',
        'view': 'STANDARD',
        'query': query,
    })
    try:
        data = res.json()
    except:
        raise ValueError('Error occurred while retrieving data for {}'.format(lastname))
    else:
        if data.get('search-results'):
            if int(data['search-results'].get('opensearch:totalResults', '0')) > 0:
                if 'entry' in data['search-results']:
                    for entry in data['search-results']['entry']:
                        if 'preferred-name' in entry:
                            givenname = entry['preferred-name'].get('given-name', '')
                            surname = entry['preferred-name'].get('surname', '')
                            if (givenname.lower() == firstname.lower()) and \
                                    (surname.lower() == lastname.lower()):
                                return entry.get('prism:url')


def extract_author_detail(authdata):
    auth_dict = {}
    auth_dict['coauthor_count'] = int(authdata.get('coauthor-count', 0))
    auth_dict['h_index'] = int(authdata.get('h-index', 0))
    auth_dict['citation_count'] = int(authdata.get('coredata', {}).get('citation-count', 0))
    auth_dict['cited_by_count'] = int(authdata.get('coredata', {}).get('cited-by-count', 0))
    auth_dict['document_count'] = int(authdata.get('coredata', {}).get('document-count', 0))
    auth_dict['url'] = authdata.get('coredata', {}).get('prism:url')
    auth_dict['pub_start'] = int(authdata.get('author-profile', {})
                                 .get('publication-range', {}).get('@start', '0'))
    auth_dict['pub_end'] = int(authdata.get('author-profile', {})
                               .get('publication-range', {}).get('@end', '0'))
    auth_dict['department'] = authdata.get('author-profile', {}).get('affiliation-current', {}) \
        .get('affiliation', {}).get('ip-doc', {}).get('preferred-name', {}).get('$')
    auth_dict['affiliation'] = authdata.get('author-profile', {}).get('affiliation-current', {}) \
        .get('affiliation', {}).get('ip-doc', {}).get('parent-preferred-name', {}).get('$')
    return auth_dict


def fetch_author_detail(url):
    """Fetch author from SCOPUS using the URL.
    Returned data are saved to the given database.
    """
    res = requests.get(
        url,
        params={
            'apiKey': SCOPUS_API_KEY,
            'view': 'ENHANCED',
            'httpAccept': 'application/json',
        }
    )
    data = res.json()
    if data.get('author-retrieval-response'):
        if isinstance(data['author-retrieval-response'], list):
            authdata = data['author-retrieval-response'][0]
            identifier = authdata.get('coredata', {}). \
                get('dc:identifier', '').replace('AUTHOR_ID:', '')
            existing_author_detail = DimScopusAuthorDetail.query.filter_by(identifier=identifier).first()
            if existing_author_detail:
                existing_author_detail.current = False
                existing_author_detail.end_date = datetime.today()
                db.session.add(existing_author_detail)
            auth_dict = extract_author_detail(authdata)
            new_author_detail = DimScopusAuthorDetail(**auth_dict)
            new_author_detail.identifier = identifier
            new_author_detail.start_date = datetime.today()
            new_author_detail.current = True
            scopus_field_group = DimScopusFieldGroup()
            new_author_detail.scopus_field_group = scopus_field_group
            db.session.add(new_author_detail)
            db.session.commit()
            for cls in authdata.get('author-profile', {}).get('classificationgroup', {}) \
                .get('classifications', {}).get('classification', []):
                code = cls.get('$')
                frequency = int(cls.get('@frequency', '0'))
                if code:
                    field = DimScopusField.query.filter_by(code=int(code)).first()
                    b = BridgeScopusFieldGroup(
                        scopus_field_group_id=scopus_field_group.id,
                        scopus_field_id=field.id,
                        frequency=frequency
                    )
                    db.session.add(b)
            db.session.commit()


if __name__ == '__main__':
    print(list(fetch_author_detail('https://api.elsevier.com/content/author/author_id/54894391300')))
