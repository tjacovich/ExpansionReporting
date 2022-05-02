

class ReferenceMatchingReport():
    """
    Main engine for gathering and processing data to create
    the reference matching report. This report depends fully
	on data in the ADS back office, because it currently is not
	available anywhere else. At some point we may have a database
	containing all the raw reference data; then the time has come
	to revisit this reporting module.
    """
    def __init__(self):
        """
        Initializes the class
        """
        # ============================= INITIALIZATION ==================================== #
        from adsputils import setup_logging, load_config
        proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
        self.config = load_config(proj_home=proj_home)
        self.logger = setup_logging(__name__, proj_home=proj_home,
                                level=self.config.get('LOGGING_LEVEL', 'INFO'),
                                attach_stdout=self.config.get('LOG_STDOUT', False))
        # ============================= MAIN FUNCTIONALITY ================================ #



    def make_report(self, collection, report_type):
        """
        Given a list journal and a report type, generate the report data
        
        param: collection: collection to create report for
        param: report_type: specification of report type
        """
        # Which journals (i.e. bibstems) make up the collection under consideration
        try:
            journals = self.config['JOURNALS'][collection]
        except Exception as err:
            msg = "Unable to find journals for collection: {} (Exception: {})".format(collection, err)
            self.logger.error(msg)
            raise



    def save_report(self, collection, report_type):
        """
        Save the data created in the make_report method in Excel format
        
        param: collection: collection to create report for
        param: report_type: specification of report type
        """
        # Where will the report(s) be written to
        outdir = "{0}/{1}".format(self.config['OUTPUT_DIRECTORY'], report_type)
        # Make sure the directory exists
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        # The names of output files will have a date string in them
        dstring = datetime.today().strftime('%Y%m%d')

