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
    bibcodes = []
    params = {
        'q':query_string,
        'fl': return_fields,
        'rows': rows,
        'start': start
    }
    data = _do_query(app, params)
    try:
        bibcodes = data['response']['docs']
    except:
        raise Exception('Solr returned unexpected data!')
    num_documents = int(data['response']['numFound'])
    num_paginates = int(math.ceil((num_documents) / (1.0*rows))) - 1
    start += rows
    for i in range(num_paginates):
        params['start'] = start
        data = do_query(app, params)
        try:
            bibcodes += data['response']['docs']
        except:
            raise Exception('Solr returned unexpected data!')
        start += rows
    return bibcodes

def get_ft_files(biblist):
    ftmap = {}
    for b in biblist:
        ftmap[b] = ''
        try:
            for entry in ftlooker(b).strip().split('\n'):
                ftmap[b] = entry.split('\t')[2].lower()
        except:
            pass
    return ftmap

def _get_fulltext_numbers(app, journal, volumes, source):
    
    for volume in volumes:
        # First, get the bibcodes for the journal being processed
        query = 'bibstem:"{0}" volume:{1} -title:erratum doctype:article'.format(journal, volume)
        data = _get_records(app, query, 'bibcode')
        try:
            bibcodes = [r['bibcode'] for r in res]
        except:
            bibcodes = []
        try:
            ft_data = _get_ft_files(bibcodes)
        except:
            ft_data = {}

def _get_fulltext_stats(app, source, journals):
    stats = {}
    for journal in journals:
        # First get the number of records per volume
        query = 'bibstem:"{0}" doctype:article'.format(journal)
        # Get the data using a facet query
        art_dict = _get_facet_data(app, query, 'volume')
        # Also, get the number of records per year
        year_dict = _get_facet_data(app, query, 'year')
        # The most recent publication year for the journal being processed
        maxyear = max(year_dict.keys())
        # The first and last volume for journal being processed
        maxvol = max(art_dict.keys())
        minvol = min(art_dict.keys())
        if source == 'general':
            # Get the number of records with full text per volume from ADS API
            query = 'bibstem:"{0}" doctype:article fulltext_mtime:["1000-01-01t00:00:00.000Z" TO *]'.format(j)
            full_dict = _get_facet_data(app, query, 'volume')
            # All necessary data has now been collected to generate the report
            coverage = [""]*(maxvol + 1)
            for vol in sorted(art_dict.keys()):
                try:
                    frac = 100*float(full_dict[vol])/float(art_dict[vol])
                except:
                    frac = 0.0
                coverage[vol] = str(round(frac,1))
            stats[journal] = {
                'maxyear': maxyear,
                'maxvol': maxvol,
                'minvol': minvol,
                'general': coverage
            }
        elif source == 'arxiv':
            # Get the number of records with full text per volume from ADS back office
            full_dict = _get_fulltext_numbers(app, journal, sorted(art_dict.keys()), source)
            

def _save_results(datadir, results, topic):
    ofile = "{0}/{1}_{2}.tsv".format(datadir, topic, dstring)
    with open(ofile, 'w') as f_output:
        for entry in results:
            try:
                f_output.write('\t'.join(entry) + '\n')
            except:
                sys.exit('Error writing to {0}: {1}\n'.format(ofile, entry))