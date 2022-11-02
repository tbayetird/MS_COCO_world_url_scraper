from scraper import Scraper
import os
import socket
import time
from _thread import *
import threading

#Choosing a configuration to run 
from configs import config_test as config_M49

'''
The server side runs the scraper with multiple configurations, one after another.
This functions allows the server to modify the considered configuration and thus
go through all the differents configurations.
- name : name of the location file being handled
'''
def modify_config(config,name):
    tmp_csv_file = config.LOG_CSV_FILE
    tmp_csv_file_split = tmp_csv_file.split('.')
    tmp_csv_file = tmp_csv_file_split[0] + name.split('.')[0][3:]
    tmp_csv_file = tmp_csv_file +'.'+tmp_csv_file_split[1]

    config.LOG_CSV_FILE = tmp_csv_file

    tmp_log_file = config.LOG_FILE
    tmp_log_file_split = tmp_log_file.split('.')
    tmp_log_file = tmp_log_file_split[0] + name.split('.')[0][3:]
    tmp_log_file = tmp_log_file +'.'+tmp_log_file_split[1]
    config.LOG_FILE = tmp_log_file

    tmp_url_file = config.URL_FILE
    tmp_url_file_split = tmp_url_file.split('.')
    tmp_url_file = tmp_url_file_split[0] + name.split('.')[0][3:]
    tmp_url_file = tmp_url_file +'.'+tmp_url_file_split[1]
    config.URL_FILE = tmp_url_file

    config.LOCATION_FILE = "M49\\" + name

### PARAMS
# some of the pathes are hardcoded, either de not modify names of folders or adapt the following lines
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),config_M49.OUTPUTS_DIRECTORY)
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
location_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"locations","M49")
log_csv_file = config_M49.LOG_CSV_FILE
log_file = config_M49.LOG_FILE
url_file = config_M49.URL_FILE


### RUN
print_lock = threading.Lock()
pid = os.getpid()
##init server
host = ""
port = 12346
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))

#ON FIRST CONNECTION, TRANSMIT PID
print("Waiting for first connexion to give pid")
s.listen(5)
c, addr = s.accept()
print_lock.acquire()
data = c.recv(1024)
print_lock.release()
c.send(str(pid).encode('utf8'))
c.close()

for root,dir,files in os.walk(location_dir):
    for file in files :
        ##put server in listening mode
        s.listen(5)
        print("socket is listening")
        c, addr = s.accept()
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        data = c.recv(1024)
        print('Message received from socket : {}'.format(data.decode('utf8')))
        print(f'###### file : {file}')

        ##init config
        config_M49.LOG_CSV_FILE = log_csv_file
        config_M49.LOG_FILE = log_file
        config_M49.URL_FILE = url_file
        modify_config(config_M49,file)

        #server-socket dynamic
        print_lock.release()
        c.send(str(f"Feeding {file} to scraper ").encode('utf8'))
        c.close()
        scraper = Scraper(config_M49,s,print_lock)
        scraper.run_scrape()

s.close()
