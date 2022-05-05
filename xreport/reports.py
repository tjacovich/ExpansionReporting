import pandas as pd
import os
import glob
from xreport.utils import _get_facet_data
from datetime import datetime

class Report(object):
    """

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
        # The names of output files will have a date string in them
        self.dstring = datetime.today().strftime('%Y%m%d')
    # ============================= MAIN FUNCTIONALITY ================================ #
    def make_report(self, collection, report_type):
        """
        Given a list journal and a report type, generate the report data
    
        param: collection: collection of publications to create report for
        param: report_type: specification of report type
        """
        # Which journals (i.e. bibstems) make up the collection under consideration
        try:
            self.journals = self.config['JOURNALS'][collection]
        except Exception as err:
            msg = "Unable to find journals for collection: {} (Exception: {})".format(collection, err)
            self.logger.error(msg)
            raise
        # Initialize statistics data structure
        self.statsdata = {}
        for journal in self.journals:
            self.statsdata[journal] = {
                'pubdata':{},
                'startyear':0,
                'lastyear':0,
                'startvol':0,
                'lastvol':0,
                'general':{},
                'arxiv':{},
                'publisher':{},
                'crossref':{}
            }
        # Update statistics data structure with general publication information
        self._get_publication_data()

    def save_report(self, collection, report_type, subject):
        """
        Save the data created in the make_report method in Excel format
        
        param: collection: collection of publications to create report for
        param: report_type: specification of report type
        param: subject: specification of type data to create report for
        """
        # Where will the report(s) be written to
        outdir = "{0}/{1}".format(self.config['OUTPUT_DIRECTORY'], report_type)
        # Make sure the directory exists
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        # Transform the data generated in the make_report method:
        # generate a data structure so that we can create a Pandas frame
        header = []
        # Add header rows
        header.append(['jrnl ->'] + [j for j in self.journals])
        header.append(['start year ->'] + [str(self.statsdata[j]['startyear']) for j in self.journals])
        header.append(['last year ->'] + [str(self.statsdata[j]['lastyear']) for j in self.journals])
        header.append(['start vol ->'] + [str(self.statsdata[j]['startvol']) for j in self.journals])
        header.append(['last vol ->'] + [str(self.statsdata[j]['lastvol']) for j in self.journals])
        #
        maxvol = max([e['lastvol'] for e in self.statsdata.values()])
        if report_type == 'NASA':
            outputdata = header
            # Generate the name of the output file, including full path
            output_file = "{0}/{1}_{2}_{3}.xlsx".format(outdir, subject.lower(), collection, self.dstring)
            # Statistics are reported per volume for each journal in the collection
            for vol in range(1, maxvol+1):
                row = [str(vol)] + [self.statsdata[j]['general'].get(vol,"") for j in self.journals]
                outputdata.append(row)
            output_frame = pd.DataFrame(outputdata)
            # Results are written to an Excel file with conditional formatting and first row and column frozen
            output_frame.style.applymap(self._highlight_cells).to_excel(output_file, engine='openpyxl', index=False, header=False, freeze_panes=(1,1))
        else:
            outputdata = header
            # For internal reporting we generate two reports, corresponding with 
            # the sources associated with the type data in the report
            # For each of these sources the processing is the same as above
            for source in self.config['SOURCES'][subject]:
                outputdata = []
                output_file = "{0}/{1}_{2}_{3}_{4}.xlsx".format(outdir, subject.lower(), source, collection, self.dstring)
                for vol in range(1, maxvol+1):
                    row = [str(vol)] + [self.statsdata[j][source].get(vol,"") for j in self.journals]
                    outputdata.append(row)
                if outputdata:
                    output_frame = pd.DataFrame(outputdata)
                    output_frame.style.applymap(self._highlight_cells).to_excel(output_file, engine='openpyxl', index=False, header=False, freeze_panes=(1,1))
    #
    def _get_publication_data(self):
        """
        For a set of journals, get some basic publication data
        
        """
        for journal in self.journals:
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
    #
    def _highlight_cells(self, val):
        """
        Mapping function for use in Pandas to apply conditional cell coloring
        when writing data to Excel
        """
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

class FullTextReport(Report):
    """
    Main engine for gathering and processing data to create
    the full text coverage report 
    """
    def __init__(self):
        """
        Initializes the class and prepares a (temporary) lookup facility for
        curators reporting. This lookup facility will be replaced by an API
        query eventually
        """
        super(FullTextReport, self).__init__()
        # ============================= AUGMENTATION of parent method ================================ #
        fulltext_links = self.config.get("CLASSIC_FULLTEXT_INDEX")
        # Compile a list of journals to generate the lookup facility for
        include = [element for sublist in self.config.get("JOURNALS").values() for element in sublist]
        # This variable will hold the data to generate the Pandas frame
        data = []
        # Gather all required data. The Pandas data frame will allow the following query:
        # provide all full text sources for a given journal and volume combination, from which will
        # follow how many records have full text from arXiv and how many from the publisher (which
        # are the numbers we are after)
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
        # The lookup facility is a Pandas dataframe
        self.ft_index = pd.DataFrame(data, columns=['bibstem','volume','source'])

    def make_report(self, collection, report_type):
        """
        param: collection: collection of publications to create report for
        param: report_type: specification of report type
        """
        super(FullTextReport, self).make_report(collection, report_type)
        # ============================= AUGMENTATION of parent method ================================ #
        # Different report types result in different reports. Specifically, for full text,
        # for external reporting only the fact that there is full text is reported.
        if report_type == "NASA":
            self._get_fulltext_data_general()
        else:
            self._get_fulltext_data_classic('publisher')
            self._get_fulltext_data_classic('arxiv')
    #
    def save_report(self, collection, report_type, subject):
        """
        Save the data created in the make_report method in Excel format
    
        param: collection: collection of publications to create report for
        param: report_type: specification of report type
        param: subject: specification of type data to create report for
        """
        super(FullTextReport, self).save_report(collection, report_type, subject)

    def _get_fulltext_data_general(self):
        """
        For a set of journals, get full text data (the number of records with full text per volume)

        """
        for journal in self.journals:
            # The ADS query to retrieve all records with full text for a given journal
            query = 'bibstem:"{0}" fulltext_mtime:["1000-01-01t00:00:00.000Z" TO *]'.format(journal)
            # The query populates a dictionary keyed on volume number, listing the number of records per volume
            full_dict = _get_facet_data(self.config, query, 'volume')
            # Coverage data is stored in a dictionary
            cov_dict = {}
            for volume in sorted(self.statsdata[journal]['pubdata'].keys()):
                try:
                    frac = 100*float(full_dict[volume])/float(self.statsdata[journal]['pubdata'][volume])
                except:
                    frac = 0.0
                cov_dict[volume] = round(frac,1)
            # Update the global statistics data structure
            self.statsdata[journal]['general'] = cov_dict

    def _get_fulltext_data_classic(self, source):
        """
        For a set of journals, get full text data from Classic
        Note: this method will be replaced by API calls once Solr has been updated
        
        param: source: source of fulltext
        """
        for journal in self.journals:
            # Coverage data is stored in a dictionary
            cov_dict = {}
            for volume in sorted(self.statsdata[journal]['pubdata'].keys()):
                # For each volume of the journals in the collection we query the Pandas dataframe to retrieve the sources of full text
                if source == 'arxiv':
                    # How many records are there with full text from arXiv?
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

class ReferenceMatchingReport(Report):
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
        super(ReferenceMatchingReport, self).__init__()
        #
    def make_report(self, collection, report_type):
        super(ReferenceMatchingReport, self).make_report(collection, report_type)
        # ============================= AUGMENTATION of parent method ================================ #
        # Different report types result in different reports.
        if report_type == "NASA":
            self._get_reference_data('general')
        else:
            self._get_reference_data('publisher')
            self._get_reference_data('crossref')

    def save_report(self, collection, report_type, subject):
        """
        Save the data created in the make_report method in Excel format
    
        param: collection: collection to create report for
        param: report_type: specification of report type
        param: subject: specification of type data to create report for
        """
        super(ReferenceMatchingReport, self).save_report(collection, report_type, subject)

    def _get_reference_data(self, rtype):
        """
        For a set of journals, get reference matching statistics
        
        param: rtype: determines whether Crossref reference data should be included
        """
        for journal in self.journals:
            cov_dict = {}
            matched = unmatched = 0
            # For each volume of the journals in the collection we retrieve that reference matching level
            for volume in sorted(self.statsdata[journal]['pubdata'].keys()):
                ok, fail = self._process_one_volume(journal, volume, rtype)
                matched += ok
                unmatched += fail
                try:
                    frac = 100*float(matched)/float(unmatched+matched)
                except:
                    frac = 0.0
                cov_dict[volume] = round(frac,1)
            self.statsdata[journal][rtype] = cov_dict
    #
    def _process_one_volume(self, jrnl, volno, source):
        """
        For a particular volume of a given journal, find the results files generated
        by the reference resolver and tally how many references were successfully and
        not successfully matched to ADS records
        """
        # Root directory for reference data
        basedir = self.config['ADS_REFERENCE_DATA']
        # Transform journal bibstem to conform with reference data conventions
        jrnl = jrnl.replace('.','').replace('&','+')
        # Transform volume number to conform with reference data conventions
        vol = str(volno).zfill(4)
        # Some idiosyncracies for A&A reference data
        if jrnl == 'A+A' and int(vol) < 317:
            jrnl = 'A&A'
        if jrnl == 'A+AS' and int(vol) < 121:
            jrnl = 'A&AS'
        # Where are reference data located?
        voldir = "%s/%s/%s" % (basedir,jrnl,vol)
        # Special treatment for ApJL
        if jrnl == 'ApJL' and (int(vol) > 888 or int(vol) < 474):
           voldir = "%s/ApJ/%s" % (basedir, vol)
           resfiles = [f for f in glob.glob(voldir+'/*' + '.result') if os.path.basename(f)[13] == 'L']
        else:
           resfiles = glob.glob(voldir+'/*' + '.result')
        if source == 'publisher':
            resfiles = [f for f in resfiles if not f.endswith('.xref.xml.result')]
        elif source == 'crossref':
            resfiles = [f for f in resfiles if f.endswith('.xref.xml.result')]
        fail = ok =  0
        # Now go through all the resolver results files
        for resfile in resfiles:
            with open(resfile) as refdata:
                for line in refdata:
                        if not line.strip():
                            continue
                        if line.strip()[0] in ['0','5']:
                            fail += 1
                        elif line.strip()[0] == '1':
                            ok += 1
                        else:
                            continue
        return [ok, fail]