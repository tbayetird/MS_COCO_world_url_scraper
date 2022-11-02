from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve
from flickrapi import FlickrAPI
import os,time,sys
import flickrapi

'''
This tool downloads images from the collected urls using the scraper or the selection tool
'''
class ImageDownloader:

    def __init__(self,config=None):
        self.parse_config(config)
        self.load_search_params()

    ######### CONFIG AND LOADINGS #########
    def parse_config(self,config):
        assert config is not None, "Expected a configuration, got None ; please provide a configuration when initializing parser"
        self.config = config

    def load_search_params(self):
        self.key = self.config.KEY
        self.secret = self.config.SECRET
        self.flickr= FlickrAPI(self.key, self.secret, format='parsed-json')


    ##### FLICKR RELATED  #####
    """
    Finds the original format url of the image and downloads it

    - id : id of the image to download in original format
    - output_folder : folder to write outputs
    """
    def get_image(self,id,output_folder):
        #Finding original image url
        try :
            response = self.flickr.photos.getSizes(
                api_key = self.key,
                photo_id = id
            )
            url_to_dl=response['sizes']['size'][-1]['source']
        except flickrapi.exceptions.FlickrError :
            print("Caught a FlickrError 500 Error")
            return 0

        #Downloading image
        filepath = os.path.join(output_folder + '\\' + url_to_dl)
        filepath = filepath.replace('https://live.staticflickr.com','flickr')
        filepath = filepath.replace('/','-')
        if os.path.exists(filepath):
            return 0
        try :
            urlretrieve(url_to_dl, filepath)
        except HTTPError :
            print("Got HTML error, skipping")
        except URLError :
            print("Got URL error, skipping")

    #####  INPUTS RELATED  #####
    '''
    returns the ID of the image pointed by the url
    '''
    def get_id_from_url(self,url):
        return url.split('/')[-1].split('_')[0]

    '''
    return a list of urls from a folder containing urls in a file named "saved_urls.txt".
    to use after selecting images with the sel_tool.
    '''
    def get_urls(self,folder):
        # get all the urls from the "saved_urls" txt files in the folders
        urls = []
        for root,dir,files in os.walk(folder):
            for file in files:
                if file == "saved_urls.txt":
                    urls.append(os.path.join(root,file))
        return urls

    #####  RUN   #####
    '''
    Run the downloader with a txt file containing urls as input
    - url_file_path : path to the url file
    - output_folder : folder to wrtie outputs
    '''
    def run_url_file(self,url_file_path,output_folder):
        print("### Running on urls in " + url_file_path)
        with open(url_file_path,'r') as f :
            urls = f.read().split(',')
            ids = [self.get_id_from_url(url) for url in urls]
        for id in ids :
            result=self.get_image(id,output_folder)

    '''
    Run the downloader with a folder containing a txt file containing urls as input
    - path : path to the input folder. It must contains a file named 'savec_urls.txt'
    '''
    def run_all_selected_images(self,path):
        urls = self.get_urls(path)
        for url in urls :
            location = url.split('\\')[-2]
            output_folder = os.path.join(self.config.OUTPUTS_DIRECTORY,location)
            if not os.path.exists(output_folder):
                os.mkdir(output_folder)
            self.run_url_file(url,output_folder)


from configs import config_download_images as conf
dl = ImageDownloader(conf)
### Examples of RUNS (got too lazy to actually do some arg passer)

# urls = dl.get_urls("D:\\workspace\\scraper\\M49_sel_outputs\\")
# print([url.split('\\')[-2] for url in urls])
# dl.run_url_file("D:\\workspace\\scraper\\test_data\\urls\\test_urls.txt")
# dl.run_folder("D:\\workspace\\scraper\\test_data\\images")
# dl.run_all_selected_images("D:\\workspace\\scraper\\M49_sel_outputs\\_rattrapage\\")
sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"test_data","urls","test_urls.txt")
dl.run_url_file(sample_path,os.path.dirname(sample_path))
