import pandas as pd
import os
from xreport.utils import _get_facet_data
from datetime import datetime

class FullTextReport():
    """
    Main engine for gathering and processing data to create
    the full text coverage report 
    """
    def __init__(self):
        """
        Initializes the class and prepares a (temporary) lookup facility for
        curators reporting
        """
        # ============================= INITIALIZATION ==================================== #
        from adsputils import setup_logging, load_config
        proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
        self.config = load_config(proj_home=proj_home)
        self.logger = setup_logging(__name__, proj_home=proj_home,
                                level=self.config.get('LOGGING_LEVEL', 'INFO'),
                                attach_stdout=self.config.get('LOG_STDOUT', False))
        # ============================= MAIN FUNCTIONALITY ================================ #
        fulltext_links = self.config.get("CLASSIC_FULLTEXT_INDEX")
        include = [element for sublist in self.config.get("JOURNALS").values() for element in sublist]
        data = []
        with open(fulltext_links) as fh:
            for line in fh:
                bibcode, ftfile, source = line.strip().split('\t')
                bibstem = bibcode[4:9]
                if bibstem not in include:
                    continue
                try:
                    volume  = int(bibcode[9:13].replace('.',''))
                except:
                    self.logger.info("Processing Classic fulltext index. Cannot get volume for: {0}. Skipping...".format(bibcode))
                    continue
                letter  = bibcode[13]
                if bibstem == 'ApJ..' and letter == 'L':
                    bibstem = 'ApJL'
                data.append([bibstem, volume, source.lower()])

        self.ft_index = pd.DataFrame(data, columns=['bibstem','volume','source'])

    def make_report(self, collection, report_type):
        """
        Given a list journal and a report type, generate the report data
        
        param: collection: collection to create report for
        param: report_type: specification of report type
        """
        try:
            journals = self.config['JOURNALS'][collection]
        except Exception as err:
            msg = "Unable to find journals for collection: {} (Exception: {})".format(collection, err)
            self.logger.error(msg)
            raise
        # Initialize statistics data structure
        self.statsdata = {}
        for journal in journals:
            self.statsdata[journal] = {
                'pubdata':{},
                'startyear':0,
                'lastyear':0,
                'startvol':0,
                'lastvol':0,
                'general':{},
                'arxiv':{},
                'publisher':{}
            }
        # Update statistics data structure with general publication information
        self._get_publication_data(journals)
        if report_type == "NASA":
            self._get_fulltext_data_general(journals)
        else:
            self._get_fulltext_data_classic(journals, 'publisher')
            self._get_fulltext_data_classic(journals, 'arxiv')

    def save_report(self, collection, report_type):
        """
        Save the data created in the make_report method in TSV format
        
        param: collection: collection to create report for
        param: report_type: specification of report type
        """
        # Where will the report(s) be written to
        outdir = "{0}/{1}".format(self.config['OUTPUT_DIRECTORY'], report_type)
        # Make sure the directory exists
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        dstring = datetime.today().strftime('%Y%m%d')
        output_file = "{0}/fulltext_{1}_{2}.xlsx".format(outdir, collection, dstring)
        # Transform the data generated in the make_report method:
        # generate a data structure than can be saved easily into a TSV file
        outputdata = []
        journals = sorted(self.statsdata.keys())
        # Add header rows
        outputdata.append(['jrnl ->'] + [j for j in journals])
        outputdata.append(['start year ->'] + [self.statsdata[j]['startyear'] for j in journals])
        outputdata.append(['last year ->'] + [self.statsdata[j]['lastyear'] for j in journals])
        outputdata.append(['start vol ->'] + [self.statsdata[j]['startvol'] for j in journals])
        outputdata.append(['last vol ->'] + [self.statsdata[j]['lastvol'] for j in journals])
        # 
        maxvol = max([e['lastvol'] for e in self.statsdata.values()])
        if report_type == 'NASA':
            for vol in range(1, maxvol+1):
                row = [str(vol)] + [self.statsdata[j]['general'].get(vol,"") for j in journals]
                outputdata.append(row)

        output_frame = pd.DataFrame(outputdata)
        output_frame.style.applymap(self._highlight_cells).to_excel(output_file, engine='openpyxl', index=False, header=False)
        

    def _get_publication_data(self, journals):
        """
        For a set of journals, get some basic publication data
        
        :param journals: list of full bibstems
        """
        for journal in journals:
            # First get the number of records per volume
            query = 'bibstem:"{0}"'.format(journal)
            # Get the data using a facet query
            art_dict = _get_facet_data(self.config, query, 'volume')
            # Also, get the number of records per year
            year_dict = _get_facet_data(self.config, query, 'year')
            # Update journal statistics
            # The first and most recent publication years
            self.statsdata[journal]['lastyear'] = max(year_dict.keys())
            self.statsdata[journal]['startyear'] = min(year_dict.keys())
            # The first and most recent volumes
            self.statsdata[journal]['lastvol'] = max(art_dict.keys())
            self.statsdata[journal]['startvol'] = min(art_dict.keys())
            # The number of publications per volume, to be used later
            # for normalization
            self.statsdata[journal]['pubdata'] = art_dict

    def _get_fulltext_data_general(self, journals):
        """
        For a set of journals, get full text data
        
        :param journals: list of full bibstems
        """
        for journal in journals:
            query = 'bibstem:"{0}" fulltext_mtime:["1000-01-01t00:00:00.000Z" TO *]'.format(journal)
            full_dict = _get_facet_data(self.config, query, 'volume')
            cov_dict = {}
            for volume in sorted(self.statsdata[journal]['pubdata'].keys()):
                try:
                    frac = 100*float(full_dict[volume])/float(self.statsdata[journal]['pubdata'][volume])
                except:
                    frac = 0.0
                cov_dict[volume] = round(frac,1)
            self.statsdata[journal]['general'] = cov_dict

    def _get_fulltext_data_classic(self, journals, source):
        """
        For a set of journals, get full text data from Classic
        Note: this method will be replaced by API calls once Solr has been updated
        
        :param journals: list of full bibstems
        """
        full_dict = {}
        for journal in journals:
            cov_dict = {}
            for volume in sorted(self.statsdata[journal]['pubdata'].keys()):
                if source == 'arxiv':
                    data = self.ft_index.query("bibstem=='{0}' and volume=={1} and source=='arxiv'".format(journal, volume))
                else:
                    data = self.ft_index.query("bibstem=='{0}' and volume=={1} and source!='arxiv'".format(journal, volume))
                try:
                    sources = data['source'].tolist()
                except Exception as err:
                    self.logger.error('Source lookup in Classic index blew up for journal {0}, volume {1}: {2}'.format(journal, volume, err))
                    sources = []
                try:
                    frac = 100*float(len(sources))/float(self.statsdata[journal]['pubdata'][volume])
                except:
                    frac = 0.0
                cov_dict[volume] = round(frac,1)
            self.statsdata[journal][source] = cov_dict

    def _highlight_cells(self, val):
        try:
            if val >= 90:
                color = '#6aa84f'
            elif val <= 60:
                color = '#f4cccc'
            elif val > 60 and val <=70:
                color = '#ffe599'
            else:
                color = '#cfe2f3'
        except:
            color = '#ffffff'
        return 'background-color: {}'.format(color)
