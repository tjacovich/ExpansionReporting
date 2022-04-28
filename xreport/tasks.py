from __future__ import absolute_import, unicode_literals
import os
import sys
from builtins import str
import csv
from datetime import datetime
import xreport.app as app_module
#from xreport.utils import _get_record_stats
#from xreport.utils import _get_fulltext_stats
#from xreport.utils import _get_references_stats
from xreport.fulltext import FullTextReport
# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
config = load_config(proj_home=proj_home)
app = app_module.xreport('ads-expansion-reporting', proj_home=proj_home, local_config=globals().get('local_config', {}))
logger = app.logger
# ============================= FUNCTIONS ========================================= #
def create_report(**args):
#    # Initializations
#    full_text_stats = {}
#    full_text_stats['general'] =
#    full_text_stats['arxiv'] =
#    full_text_stats['publisher'] =
#    # What is the report format
#    report_format = args['format']
#    # For which collection are we generating the report
#    collection = args['collection']
#    # Which journals does this collection consist of?
#    try:
#        journals = config['JOURNALS'][collection]
#    except Exception as err:
#        msg = "Unable to find journals for collection: {} (Exception: {})".format(collection, err)
#        logger.error(msg)
#        raise
#    # Collect all necessary data for these journals
#    journals = ['PSJ..']
#    # General record coverage
##    record_stats = _get_record_stats(report_format, journals)
#    # Full text coverage
#    if report_format == "NASA":
#        full_text_stats['general'] = _get_fulltext_stats(app, 'general', journals, 'volume')
#    elif report_format == "CURATORS":
#        full_text_stats['arxiv'] = _get_fulltext_stats(app, 'arxiv', journals, 'volume')
#        full_text_stats['publisher'] = _get_fulltext_stats(app, 'publisher', journals, 'volume')
#        
#    # Reference coverage
##    references_stats = _get_references_stats(report_format, journals)
    # What is the report format
    report_format = args['format']
    # For which collection are we generating the report
    collection = args['collection']
    #
    ftreport = FullTextReport()
    try:
        ftreport.make_report(collection, report_format)
    except Exception as err:
        msg = "Error making full text report for collection '{0}' in format '{1}': {2}".format(collection, report_format, err)
        print(msg)
        logger.error(msg)
    try:
        ftreport.save_report(collection, report_format)
    except Exception as err:
        msg = "Error saving full text report for collection '{0}' in format '{1}': {2}".format(collection, report_format, err)
        print(msg)
        logger.error(msg)
    
        
        
        
