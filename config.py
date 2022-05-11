# ============================= LOGGING ======================================== #
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = False
# ============================= ADS ============================================ #
ADS_API_TOKEN = "<secret>"
ADS_API_URL = "https://ui.adsabs.harvard.edu/v1"
CLASSIC_FULLTEXT_INDEX = "/tmp/all.links"
CLASSIC_USAGE_INDEX = {
    'reads':'/tmp/reads.links',
    'downloads':'/tmp/downloads.links'
}
ADS_REFERENCE_DATA = "/references/resolved"
# ============================= APPLICATION ==================================== #
# 
# Collections we are reporting on
COLLECTIONS = ['AST', 'HP', 'PS', 'HP_AST', 'PS_AST']
# Report formats supported
FORMATS = ['NASA', 'CURATORS', 'SUMMARY']
# Report types supported
SUBJECTS = ['FULLTEXT', 'REFERENCES', 'SUMMARY']
# Which journals are we reporting on per collection
JOURNALS = {
    'AST': ["ApJ..","ApJL","ApJS.","AJ...","MNRAS","A&A..","A&AS.","PASP.","AN...","PhRvD","JCAP.","APh..","CQGra"],
    'PS': ["AREPS","ASTRA","AdSpR","AnGeo","Ap&SS","AsBio","CeMDA","E&PSL","EM&P.","GeCoA","IJAsB","Icar.","JAtS.","JGRA.","JGRD.",
              "JGRE.","M&PS.","M&PSA","Metic","NatGe","P&SS.","PEPI.","RvGeo","SSRv.","SoSyR","SoPh.","SpWea","PSJ..","Moon.","SpPol"],
    'HP': ['SoPh.','SpWea'],
    'HP_AST': ["ApJ..","ApJL","ApJS.","AJ...","MNRAS","A&A..","A&AS."],
    'PS_AST': ["ApJ..","ApJL","ApJS.","AJ...","MNRAS","A&A..","A&AS."]
}
# For some collection we define filters (to e.g. get the right content from multidisciplinary journals)
COLLECTION_FILTERS = {
    'HP_AST':'keyword:"sun*"',
    'PS_AST':'keyword:("planets*" OR meteor OR asteroid OR "celestial*" OR "solar system") -exoplanet -interstellar'
}
# Filtering to help us get recent content (i.e. entered in the past year)
CONTENT_QUERIES = {
    'HP':'{0} entdate:[NOW-365DAYS TO *]',
    'HP_AST':'{0} entdate:[NOW-365DAYS TO *]',
    'PS':'{0} entdate:[NOW-365DAYS TO *]',
    'PS_AST':'{0} entdate:[NOW-365DAYS TO *]',
    'AST':'{0} entdate:[NOW-365DAYS TO *]'
}
# For specific types of metadata, specify the sources we are considering
SOURCES = {
    'FULLTEXT': ['publisher','arxiv'],
    'REFERENCES': ['publisher', 'crossref']
}
# For these collections we need to skip the calculation of usage
# (because it would involve retrieving all bibcodes)
SKIP_USAGE = ['HP_AST', 'PS_AST']
# For these publications (bibstem) the volume is treated as volume. This dictionary lists the start year
YEAR_IS_VOL = {
    'JCAP.':2003
}
# The root of the output location
OUTPUT_DIRECTORY = '/tmp/reports'

