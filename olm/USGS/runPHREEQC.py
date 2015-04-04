"""
Executable to re-process a site directory in PHREEQC
"""

from olm.USGS.loadWaterQualityData import loadSiteListData
from olm.USGS.PhreeqcPandas import processPanel
import xlrd, os, sys
import cPickle as pickle

def runPHREEQC(startfilename, charge_balance_only=False):
    print("Processing site water chemisty data in PHREEQC...")
    startfile = xlrd.open_workbook(startfilename)
    sheet = startfile.sheet_by_index(0)
    #parse start file to determine what should be done
    characteristicsBlockStarted = False
    settingsDict = {}
    charDict = {}
    for rownum in range(sheet.nrows):
        line = sheet.row_values(rownum)
        if not(line[0][0] == '#'): #ignore comments
            if not(characteristicsBlockStarted):      
                if not(line[0] == 'Characteristic'):
                    settingsDict[line[0]] = line[1]
                else: #grab the characteristic block column headings
                    characteristicsBlockStarted = True
                    column_headings = line[1:]
            else:
                charDict[line[0]] = dict(zip(column_headings,line[1:]))                
    DATABASE_FILE = os.path.join(
        settingsDict['Path to chemical database'], 
        settingsDict['Name of chemical database'])
    LOG_FILE = os.path.join(
        settingsDict['Path to output directory'],
        settingsDict['Name of output directory'],
        settingsDict['Log file name'])  
    PHREEQC_PATH = settingsDict['Path to PHREEQC'] 
    bracket_charge_balance = settingsDict['Force balance on Ca and Alk'] == 'Yes'
    sitesdir = os.path.join(settingsDict['Path to output directory'],
                            settingsDict['Name of output directory'])
    #Load data for sites
    sitesDict = loadSiteListData(processedSitesDir=sitesdir)
    if not charge_balance_only:
        for location, pnl in sitesDict.iteritems():               
            print "Processing site panel from ", location
            phreeqc_df = processPanel(pnl, os.path.join(sitesdir,location), PHREEQC_PATH, DATABASE_FILE)               
            phreeqc_site_file = os.path.join(sitesdir,location,location+'-PHREEQC.pkl')
            try:
                pickle.dump(phreeqc_df, open(phreeqc_site_file, 'wb'))
                phreeqc_df.to_csv(phreeqc_site_file[:-3]+'csv')
            except IOError:
                print('Problem writing out PHREEQC data file.')
    if bracket_charge_balance:
        for location, pnl in sitesDict.iteritems():               
            #Force balance on Calcium
            phreeqc_df_ca = processPanel(pnl, os.path.join(sitesdir,location), PHREEQC_PATH, DATABASE_FILE, force_balance='Ca')               
            phreeqc_site_file_ca = os.path.join(sitesdir,location,location+'-PHREEQC-Ca.pkl')
            try:
                pickle.dump(phreeqc_df_ca, open(phreeqc_site_file_ca, 'wb'))
                phreeqc_df_ca.to_csv(phreeqc_site_file_ca[:-3]+'csv')
            except IOError:
                print('Problem writing out PHREEQC Ca data file.')               
            #Force balance on Alkalinity
            phreeqc_df_alk = processPanel(pnl, os.path.join(sitesdir,location), PHREEQC_PATH, DATABASE_FILE, force_balance='Alk')               
            phreeqc_site_file_alk = os.path.join(sitesdir,location,location+'-PHREEQC-Alk.pkl')
            try:
                pickle.dump(phreeqc_df_alk, open(phreeqc_site_file_alk, 'wb'))
                phreeqc_df_alk.to_csv(phreeqc_site_file_alk[:-3]+'csv')
            except IOError:
                print('Problem writing out PHREEQC Alk data file.')                

if __name__=="__main__":
    #get site directory  and charge bracketing from command line argument
    startfilename = sys.argv[1]
    runPHREEQC(startfilename)
