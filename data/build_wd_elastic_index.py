import requests

from elasticsearch import Elasticsearch, client
from elasticsearch.exceptions import RequestError
es = Elasticsearch()


# retrieve all QIDs from the populated reframe ES index

qid_list = []
only_add_missing = True

def process_batch(batch):
    for count, hit in enumerate(batch['hits']['hits']):
        qid = hit['_source']['qid']
        if qid:
            qid_list.append(qid)


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
    "sort": [
        "_doc"
    ],
    'size': 9999
}

es.indices.refresh(index="reframe")

r = es.search(index="reframe", body=body, scroll='1m')
scroll_id = r['_scroll_id']
process_batch(r)

while True:
    r = es.scroll(scroll='1m', scroll_id=scroll_id)
    print(r)
    if len(r['hits']['hits']) == 0:
        break
    process_batch(r)


print(len(qid_list))

bd = {
    'mapping': {
        'total_fields': {
            'limit': 30000
        }
    }
}

c = client.IndicesClient(es)
# check if index exists, otherwise, create
if not only_add_missing:
    if c.exists(index='wikidata'):
        c.delete(index='wikidata')

    #     c.put_settings(index='wikidata', body=bd)
    # else:
    c.create(index='wikidata', body=bd)

session = requests.Session()

for count, qid in enumerate(qid_list):

    if only_add_missing:
        if es.exists(index='wikidata', doc_type='compound', id=qid):
            continue

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

    if es.exists(index='wikidata', doc_type='compound', id=qid, request_timeout=30):
        # print('this exists!!')
        es.update(index='wikidata', id=qid, doc_type='compound', body={'doc': obj}, request_timeout=30)
        # pass
    else:
        try:
            res = es.index(index="wikidata", doc_type='compound', id=qid, body=obj, request_timeout=30)

        except RequestError as e:
            print(e)

    if count % 100 == 0:
        print('imported ', count)

