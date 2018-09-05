## crawlerMD adapted to Chrome
## series/multiple trigger
## config: macOS High Sierra; python 2.7.13; chrome
## please download selenium and chromedriver first

### Things-to-be-improved
###### make 'parallel': do batch submission
###### allow multiple site mutations
###### allow site-specific mutations

# Created: Aug 5th, 2018
# By: Xiaoyu (Helen) 
# Last updated: Aug 5th 2018, xiaoyu


###########################   input    ###############################
## download_path: Create a parental folder to accomodate sub-folders;
## recommended: include date&parameters in name (e.g, 20180805_downState_saturated)
## sub-folders will be named as position name (e.g, '124')
## pdb_path: Set path to pdb file
### TO-BE-IMPROVED: Add site-specific mutations here
## screening positons: follow pdb numbering
## translations: the translation when doing protein orientation, -3 for down/-9 for up
## environ path: path to webdriver.exec

download_path = '/Users/helen/Desktop/Francois/MolecularDynamics/Dry/Job_Submit/CrawlerTest'
pdb_path='/Users/helen/Desktop/Francois/MolecularDynamics/Dry/GgVSD_UP_trnc.pdb'
screening_position = [70,71]
screening_mutants = ['ALA']
translation = -3
import os
os.environ["PATH"] += os.pathsep + r'/Users/helen/Desktop'

#######################  import and defaults  ########################
import selenium
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time,re

xpath_dict = {'ALA':'1','ARG':'2','ASN':'3','ASP':'4','CYS':'5',\
              'GLN':'6','GLU':'7','GLY':'8','HSD':'9','HSE':'10',\
              'HSP':'11','ILE':'12','LEU':'13','LYS':'14','MET':'15',\
              'PHE':'16','PRO':'17','SER':'18','THR':'19','TRP':'20',\
              'TYR':'21','VAL':'22','HIS':'23'}

####################  series-trigger function  ######################
def seriesTrigger(dlpath,pdbpath,pos,mut,trans):
    # Set dlpath as parental folder
    # RECOMMENDED: include date&parameters in folder name
    # For each position there will be a seperate folder for all tgz
    # Check if parental path exists:
    isExists = os.path.exists(dlpath)
    if not isExists:
        os.makedirs(dlpath)
        print('download path: %s created~' %(str(dlpath)))
    for position in pos:
        dlChildPath = os.path.join(dlpath,str(position))
        ## Create sub-folder
        isExists = os.path.exists(dlChildPath)
        if not isExists:
            os.makedirs(dlChildPath)
            print('download path: %s created~' %(str(dlChildPath)))
        for mutation in mut:
            ## define each mutation
            Test1 = CharmmGuiMB()
            Test1.setUp(dlChildPath)
            ## define xpath for each mutant
            default_xpath = '/html/body/div[4]/div[2]/div[2]/div[2]/form/p[3]/table/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[4]/select/option['
            list_xpath = [default_xpath,xpath_dict[mutation],']']
            mutation_xpath = ''.join(list_xpath)
            Test1.test_charmm_gui_mb(pdbpath,position,mutation_xpath,trans)

#####################  class CharmmGuiMB  ######################
class CharmmGuiMB():
    def setUp(self,dlAddr):
        ## Chrome-specific set up && case-specific set up
        prefs ={'profile.default_content_settings.popups': 0,"download.default_directory":dlAddr}
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chromeOptions)
        ## Generals
        self.driver.implicitly_wait(2000) #SECONDS
        self.base_url = "http://www.charmm-gui.org/?doc=input/membrane"
        self.verificationErrors = []
        self.accept_next_alert = True


    def test_charmm_gui_mb(self,pdbAddr,pos,mut_xpath,trans):
        driver=self.driver
        self.driver.implicitly_wait(2000)
        ## Upload PDB from local 
        driver.get(self.base_url)
        driver.find_element_by_name("file").send_keys(pdbAddr)
        driver.find_element_by_name("pdb_format").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Select Model/Chain'])[1]/following::img[1]").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Manipulate PDB'])[1]/following::img[1]").click()
        ## Select mutations
        driver.find_element_by_id("mutation_checked").click()
        driver.find_element_by_id("mutation_rid_0").click()
        ### TO-BE-IMPROVED: multiple mutation
        Select(driver.find_element_by_id("mutation_rid_0")).select_by_visible_text(str(pos)) ###
        driver.find_element_by_xpath(mut_xpath).click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Generate PDB and Orient Molecule'])[1]/following::img[1]").click()
        ## Align and translation
        driver.find_element_by_name("align_option").click()
        driver.find_element_by_name("translate_checked").click()
        driver.find_element_by_name("zdist").send_keys(str(trans))###
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Calculate Cross-Sectional Area'])[1]/following::img[1]").click()
        ## Define membrane: shape, components and ratio
        ### TO-BE-IMPROVED: add a feedback here to report if systems size is around 70
        Select(driver.find_element_by_name("hetero_boxtype")).select_by_visible_text("Hexagonal")
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Heterogeneous Lipid'])[2]/following::option[2]").click()     
        driver.find_element_by_name("hetero_wdist").clear()
        driver.find_element_by_name("hetero_wdist").send_keys("20")
        driver.find_element_by_name("hetero_lx").send_keys("70")
        link = driver.find_element_by_xpath("/html/body/div[4]/div[2]/div[2]/div[3]/form/div[4]/div/div[1]/p[2]/table/tbody/tr[4]/td/img")
        driver.execute_script('$(arguments[0]).click()', link)
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Heterogeneous Lipid'])[2]/following::option[2]").click()
        driver.find_element_by_id("lipid_ratio[upper][popc]").clear()
        driver.find_element_by_id("lipid_ratio[upper][popc]").send_keys("1")
        driver.find_element_by_id("lipid_ratio[lower][popc]").clear()
        driver.find_element_by_id("lipid_ratio[lower][popc]").send_keys("1")
        driver.find_element_by_id("hetero_size_button").click()
        driver.find_element_by_id("hetero_size_button").click() # it's weird but double click is necessary here
        time.sleep(3) # probably need a second to show system info, set as 3s here
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Determine the System Size'])[1]/following::img[1]").click()
        WebDriverWait(driver,3000).until(EC.element_to_be_clickable((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Build Components'])[1]/following::img[1]"))).click()
        WebDriverWait(driver,3000).until(EC.element_to_be_clickable((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Assemble Components'])[1]/following::img[1]")))
        # In 'Manual' mode the page sometimes goes blank after assemble, I guess it's related to the bug "Failed to find value field", so do compulsory wait here
        ## Assemble components 1
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Assemble Components'])[1]/following::img[1]").click() 
        time.sleep(30)
        ## Assemble components 2
        WebDriverWait(driver,3000).until(EC.element_to_be_clickable((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Assemble Components'])[1]/following::img[1]")))
        link = driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Assemble Components'])[1]/following::img[1]")
        driver.execute_script('$(arguments[0]).click()', link)
        ## Choose gromacs and generate files
        driver.find_element_by_name("gmx_checked").click()
        driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='Next Step:Generate Equilibration and Dynamics Inputs'])[1]/following::img[1]").click()
        time.sleep(100)
        ## Download tgz
        WebDriverWait(driver,2000).until(EC.element_to_be_clickable((By.XPATH,"(.//*[normalize-space(text()) and normalize-space(.)='step5_assembly.pdb'])[1]/following::a[2]")))        
        link = driver.find_element_by_xpath("(.//*[normalize-space(text()) and normalize-space(.)='step5_assembly.pdb'])[1]/following::a[2]")
        driver.execute_script('$(arguments[0]).click()', link)
        time.sleep(3) # wait until download finished
        ## Quit Chrome
        self.driver.quit()

#############################  main  ###############################
seriesTrigger(download_path,pdb_path,screening_position,screening_mutants,translation)


    
    
