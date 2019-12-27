import requests

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
                            if (givenname.lower() == firstname.lower()) and\
                                    (surname.lower() == lastname.lower()):
                                yield entry.get('prism:url')


def fetch_author_detail(url):
    if data and 'author-retrieval-response' in data:
        if isinstance(data['author-retrieval-response'], list):
            authdata = data['author-retrieval-response'][0]
        else:
            print('Author data not available.')
            raise ValueError('Author has no data.')
    else:
        return data


if __name__ == '__main__':
    print(list(fetch_author_initial('', 'Prachayasittikul')))
