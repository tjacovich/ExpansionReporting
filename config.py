# ============================= LOGGING ======================================== #
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = False
# ============================= ADS ============================================ #
ADS_API_TOKEN = "<secret>"
ADS_API_URL = "https://ui.adsabs.harvard.edu/v1"
CLASSIC_FULLTEXT_INDEX = "/tmp/all.links"
ADS_REFERENCE_DATA = "/references/resolved"
# ============================= APPLICATION ==================================== #
# 
# Collections we are reporting on
COLLECTIONS = ['AST', 'PS+HP', 'TEST']
# Report formats supported
FORMATS = ['NASA', 'CURATORS', 'SUMMARY']
# Report types supported
SUBJECTS = ['FULLTEXT', 'REFERENCES']
# Which journals are we reporting on per collection
JOURNALS = {
    'AST': ["ApJ..","ApJL","ApJS.","AJ...","MNRAS","A&A..","A&AS.","PASP.","AN...","PhRvD","JCAP.","APh..","CQGra"],
    'PS+HP': ["AREPS","ASTRA","AdSpR","AnGeo","Ap&SS","AsBio","CeMDA","E&PSL","EM&P.","GeCoA","IJAsB","Icar.","JAtS.","JGRA.","JGRD.",
              "JGRE.","M&PS.","M&PSA","Metic","NatGe","P&SS.","PEPI.","RvGeo","SSRv.","SoSyR","SoPh.","SpWea","PSJ..","Moon."],
    'HP': ['SoPh.','SpWea'],
    'TEST': ['ApJ..']
} 
CONTENT_QUERIES = {
    'HP recent sample':'keyword:"sun*" collection:astronomy year:[2010 TO *] doctype:article',
    'PS recent sample':'keyword:(planets* OR "solar sytem*" OR comet* OR meteor* OR kuiper* OR asteroid* OR TNO) year:[2010 TO *] collection:astronomy',
}
SOURCES = {
    'FULLTEXT': ['publisher','arxiv'],
    'REFERENCES': ['publisher', 'crossref']
}
YEAR_IS_VOL = {
    'JCAP.':2003
}
# The root of the output location
OUTPUT_DIRECTORY = '/tmp/reports'

