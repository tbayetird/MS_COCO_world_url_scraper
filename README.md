# MS COCO WORLD URL SCRAPER

This tool is used to scrape urls to gather MS COCO-style images, through the Flickr platform. It works thanks to configurations and the Flickr API.

## Installation

All dependencies are found in the spec-file.txt
You can automatize installation thanks to conda, using :

'''
conda create --name scraper --file spec-file.txt
'''

## Quick start

First, you need to modify the KEY and SECRET lines from the configs/config_M49_test.py configuration, with your own KEY and SECRET from the Flickr API

Next, just run the run_M49_socket.py :

'''
python run_M49_socket.py
'''

The scraper will start an internal server and run the config_test configuration

## Choosing a configuration

To run a different configuration, modify the line 9 from the run_M49_server.py script.

To switch from config_test to config_M49_test, change the following line :

'''
from configs import config_test as config_M49
'''
in :

'''
from configs import config_M49_test as config_M49
'''

Do not forget to add you KEY and SECRET to the configuration

## Modifying a configuration

You can modify every parameter of any configuration, given that they respect the boundaries of said parameters.
