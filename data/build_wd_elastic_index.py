import requests
import pprint
import wikidataintegrator as wdi
from elasticsearch import Elasticsearch, client
from elasticsearch.exceptions import RequestError
es = Elasticsearch()


# retrieve all QIDs from the populated reframe ES index

qid_list = []
only_add_missing = True
qid_label_map = {}


def process_batch(batch):
    for count, hit in enumerate(batch['hits']['hits']):
        qid = hit['_source']['qid']
        if qid:
            qid_list.append(qid)


def lookup_wd_item_label(qid):
    if qid in qid_label_map:
        return qid_label_map[qid]
    else:
        query = '''
           SELECT ?compound ?label WHERE {{
              VALUES ?compound  {{ wd:{} }}
              ?compound rdfs:label ?label FILTER (LANG(?label) = "en") .
            }}
            '''.format(qid)

        results = wdi.wdi_core.WDItemEngine.execute_sparql_query(query)
        for x in results['results']['bindings']:
            qid_label_map.update({x['compound']['value']: x['label']['value']})
            return x['label']['value']

        return qid


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

# bd = {
#     'mapping': {
#         'total_fields': {
#             'limit': 30000
#         }
#     }
# }

c = client.IndicesClient(es)
# check if index exists, otherwise, create
if not only_add_missing:
    if c.exists(index='wikidata'):
        c.delete(index='wikidata')

    #     c.put_settings(index='wikidata', body=bd)
    # else:
    c.create(index='wikidata')

session = requests.Session()

for count, qid in enumerate(qid_list):
    # print(qid)
    if only_add_missing:
        if es.exists(index='wikidata', doc_type='compound', id=qid):
            continue

    condensed_wditem = {}
    wditem = wdi.wdi_core.WDItemEngine(wd_item_id=qid)

    condensed_wditem['label'] = wditem.get_label('en') if wditem.get_label('en') else wditem.get_label('de')
    condensed_wditem['aliases'] = wditem.get_aliases('en')

    exclude_props = ['P575', 'P117', 'P61', 'P1343', 'P373', 'P527', 'P508', 'P646', 'P227', 'P349', 'P1296', 'P3471',
                     'P2669']
    for x in wditem.original_statements:
        prop_nr = x.get_prop_nr()
        if prop_nr in exclude_props:
            continue
        value = x.get_value()
        if type(x) == wdi.wdi_core.WDItemID and value:
            value = lookup_wd_item_label('Q' + str(value))

        if prop_nr in condensed_wditem and value:
            condensed_wditem[prop_nr].append(value)
        elif value:
            condensed_wditem[prop_nr] = [value]

        else:
            continue

    if es.exists(index='wikidata', doc_type='compound', id=qid, request_timeout=30):
        # print('this exists!!')
        es.update(index='wikidata', id=qid, doc_type='compound', body={'doc': condensed_wditem}, request_timeout=30)
        # pass
    else:
        try:
            res = es.index(index="wikidata", doc_type='compound', id=qid, body=condensed_wditem, request_timeout=30)

        except RequestError as e:
            print(e)

    if count % 100 == 0:
        print('imported ', count)
