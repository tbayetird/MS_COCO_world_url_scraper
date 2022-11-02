import os

#Init
KEY = "YOUR_KEY"
SECRET = "YOUR_SECRET"
WAIT_TIME = 1

#Paths and name
NAME= "sample M49 test"
CLASSES_FILE = "coco_sample_classes.txt"
LOCATION_FILE = "replace_me"
SCENE_FILE = "sample_scenes.txt"
OUTPUTS_DIRECTORY = "test_M49_serv_outputs"
LOG_DIRECTORY = OUTPUTS_DIRECTORY
LOG_CSV_FILE = "t_M49.xlsx"
LOG_FILE = "t_M49_log.log"
URL_FILE = "t_M49_urls.txt"
CONFIG_PATH = os.path.abspath(__file__)

#Params
SAMPLE_CLASSES = 3
LOCATION = 1
STORE_URL=1
LOG_TO_CSV = 1
MIN_PER_CLASS = 100


#Search
PER_PAGE = 500
PAGE = 1
MEDIA = 'photos'
SORT = 'relevance'
SAFE_SEARCH = 1
LICENSE = '1,2,3,4,5,6,7,9,10' #ALL COMMONS
EXTRAS = 'url_q, geo,date_upload,owner_name'
