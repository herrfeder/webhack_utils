import pip
import os
import requests
import tarfile

pos = "[+]"
neg = "[-]"
inf = "[*]"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def checkfile(string):

    dire = os.listdir(".")
    for line in [x.lower() for x in dire]:
        if os.path.isfile(string.lower()):
            return True
    return False

def check_phantomJS(exprint):
    dire = os.listdir(".")
    if checkfile("phantomjs"):
        exprint(pos,"PhantomJS")
    else:
        exprint(neg,"PhantomJS")
        url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_size = int(response.headers['Content-Length'])
            with open('phantomjs.tar.bz2', 'wb') as f:
                down_size = 0
                for chunk in response.iter_content(1024):
                    down_size += 1024
                    os.system("printf "+"'"+ "Downloading "+str(down_size)+"/"+str(file_size)+"'")
                    os.system("printf '\r'")
                    f.write(chunk)
            tar = tarfile.open("phantomjs.tar.bz2", "r:bz2")
            tar.extractall()
            tar.close()
            os.system("cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs .")
            exprint(pos,"PhantomJS")
            if checkfile("phantomjs"):
                exprint(pos,"PhantomJS")

def check_pip(exprint,package):
    try:
        __import__(selenium)
        exprint(pos,package)
    except NameError:
        exprint(neg,package)
        pip.main(['install', package])
        exprint(pos,package)

def existence_print(status,package):
    if status == neg:
        print bcolors.WARNING + neg + bcolors.ENDC +" "+package
    if status == pos:
        print bcolors.OKGREEN + pos + bcolors.ENDC +" "+package
    if status == inf:
        print bcolors.OKBLUE + inf + bcolors.ENDC +" "+package

if __name__ == "__main__":

    print "You need to meet a few prequisities to use this framework"
    check_pip(existence_print,"Selenium")
    check_pip(existence_print,"BeautifulSoup")
    check_phantomJS(existence_print)

