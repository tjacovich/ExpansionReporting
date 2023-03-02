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
    parser.add_argument('-c', '--collection', default='CORE', dest='collection',
                        help='Collection to create report for (accepted values: AST or PS+HP)')
    parser.add_argument('-f', '--format', default='NASA', dest='format',
                        help='Format of report')
    parser.add_argument('-s', '--subject', default='ALL', dest='subject',
                        help='Subject of the report')
    args = parser.parse_args()

    if args.collection not in config.get('COLLECTIONS'):
        sys.exit('Please specify one of the following values for the collection parameter: {}'.format(config.get('COLLECTIONS')))
    if args.format not in config.get('FORMATS'):
        sys.exit('Please specify one of the following values for the format parameter: {}'.format(config.get('FORMATS')))
    if args.subject not in config.get('SUBJECTS'):
        sys.exit('Please specify one of the following values for the subject parameter: {}'.format(config.get('SUBJECTS')))
    try:
        report = tasks.create_report(collection=args.collection, format=args.format, subject=args.subject)
    except Exception as error:
        logger.error('Creating "{0}" report for "{1}" on collection "{2}" failed: {3}'.format(args.subject, args.format, args.collection, error))
        sys.exit('Creating "{0}" report for "{1}" on collection "{2}" failed: {3}'.format(args.subject, args.format, args.collection, error))