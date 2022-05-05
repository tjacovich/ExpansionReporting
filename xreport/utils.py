import re
import os
import urllib.request, urllib.parse, urllib.error
import requests
#import xreport.app as app_module
# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
config = load_config(proj_home=proj_home)
#app = app_module.xreport('ads-expansion-reporting', proj_home=proj_home, local_config=globals().get('local_config', {}))
logger = setup_logging(__name__, proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))
# =============================== FUNCTIONS ======================================= #
def _group(lst, n):
    for i in range(0, len(lst), n):
        val = lst[i:i+n]
        if len(val) == n:
            yield tuple(val)

def _make_dict(tup, key_is_int=True):
    newtup = tup
    if key_is_int:
        newtup = [(int(re.sub("[^0-9]", "", e[0])), e[1]) for e in tup]        
    return dict(newtup)

def _do_query(conf, params):
    headers = {}
    headers["Authorization"] = "Bearer:{}".format(conf['ADS_API_TOKEN'])
    headers["Accept"] = "application/json"
    url = "{}/search/query?{}".format(conf['ADS_API_URL'], urllib.parse.urlencode(params))
    r_json = {}
    try:
        r = requests.get(url, headers=headers)
    except Exception as err:
        logger.error("Search API request failed: {}".format(err))
        raise
    if not r.ok:
        msg = "Search API request with error code '{}'".format(r.status_code)
        logger.error(msg)
        raise Exception(msg)
    else:
        try:
            r_json = r.json()
        except ValueError:
            msg = "No JSON object could be decoded from Search API"
            logger.error(msg)
            raise Exception(msg)
        else:
            return r_json
    return r_json

def _get_facet_data(conf, query_string, facet):

    params = {
        'q':query_string,
        'fl': 'id',
        'rows': 1,
        'facet':'on',
        'facet.field': facet,
        'facet.limit': 1000,
        'facet.mincount': 1,
        'facet.offset':0,
        'sort':'date desc'
    }

    data = _do_query(conf, params)
    results = data['facet_counts']['facet_fields'].get(facet)
    return _make_dict(list(_group(results, 2)))

def _get_records(app, query_string, return_fields):
    start = 0
    rows = 10
    results = []
    params = {
        'q':query_string,
        'fl': return_fields,
        'rows': rows,
        'start': start
    }
    data = _do_query(app, params)
    try:
        results = data['response']['docs']
    except:
        raise Exception('Solr returned unexpected data!')
    num_documents = int(data['response']['numFound'])
    num_paginates = int(math.ceil((num_documents) / (1.0*rows))) - 1
    start += rows
    for i in range(num_paginates):
        params['start'] = start
        data = do_query(app, params)
        try:
            results += data['response']['docs']
        except:
            raise Exception('Solr returned unexpected data!')
        start += rows
    return bibcodes