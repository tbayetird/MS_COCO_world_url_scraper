import os

#Init
KEY = "YOUR_KEY"
SECRET = "YOUR_SECRET"
WAIT_TIME = 1

#Paths and name
NAME= "sample test"
CLASSES_FILE = "coco_sample_classes.txt"
LOCATION_FILE = "sample_locations.txt"
SCENE_FILE = "sample_scenes.txt"
LOG_CSV_FILE = "test_logs.xlsx"
OUTPUTS_DIRECTORY = "test_outputs"
LOG_DIRECTORY = OUTPUTS_DIRECTORY
LOG_FILE = "test_log_file.log"
URL_FILE = "test_urls.txt"
CONFIG_PATH = os.path.abspath(__file__)

#Params
SAMPLE_CLASSES = 5
LOCATION = 1
DOWNLOAD_IMAGES = 0
STORE_URL=1
LOG_TO_CSV = 1
MIN_PER_CLASS = 5000


#Search
PER_PAGE = 5
PAGE = 1
MEDIA = 'photos'
SORT = 'relevance'
SAFE_SEARCH = 1
LICENSE = '1,2,3,4,5,6,7,9,10' #ALL COMMONS
EXTRAS = 'url_q, geo,date_upload,owner_name'
