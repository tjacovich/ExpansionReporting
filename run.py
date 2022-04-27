from __future__ import print_function
import argparse
import datetime
import sys
import os

from xreport import tasks

# ============================= INITIALIZATION ==================================== #

from adsputils import setup_logging, load_config
proj_home = os.path.realpath(os.path.dirname(__file__))
config = load_config(proj_home=proj_home)
logger = setup_logging('run.py', proj_home=proj_home,
                        level=config.get('LOGGING_LEVEL', 'INFO'),
                        attach_stdout=config.get('LOG_STDOUT', False))
                        

# =============================== FUNCTIONS ======================================= #


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--collection', default='PS+HP', dest='collection',
                        help='Collection to create report for (accepted values: AST or PS+HP)')
    parser.add_argument('-f', '--format', default='CURATORS', dest='format',
                        help='Format of report (accepted)')
    args = parser.parse_args()
    
    if args.collection not in config.get('COLLECTIONS'):
        sys.exit('Please specify one of the following values for the collection parameter: {}'.format(config.get('COLLECTIONS')))
    if args.format not in config.get('FORMATS'):
        sys.exit('Please specify one of the following values for the format parameter: {}'.format(config.get('FORMATS')))
    try:
        report = tasks.create_report(collection=args.collection, format=args.format)
    except Exception as error:
#        logger.error('Creating "{0}" report on collection "{1}" failed: {2}'.format(args.target, args.collection, error))
        sys.exit('Creating "{0}" report on collection "{1}" failed: {2}'.format(args.format, args.collection, error))