# ============================= LOGGING ======================================== #
LOGGING_LEVEL = 'INFO'
LOG_STDOUT = False
# ============================= ADS ============================================ #
ADS_API_TOKEN = "<secret>"
ADS_API_URL = "https://ui.adsabs.harvard.edu/v1"
CLASSIC_FULLTEXT_INDEX = "/tmp/all.links"
# ============================= APPLICATION ==================================== #
# 
# Collections we are reporting on
COLLECTIONS = ['AST', 'PS+HP']
# Report formats supported
FORMATS = ['NASA', 'CURATORS']
# Which journals are we reporting on per collection
JOURNALS = {
    'AST': ["ApJ..","ApJL","ApJS.","AJ...","MNRAS","A&A..","A&AS.","PASP.","AN...","PhRvD","JCAP.","APh..","CQGra"],
    'PS+HP': ["AREPS","ASTRA","AdSpR","AnGeo","Ap&SS","AsBio","CeMDA","E&PSL","EM&P.","GeCoA","IJAsB","Icar.","JAtS.","JGRA.","JGRD.",
              "JGRE.","M&PS.","M&PSA","Metic","NatGe","P&SS.","PEPI.","RvGeo","SSRv.","SoSyR","SoPh.","SpWea","PSJ..","Moon."]
} 

YEAR_IS_VOL = {
    'JCAP.':2003
}

