from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
import pandas as pd
import random
import cv2
import time
import os


'''
This tool is a simple image visualizer and image selection tool.
It handles keyboard press to allow user to save, discard, or label the image as
problematic ethically speaking.
'''
class SelectionTool:

    def __init__(self,config=None):
        self.parse_config(config)
        self.load_paths()
        self.load_urls()

######### CONFIG AND LOADINGS #########
    '''
    This tool uses configurations that should be in the 'configs/M49selConfigs' folder
    but you can just actually put them anywhere and import them.
    Examples configurations are found in the 'configs/M49selConfigs' folder
    Any configuration should have 4 elements : OUTPUTS_DIRECTORY, URL_FILE, OUTPUT_URL, OUTPUT_RGPD
    '''
    def parse_config(self,config):
        assert config is not None, "Expected a configuration, got None ; please provide a configuration when initializing selection tool"
        self.config = config

    '''
    In case of errors, stops, or anything really, we're implementing the loading
    of a previous run to help the user saving and reworking on it later
    '''
    def load_urls(self):
        self.urls_to_save=[]
        self.urls_rgpd = []
        if os.path.exists(self.urls_to_save_path):
            with open(self.urls_to_save_path,"r") as file :
                stream = file.read()
            self.urls_saved=stream.split(',')[:-1]
            self.saved_count = len(self.urls_saved)
        else:
            self.urls_saved = []
            self.saved_count=0
        if os.path.exists(self.urls_rgpd_path):
            with open(self.urls_rgpd_path,"r") as file :
                stream = file.read()
            self.urls_rgpd_saved=stream.split(',')[:-1]
        else:
            self.urls_rgpd_saved = []

    '''
    Loading some useful paths
    '''
    def load_paths(self):
        self.local_dir =os.path.dirname(os.path.abspath(__file__))
        self.urls_filepath = os.path.join(self.config.URL_FILE)
        self.tmp_filepath = os.path.join(self.local_dir,"tmp_img.jpg")
        self.urls_to_save_path = os.path.join(self.local_dir,self.config.OUTPUTS_DIRECTORY,self.config.OUTPUT_URL)
        self.urls_rgpd_path = os.path.join(self.local_dir,self.config.OUTPUTS_DIRECTORY,self.config.OUTPUT_RGPD)

######### INTERN FUNCTIONS #########
    '''
    Handling of the kerboard press.
    Hard coded :
    - to save and image, press s
    - to signal an image as inconvenient, press f
    - to exit app, press echap or q
    - to discard the image, press anything really
    '''
    def _handle_keyboard(self,key,url):
        if key == ord("s"):
            self.urls_to_save.append(url)
        if key == ord("f"):
            self.urls_rgpd.append(url)
        if key == 27 or key == 113 :
            #q or echap has been pressed, exit app
            return 1
        return 0

    '''
    Visualization of the image happens here
    '''
    def _visualize_url(self,url,filepath):
        try :
            urlretrieve(url, filepath)
        except HTTPError :
            print("Got HTML error, skipping")
        except URLError :
            print("Got URL error, skipping")

        img = cv2.imread(filepath,cv2.IMREAD_ANYCOLOR)
        img = cv2.resize(img,(500,500))
        count = self.saved_count + len(self.urls_to_save)
        cv2.putText(img=img, text='Count : ' + str(count), org=(5,25), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 255, 0),thickness=1)
        if img is not None :
            # place the image using a window
            winname = "Image to select"
            cv2.namedWindow(winname)        # Create a named window
            cv2.moveWindow(winname, 1400,30)  # Move it to (1400,30) for personal reasons (like watching youtube while selecting images to prevent my brain from melting)
            cv2.imshow(winname,img)
            pressed_key = cv2.waitKey(0) & 0xFF
            cv2.destroyAllWindows()
        else :
            print("Error : img is none ")
        return pressed_key

    '''
    Saving state and exiting application
    '''
    def _save_and_quit(self):
        print("Exiting application ... ")
        #check if path exists, if not create it
        path = os.path.join(self.local_dir,self.config.OUTPUTS_DIRECTORY)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(self.urls_to_save_path,"a") as output :
            for elem in self.urls_to_save:
                output.write(elem+',')
        with open(self.urls_rgpd_path,"a") as output :
            for elem in self.urls_rgpd:
                output.write(elem+',')

######### MAIN RUN  #########
    '''
    Run the tool according to the chosen configuration
    '''
    def run(self):
        with open(self.urls_filepath,'r') as url_file:
            content = url_file.read()
            urls = content.split(',')
        random.shuffle(urls)
        for url in urls :
            if url in self.urls_to_save or url in self.urls_saved or url in self.urls_rgpd or url in self.urls_rgpd_saved:
                print('Skipping already seen url ... ')
                continue
            state = self._visualize_url(url,self.tmp_filepath)
            exit = self._handle_keyboard(state,url)
            if exit ==1 :
                break
        self._save_and_quit()

'''
I got lazy to go through the hassle of importing variable path passed as argument
from the terminal, so to actually run a configuration, change conf name in the following line
'''
from configs.M49SelConfigs import Western_Europe as conf
tool = SelectionTool(conf)
tool.run()
