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
    # What is the report format
    report_format = args['format']
    # For which collection are we generating the report
    collection = args['collection']
    # Initialize the class for full text reporting
    ftreport = FullTextReport()
    # The first step consists of retrieving and preparing the data to generate the report
    try:
        ftreport.make_report(collection, report_format)
    except Exception as err:
        msg = "Error making full text report for collection '{0}' in format '{1}': {2}".format(collection, report_format, err)
        print(msg)
        logger.error(msg)
    # Write the report to file
    try:
        ftreport.save_report(collection, report_format)
    except Exception as err:
        msg = "Error saving full text report for collection '{0}' in format '{1}': {2}".format(collection, report_format, err)
        print(msg)
        logger.error(msg)
    
        
        
        