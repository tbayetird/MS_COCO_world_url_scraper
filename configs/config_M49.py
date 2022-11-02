import os

#Init
KEY = "YOUR_KEY"
SECRET = "YOUR_SECRET"
WAIT_TIME = 1

#Paths and name
NAME= "M49"
CLASSES_FILE = "coco_classes.txt"
LOCATION_FILE = "replace_me"
SCENE_FILE = "scenes.txt"
OUTPUTS_DIRECTORY = "M49_serv_outputs"
LOG_DIRECTORY = OUTPUTS_DIRECTORY
LOG_CSV_FILE = "M49.xlsx"
LOG_FILE = "M49_log.log"
URL_FILE = "M49_urls.txt"
CONFIG_PATH = os.path.abspath(__file__)

#Params
SAMPLE_CLASSES = 0
LOCATION = 1
DOWNLOAD_IMAGES = 0
STORE_URL=1
LOG_TO_CSV = 1
MIN_PER_CLASS = 100

#Search
PER_PAGE = 500
PAGE=1
MEDIA = 'photos'
SORT = 'relevance'
SAFE_SEARCH = 1
LICENSE = '1,2,3,4,5,6,7,9,10' #ALL COMMONS
EXTRAS = 'url_q, geo,date_upload,owner_name'
