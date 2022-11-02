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
This tool here is used to go through images and gather informations about it,
in order to generate a license file
'''
class LicenseCheck:

    def __init__(self,config=None):
        self.parse_config(config)
        self.load_search_params()
        self.bad_images=[]

    ######### CONFIG AND LOADINGS #########
    def parse_config(self,config):
        assert config is not None, "Expected a configuration, got None ; please provide a configuration when initializing parser"
        self.config = config

    def load_search_params(self):
        self.key = self.config.KEY
        self.secret = self.config.SECRET
        self.flickr= FlickrAPI(self.key, self.secret, format='parsed-json')


    ##### FLICKR RELATED  #####
    '''
    Flickr has different kind of licenses, identified by id.
    So we're hardcoding the licenses here, by id.
    '''
    def flickr_from_number_to_license(self,id):
        if id==0 :
            return "All Rights Reserved",""
        if id==1 :
            return "Attribution-NonCommercial-ShareAlike License","https://creativecommons.org/licenses/by-nc-sa/2.0/"
        if id==2 :
            return "Attribution-NonCommercial License","https://creativecommons.org/licenses/by-nc/2.0/"
        if id==3 :
            return "Attribution-NonCommercial-NoDerivs License","https://creativecommons.org/licenses/by-nc-nd/2.0/"
        if id==4 :
            return "Attribution License","https://creativecommons.org/licenses/by/2.0/"
        if id==5 :
            return "Attribution-ShareAlike License","https://creativecommons.org/licenses/by-sa/2.0/"
        if id==6 :
            return "Attribution-NoDerivs License","https://creativecommons.org/licenses/by-nd/2.0/"
        if id==7 :
            return "No known copyright restrictions","https://www.flickr.com/commons/usage/"
        if id==8 :
            return "United States Government Work","http://www.usa.gov/copyright.shtml"
        if id==9 :
            return "Public Domain Dedication (CC0)","https://creativecommons.org/publicdomain/zero/1.0/"
        if id==10 :
            return "Public Domain Mark","https://creativecommons.org/publicdomain/mark/1.0/"
        #Should not happen
        return 1


    '''
    Given the ID of an image from the Flickr platform, retrieve informations
    about the image.
    - id : id of the flickr image

    returns a dictionnary containing informations of the image
    '''
    def get_infos(self,id):
        result = {}
        try :
            response = self.flickr.photos.getInfo(
                api_key = self.key,
                photo_id = id
            )
            response = response['photo']
            keys = response.keys()
            if 'owner' in keys :
                result['author-id']=response['owner']['nsid']
                result['author-name']=response['owner']['username']
            result['url']=response['urls']['url'][0]['_content']
            if 'license' in keys :
                license_id=response['license']
                license_name, license_link = self.flickr_from_number_to_license(int(license_id))
                result['license-name'] = license_name
                result['license-link'] = license_link
        except flickrapi.exceptions.FlickrError as e:
            print("Caught a FlickrError ; skipping photo  ", id)
            return {'author-id': 'Unknown' , 'author-name': 'Unknown' , 'url' : 'Unknown' ,
                    'license-name' : 'None' , 'license-link' : 'None' }
        # print(result)
        return result

    #####  OUTPUTS RELATED  #####
    def init_copyrights_infos(self):
        self.df_copyrights = pd.DataFrame({},columns=['id','url','author-id','author-name','license-name','license-link'])

    def add_copyrights_info(self,id,result):
        author_name = result['author-name']
        author_id = result['author-id']
        url = result['url']
        license_name = result['license-name']
        license_link = result['license-link']
        self.df_copyrights = self.df_copyrights.append(pd.Series(data=[id,url,author_id,author_name,license_name,license_link],index = self.df_copyrights.columns),ignore_index=True)

    def write_copyrights(self,filename="copyrights.csv"):
        script_path = os.path.dirname(os.path.abspath(__file__))
        self.df_copyrights.to_csv(os.path.join(script_path,self.config.OUTPUTS_DIRECTORY,filename))

    #####  INPUTS RELATED  #####
    '''
    This tool supports different kind of inputs : a txt file or a path to a folder
    with images. As the id of the image is contained in the name, these functions
    are used to retrieve the id from the source image name or url.
    '''
    def get_id_from_url(self,url):
        return url.split('/')[-1].split('_')[0]

    def get_id_from_filename(self,filename):
        return filename.split('-')[2].split('_')[0]

    def get_ids_from_folder(self,folder_path):
        for root,dir,files in os.walk(folder_path):
            ids = [self.get_id_from_filename(filename) for filename in [filename for filename in files if '.jpg' in filename]]
            break
        return ids

    #####  RUN   #####
    '''
    Runs the tool on a folder containing images named with their original
    flickr name.
    - folder_path : path to the folder containing the images
    '''
    def run_folder(self,folder_path):
        print("### Running on folder " + folder_path)
        self.init_copyrights_infos()
        ids = self.get_ids_from_folder(folder_path)
        for id in ids:
            result = 1
            while result ==1 :
                result = self.get_infos(id)
            if result == {}:
                self.bad_images.append(id)
                continue
            self.add_copyrights_info(id,result)

    '''
    Runs the tool on a txt filecontaining urls pointing to images from the Flickr
    platform.
    - url_file_path : path to the txt file containing the urls
    '''
    def run_url_file(self,url_file_path):
        print("### Running on urls in " + url_file_path)
        self.init_copyrights_infos()
        with open(url_file_path,'r') as f :
            urls = f.read().split(',')
            ids = [self.get_id_from_url(url) for url in urls]
        for id in ids :
            result=self.get_infos(id)
            self.add_copyrights_info(id,result)


from configs import config_infos_GDS as conf



## RUN on sample
lc = LicenseCheck(conf)
lc.run_url_file("D:\\workspace\\scraper\\test_data\\urls\\test_urls.txt")
lc.write_copyrights()
