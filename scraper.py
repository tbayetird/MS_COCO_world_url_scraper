from openpyxl.utils.dataframe import dataframe_to_rows
from urllib.request import urlretrieve
from flickrapi import FlickrAPI
from pprint import pprint
import pandas as pd
import os,time,sys
import flickrapi
import openpyxl
import logging
import shutil
import time

from _thread import *
import threading
import socket

'''
This is the class for the actual scraper, so all the querry-related and logs-related
stuff is right here.
This scraper is using the Flickr API to retrieve images from the flickr platform
using combinations of keywords in the MS-COCO style, upgraded with some locations
names from around the world.
It stores the urls for each geographical zone (as taken from the M49 norm from the UN)
in a txt file.
'''
class Scraper:

    '''
    Initialization requires pasing configurations, loading paths, search parameters,
    and server-related stuff, as the scraper is run through an internal server-socket fashion
    to allow for some crash handling and multiple configurations handling.
    '''
    def __init__(self,config=None,socket=None,lock=None):
        self.parse_config(config)
        self.load_paths()
        self.load_search_params()
        self.socket = socket
        self.lock = lock


    ######### CONFIG AND LOADINGS #########
    def parse_config(self,config):
        assert config is not None, "Expected a configuration, got None ; please provide a configuration when initializing parser"
        self.config = config

    def load_paths(self):
        self.local_dir =os.path.dirname(os.path.abspath(__file__))
        self.scenes = pd.read_csv(os.path.join(self.local_dir,"scenes",self.config.SCENE_FILE))['scenes']
        if bool(self.config.LOCATION):
            self.locations=pd.read_csv(os.path.join(self.local_dir,"locations",self.config.LOCATION_FILE))['locations']
        else:
            self.locations=[None]
        if bool(self.config.SAMPLE_CLASSES):
            self.classes = pd.read_csv(os.path.join(self.local_dir,"classes",self.config.CLASSES_FILE)).sample(self.config.SAMPLE_CLASSES)['class']
        else:
            self.classes = pd.read_csv(os.path.join(self.local_dir,"classes",self.config.CLASSES_FILE))['class']
        self.csv_logs_path=os.path.join(self.local_dir,self.config.LOG_DIRECTORY,self.config.LOG_CSV_FILE)
        self.urls_logs_path = os.path.join(self.local_dir,self.config.LOG_DIRECTORY,self.config.URL_FILE)

    def load_search_params(self):
        self.key = self.config.KEY
        self.secret = self.config.SECRET
        self.wait_time = self.config.WAIT_TIME
        self.flickr= FlickrAPI(self.key, self.secret, format='parsed-json')


    ##### FLICKR AND QUERRY RELATED #####
    '''
    Build the querries that will go through the Flickr API to retrieve URLs.
    - word : the word we're building the querries for
    - category_list : a list of string containing the categories used for the scraping
    - scene_list : a list of string containing the scenes used for the scraping
    - loc : the location we're currently working on, as a string.

    returns a list of string containing querries to be put through the Flickr API
    '''
    def get_querries(self,word,category_list,scene_list,loc=None):
        querries=[]
        ## Pairwise categories querries
        for category in category_list:
            if category == word :
                continue
            tmp_querry = word + " " + category
            if loc is None :
                querries.append(tmp_querry)
            else :
                querries.append(tmp_querry + " " +loc)
        ## Pair of object + scene querries
        for scene in scene_list:
            tmp_querry = word + " " + scene
            if loc is None :
                querries.append(tmp_querry)
            else :
                querries.append(tmp_querry + " " +loc)
        return querries

    '''
    Build a querry that will go through the Flickr API to retrieve URLs.
    - word : the word we're building the querries for
    - loc : the location we're currently working on, as a string.

    returns a string containing a querry to be put through the Flickr API
    '''
    def get_querry(self,word, loc=None):
        if loc is None :
            return word
        return word + " " + loc

    '''
    Procedure requires that the scraper should not save more than 5 images from
    the same author in a day timeframe. This is handle through this function.
    - photos : a list of dictionnaries containing the outputs of a Flickr API request

    returns a list of elements from the input directory.
    '''
    def clean_results(self,photos):
        # clean the results : no more than 5 images from the same author in a day timeframe
        author_date_dic = {}
        tmp_photos=[]
        for photo in photos:
            author = photo['ownername']
            date = photo['dateupload']
            key = author+date
            if key not in author_date_dic:
                author_date_dic[key]=1
                tmp_photos.append(photo)
            else :
                if author_date_dic[key]>=5:
                    continue
                author_date_dic[key]+=1
                tmp_photos.append(photo)
        return tmp_photos

    """
    The actual handling of Flickr API
    - querry : the querry to be put through the API
    - log : passed as paramater to log errors from Flickr API

    returns a dictionnary containing the results of the scraping
    """
    def search_word(self,querry,log):
        try :
            result  = self.flickr.photos.search(
                api_key = self.key,
                text = querry,
                per_page = self.config.PER_PAGE,
                page = self.config.PAGE,
                media = self.config.MEDIA,
                sort = self.config.SORT,
                safe_search = self.config.SAFE_SEARCH,
                license = self.config.LICENSE,
                extras = self.config.EXTRAS
            )
            photos = self.clean_results(result['photos']['photo'])
            result['photos']['photo']=photos
        except flickrapi.exceptions.FlickrError :
            log.info("Caught a FlickrError 500 Error ; searching again ")
            result=self.search_word(querry,log)
        return result


    ##### LOGS RELATED #####
    '''
    All logs related functions are situated in this section. We log a lot of
    information at different levels and in differents formats (txt, csv).
    They're pretty explicit by themselves and boring to annotate so I'll leave
    them like that
    '''
    def update_csv_logs(self,sheet,data,i=None, loc = None ):
        workbook = openpyxl.load_workbook(self.csv_logs_path)

        sheet = workbook[sheet]
        for row in dataframe_to_rows(data,header=False):
            sheet.append(row)

        if i is not None :
            loc_sheet = workbook[workbook.sheetnames[i+1]]
            for row in dataframe_to_rows(data,header=False):
                loc_sheet.append(row)

        if loc is not None :
            loc_sheet_name = "logs_"+loc
            loc_sheet = workbook[loc_sheet_name[:30]]
            for row in dataframe_to_rows(data,header=False):
                loc_sheet.append(row)
        workbook.save(self.csv_logs_path)
        workbook.close()

    def update_urls_logs(self,buffer_urls):
        with open(self.urls_logs_path,"a") as url_output:
            url_output.write(buffer_urls)

    def get_done_classes(self,df,classes):
        tmp_df = df[df['Querry'].isin(classes)]
        return tmp_df['Querry'].tolist()

    def get_filtered(self,df,classe):
        tmp_df = df[df['Querry'].str.startswith(classe)]
        filter = tmp_df['Querry']!=classe
        tmp_df = tmp_df.where(filter)
        return tmp_df.dropna()

    def get_total_image_classes(self,path,classes):
        df= pd.read_excel(path,sheet_name="full logs").dropna()
        done_classes = self.get_done_classes(df,classes)
        total_image_classes = {}
        for elem in done_classes :
            filter = df['Querry']==elem
            total_image_classes[elem]=int(df.where(filter).dropna()['Number of results'].tolist()[0])
        leftover_classes = [elem for elem in classes if (elem not in done_classes)]
        for elem in leftover_classes:
            tmp_df = self.get_filtered(df,elem)
            if not tmp_df.empty :
                total_image_classes[elem]=sum(tmp_df['Number of results'].tolist())
        return done_classes,total_image_classes

    def get_done_querries(self,path):
        df= pd.read_excel(path,sheet_name="full logs")
        return df['Querry'].dropna().tolist()

    def log_buffer_search(self,buffer_txt,buffer_csv,buffer_urls,log,loc):
        log.info(buffer_txt)
        data = pd.DataFrame(buffer_csv)
        self.update_csv_logs(data=data,sheet="full logs",loc = loc )
        self.update_urls_logs(buffer_urls)

    def buffer_search(self,querry,results,log):
        buffer_txt = "++ Results for querry {}\n".format(querry)
        buffer_txt += "Total of image found : {}\n".format(str(min(results['total'],4000)))
        buffer_txt += f"Total of urls found : {len(results['photo'])}\n"
        buffer_txt += f" results total : {results['total']}\n"

        buffer_csv = {'Querry' : querry,
                'Number of results' : results['total']}
        return results['total'],buffer_txt,buffer_csv

    def log_class(self,given_class,total,log):
        #CSV LOGS
        data = {'Querry' : [given_class],
                'Number of results' : [total]}
        data = pd.DataFrame(data)
        self.update_csv_logs(data = data,sheet = "full logs")

        #TXT LOGS
        print("+++++ Results for class {}".format(given_class))
        print("Total of images found : {}".format(total))
        log.info("+++++ Results for class {}".format(given_class))
        log.info("Total of {} images found : {}".format(given_class,total))

    def log_total(self,total,time,log):
        #CSV LOGS
        data = {'Querry' : ['All class'],
                'Number of results' : [total]}
        data = pd.DataFrame(data)
        self.update_csv_logs(data = data,sheet = "full logs")

        #TXT LOGS
        log.info("Total images found using this config : {}".format(total))
        log.info("Total CPU time used : {}".format(time))

    def init_logs(self,path,locations,catch_up =False):
        if not catch_up :
            shutil.copy(self.config.CONFIG_PATH,path)
        log = logging.getLogger(self.config.NAME)
        log.setLevel(logging.DEBUG)
        handler = logging.FileHandler(path)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
            )
        handler.setFormatter(formatter)
        log.addHandler(handler)
        if not catch_up :
            log.info(" ")
            log.info(" Config is logged above for record, logging starts here ")
            log.info(" ")
            log.info(" __________________________________________________   ")
            log.info(" ")

            # Creating excel file to gather sheets of logs
            writer = pd.ExcelWriter(os.path.join(self.local_dir,self.config.LOG_DIRECTORY,self.config.LOG_CSV_FILE),
                                    engine = "xlsxwriter")
            data = {'Querry' : None,
                    'Number of results' : None}
            df = pd.DataFrame(data, columns = ['Querry','Number of results'])
            df.to_excel(writer,sheet_name="full logs")
            for i,loc in enumerate(locations):
                sheet_name = "logs_"+ str(locations[i])
                tmp_df = pd.DataFrame(data, columns = ['Querry','Number of results'])
                tmp_df.to_excel(writer,sheet_name=sheet_name[:30])
            writer.save()
        return handler,log

    ##### SERVER RELATED #####
    '''
    The scraper is handled by a server listening to sockets, all servers and sockets
    related functions are in this section.
    '''
    def get_message(self,log):
        log.info(f"------ [DEBUG] IN SCRAPER  ------ Getting message")
        ##put server in listening mode
        self.socket.listen(15)
        c, addr = self.socket.accept()
        self.lock.acquire()
        data = c.recv(1024)
        log.info('------ [DEBUG] IN SCRAPER  ------ Message received from socket : {}'.format(data.decode('ascii')))
        # print('###### [DEBUG] IN SCRAPER  ')
        return c

    def send_message(self,connection,message,log):
        log.info(f"------ [DEBUG] IN SCRAPER  ------ Sending message ")
        self.lock.release()
        connection.send(message)
        connection.close()

    ##### SCRAPING RELATED #####
    '''
    This section constains the functions related to actually running the scraper
    , handling the results from the Flickr API, building the outputs, ...
    '''

    '''
    This function handle the call fo the Flickr API, logs and writes them when
    necessary

    - querry : querry to be passed to the Flickr API
    - elem : the  word used as the basis for the querry
    - log : passed as paramater to log errors from Flickr API
    - total_images_class : total number of images for the considered class, int
    - log_to_csv : boolean, whether we log to csv or no
    - store_urls : boolean, whether we store the urls or no
    '''
    def handle_querry(self,querry,elem,log,total_images_class,log_to_csv,store_urls):
        result = self.search_word(querry,log)
        savedir = os.path.join(self.local_dir,self.config.OUTPUTS_DIRECTORY,elem)
        photos = result['photos']
        nb_imgs,buffer_txt,buffer_csv=self.buffer_search(querry,photos,log)
        buffer_urls=''
        total_images_class += nb_imgs
        if log_to_csv:
            tmp_serie=pd.Series([nb_imgs],index=[querry])

        if store_urls:
            for photo in photos['photo']:
                buffer_urls+= str(photo['url_q']) + ','

        return total_images_class,buffer_txt,buffer_csv,buffer_urls

    '''
    Backbone of the scraper, organizes everything and run through all the work
    - category_list : list of string, containing the considered categories
    - scene_list : list of string, containing the considered scenes
    - locations : list of string, containing the considered locations
    - log_to_csv : boolean, whether we log to csv or no
    - store_urls : boolean, whether we store the urls or no
    '''
    def scrape_all(self, category_list, scene_list, locations=[None],store_urls=False, log_to_csv=False):
        start_time= time.time()
        #check if logs has already started and start from previous step, or start new ones
        log_file_path=os.path.join(self.local_dir,self.config.LOG_DIRECTORY,self.config.LOG_FILE)
        if os.path.exists(log_file_path):
            print("LOG FILES EXISTS ALREADY, We'll be skipping what's been done")
            #identify what has already been done
            done_querries = self.get_done_querries(self.csv_logs_path)
            done_classes,total_image_classes = self.get_total_image_classes(self.csv_logs_path,category_list)
            if len(done_classes)==len(category_list):
                print(" All queries were already done, skipping file ")
                return 0
            #still need to catch up
            handler,log = self.init_logs(log_file_path,locations,catch_up = True)
        else:
            done_querries=[]
            done_classes = []
            total_image_classes={}
            handler,log = self.init_logs(log_file_path,locations)

        #Walk through all the querries
        total_images=0
        series=[]
        series_by_loc=[]
        urls=[]
        for elem in category_list:
            if elem in done_classes:
                print(f'Class {elem} is already done, skipping ')
                total_images += total_image_classes[elem]
                c = self.get_message(log)
                self.send_message(c,str(f"{elem} was already done, scraping next object").encode('utf-8'),log)
                continue
            if elem in total_image_classes.keys():
                total_images_class = int(total_image_classes[elem])
            else :
                total_images_class = 0
            for i,loc in enumerate(locations) :
                c = self.get_message(log)
                querries = self.get_querries(word=elem,
                                            loc=loc,
                                            category_list=category_list,
                                            scene_list=scene_list)
                lasting_querries = [x for x in querries  if (x not in done_querries)]
                if len(lasting_querries)==0:
                    self.send_message(c,str(f"{elem} + {loc} was already done, scraping next location").encode('utf-8'),log)
                    continue
                buffer_txt = ''
                buffer_csv = {'Querry' : [], 'Number of results' : []}
                buffer_urls = ''
                for querry in lasting_querries :
                    try :
                        total_images_class,tmp_buffer_txt,tmp_buffer_csv,tmp_buffer_url = self.handle_querry(querry,elem,log,total_images_class,log_to_csv,store_urls)
                        buffer_txt += tmp_buffer_txt
                        buffer_urls += tmp_buffer_url
                        for key in buffer_csv.keys():
                            buffer_csv[key].append(tmp_buffer_csv[key])
                    except Exception as e :
                        log.info(f"------ [DEBUG] IN SCRAPER  ------ caught exception {e} with querry {querry}")
                        self.send_message(c,str(f"{elem} + {loc} generated exception {e}").encode('utf-8'),log)
                        raise e
                #Log buffers here, at the end of the epoch of the location
                self.log_buffer_search(buffer_txt,buffer_csv,buffer_urls,log,loc)
                self.send_message(c,str(f"{elem} + {loc} is done, scraping next location").encode('utf-8'),log)
            total_images+=total_images_class
            if total_images_class < self.config.MIN_PER_CLASS :
                buffer_txt = ''
                buffer_csv = {'Querry' : [], 'Number of results' : []}
                buffer_urls = ''
                #We didn't get enough images, let's add some querries but without pair combination
                for i,loc in enumerate(locations):
                    querry = self.get_querry(elem,loc)
                    total_images_class,tmp_buffer_txt,tmp_buffer_csv,tmp_buffer_urls = self.handle_querry(querry,elem,log,total_images_class,log_to_csv,store_urls)
                    buffer_txt += tmp_buffer_txt
                    buffer_urls += tmp_buffer_url
                    for key in buffer_csv.keys():
                        buffer_csv[key].append(tmp_buffer_csv[key])
                self.log_buffer_search(buffer_txt,buffer_csv,buffer_urls,log,loc)

            self.log_class(elem,total_images_class,log)
            if log_to_csv:
                series.append(pd.Series([total_images_class],index=[elem]))
        # ending logs before saving and closing
        end_time = round(time.time()-start_time, 2)
        self.log_total(total_images,end_time,log)

        #closing loggs is not that easy
        log.removeHandler(handler)
        log.handlers.clear()
        logging.shutdown()
        return 0

    def run_scrape(self):
        self.scrape_all(category_list = self.classes,
                        scene_list = self.scenes,
                        locations = self.locations,
                        log_to_csv=bool(self.config.LOG_TO_CSV),
                        store_urls=self.config.STORE_URL)
