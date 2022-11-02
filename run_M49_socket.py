# Import socket module
import socket
import time
import psutil
import os,subprocess


pid = os.getpid()

'''
Launches the server side with hardcoded path. Change the hardcoded path to run it in
your environment.
'''
def run_server():
    cmd_line = 'python D:\\workspace\\THESIS\\GDS\\scraper_production\\run_M49_server.py'
    p = subprocess.Popen(cmd_line, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(" Waiting 15 secs to let server connect ... ")
    time.sleep(15)
    return p

'''
Gets the pid of the server, to intialize things.
'''
def get_serv_pid():
    ## to be executed after each serv reboot
    host = '127.0.0.1'
    port = 12346
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((host,port))
    message = "hello"
    s.send(message.encode('utf8'))
    data = s.recv(1024)
    serv_pid = int(data.decode('utf8'))
    s.close()
    return serv_pid

'''
initialize connection between sockets and server
'''
def init_connection():
    p = run_server()
    serv_pid = get_serv_pid()
    k=0
    return serv_pid,k, p

'''
Runs the socket-server dynamic.
'''
def Main():
    serv_pid,k, p=init_connection()
    print(f" GOT server ID : {serv_pid} -  now advancing into main loop")
    while True:
        # local host IP '127.0.0.1'
        host = '127.0.0.1'

        # Define the port on which you want to connect
        port = 12346

        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(2000)
        # connect to server on local computer
        s.connect((host,port))

        # message you send to server - simple runs checks
        message = f"This is message numero {k}"

        # message sent to server
        s.send(message.encode('utf8'))

        try :
            # message received from server
            data = s.recv(1024)
            print("Serveur pid : {}  ; socket pid : {} ; message {}".format(serv_pid,pid,k))
        except socket.timeout :
            print(" caught timeout error")
            print(" Terminating server process : {}".format(serv_pid))
            p_serv = psutil.Process(serv_pid)
            p_serv.kill()
            print("Launching server")
            time.sleep(15)
            serv_pid,k, p = init_connection()
            continue
        k+=1
        # print the received message
        print('Received from the server :',str(data.decode('utf8')))

        # close the connection
        s.close()
        time.sleep(5)


if __name__ == '__main__':
    Main()
