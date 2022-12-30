import multiprocessing as mp
from multiprocessing.managers import SharedMemoryManager
import time
import json
import os

def funct():
    while True:
        print("funct still running")
        #shared_list.buf
        time.sleep(1)
        
        
def funct2():
    while True: 
        print("funct2 still running")
        #print(len(shared_list))
        time.sleep(1)

def write_list(list):
    with open('Raspberry/save.json', 'w') as fp:
        json.dump(list, fp)
        print("saving done")

def read_list():
    with open('Raspberry/save.json', 'rb') as fp:
        list = json.load(fp)
        return list 
   
if __name__ == "__main__":
    #smm = SharedMemoryManager()
    #smm.start()
    #shared_list = smm.ShareableList('shared_list')
    proc_funct1 = mp.Process(target=funct)
    proc_funct2 = mp.Process(target=funct2)
    #proc_funct1.start()
    #proc_funct2.start()
    
    shared_playlist = read_list()
    for i in shared_playlist:
        os.remove(i)
    print("finished")
    time.sleep(4)
    shared_playlist = read_list()
    print(shared_playlist)
    new_sl = []
    write_list(new_sl)
    print(str(read_list))
    