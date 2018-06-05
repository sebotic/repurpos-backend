import requests

from elasticsearch import Elasticsearch, client
from elasticsearch.exceptions import RequestError
es = Elasticsearch()


# retrieve all QIDs from the populated reframe ES index
body = {
    "_source": {
        "includes": ["qid"],
    },
    "query": {
        "query_string": {

            "query": "Q*",
            "fields": ['qid']
        }
    },
    "from": 0, "size": 10000,
}

es.indices.refresh(index="reframe")

r = es.search(index="reframe", body=body)

bd = {
    'mapping': {
        'total_fields': {
            'limit': 30000
        }
    }
}

c = client.IndicesClient(es)
# check if index exists, otherwise, create
if c.exists(index='wikidata'):

    c.put_settings(index='wikidata', body=bd)
else:
    c.create(index='wikidata', body=bd)

session = requests.Session()

for count, hit in enumerate(r['hits']['hits']):
    qid = hit['_source']['qid']

    header = {
        'Accept': 'application/json'
    }

    r = session.get('http://www.wikidata.org/entity/{}'.format(qid), headers=header).json()
    # print(r)

    obj = r['entities'][qid]
    del obj['descriptions']

    for claim, value in obj['claims'].items():
        # print(claim, value)
        for x in value:
            if 'references' in x:
                del x['references']

    if es.exists(index='wikidata', doc_type='compound', id=qid):
        # print('this exists!!')
        es.update(index='wikidata', id=qid, doc_type='compound', body={'doc': obj})
        # pass
    else:
        try:
            res = es.index(index="wikidata", doc_type='compound', id=qid, body=obj)

        except RequestError as e:
            print(e)

    if count % 100 == 0:
        print('imported ', count)

