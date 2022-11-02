import os

#Init
KEY = "YOUR_KEY"
SECRET = "YOUR_SECRET"
WAIT_TIME = 1

#Paths and name
CLASSES_FILE = "coco_classes.txt"
LOCATION_FILE = "West_Africa_locations.txt"
# LOCATION_FILE = "West_Europe_locations.txt"
LOG_CSV_FILE = "logs.csv"
OUTPUTS_DIRECTORY = "outputs"
LOG_DIRECTORY = OUTPUTS_DIRECTORY
LOG_FILE = "log_file.log"
CONFIG_PATH = os.path.abspath(__file__)
SCENE_FILE = "scenes.txt"
URL_FILE = "M49_urls.txt"

#Params
SAMPLE_CLASSES = 0
CLASSES = "coco_sample"
LOCATION = 1
DOWNLOAD_IMAGES = 0
LOG_TO_CSV = 1


#Search
PER_PAGE = 5
MEDIA = 'photos'
SORT = 'relevance'
SAFE_SEARCH = 1
LICENSE = '1,2,3,4,5,6,7,9,10' #ALL COMMONS
EXTRAS = 'url_q, geo'
