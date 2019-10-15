import logging
import threading
import time
import zipfile
import os
import shutil
import codecs
from shutil import copyfile
import threading
import ftplib,sys,getopt 
from threading import Event
import paramiko 
from consolemenu import *
from consolemenu.items import *
import json
import requests
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode



path = "C:/Users/Bogdan/Desktop/facebook/скрипты/файлы/"; 
prelendZip = '/prelend.zip';
lendZip = '/lend.zip'
folder1 = '/1'
blackFolder = '/black'
whiteFolder = '/white'
host = 'bogdanbc.beget.tech'
login = 'bogdanbc'
password = '171297Fe!'
arrOfZips = 1
api_url_base = 'https://api.digitalocean.com/v2/'

folder = os.walk(path)

# идем по папкам рекурсивно и смотрим,есть ли в них файл prelend
def localWork():
    for i in folder:
        
        # Если в папке есть prelend.zip , заходим в неё
        if zipfile.is_zipfile(i[0] + prelendZip):
            
            # если /black не существует,то делаем ее
            if not os.path.exists((str(i[0]) + blackFolder)):
                os.mkdir(str(i[0]) + blackFolder)
                # перемещаем ленд и преленд в /black
                shutil.move(str(i[0]) + lendZip, str(i[0]) + blackFolder)
                shutil.move(str(i[0]) + prelendZip, str(i[0]) + blackFolder)

                # создаем папку 1
                os.mkdir(str(i[0]) + blackFolder + folder1)
                shutil.move(str(i[0]) + blackFolder + lendZip, str(i[0]) + blackFolder + folder1)

                # распаковка преленда 
                z = zipfile.ZipFile(str(i[0]) + blackFolder + prelendZip)    
                z.extractall(str(i[0]) + blackFolder)

                # Распаковка ленда
                z = zipfile.ZipFile(str(i[0]) + blackFolder + folder1 + lendZip)    
                z.extractall(str(i[0]) + blackFolder + folder1)

                # ренейм html в php
                if os.path.exists(str(i[0]) + blackFolder + '/index.html'):
                    os.rename(str(i[0]) + blackFolder + '/index.html', str(i[0]) + blackFolder + '/index.php')

                # в файле index.php преленда прописываем base после header    
                myf = codecs.open( str(i[0]) + blackFolder + '/index.php', 'r' , 'utf-8')
                memo = myf.read()

                ah = codecs.open( str(i[0]) + blackFolder + '/index.php', 'w', 'utf-8') 
                ah.write('<base href=<?php echo "http://" . $_SERVER["SERVER_NAME"] . $_SERVER["REQUEST_URI"] . "black" ?>/>') 
                ah.close()

                myf_new = codecs.open( str(i[0]) + blackFolder + '/index.php', 'a','utf-8')
                myf_new.write(memo)
                myf_new.close()

                # переносим папку index.php в папку
                shutil.copy(os.path.abspath(os.curdir) + '/needFiles/index.php', str(i[0]))

            # если белой папки не существует,то переносим ее               
            if not os.path.exists((str(i[0]) + whiteFolder)):
                # os.mkdir(str(i[0]) + whiteFolder)
                # shutil.
                shutil.copytree(os.path.abspath(os.curdir) + '/needFiles/white', str(i[0]) + whiteFolder)
                
                
                # в файле index.php white  прописываем base после header    
                myfw = codecs.open( str(i[0]) + whiteFolder + '/index.php', 'r' , 'utf-8')
                memoW = myfw.read()

                ahW = codecs.open( str(i[0]) + whiteFolder + '/index.php', 'w', 'utf-8') 
                ahW.write('<base href=<?php echo "http://" . $_SERVER["SERVER_NAME"] . $_SERVER["REQUEST_URI"] . "white" ?>/>') 
                ahW.close()

                myf_new = codecs.open( str(i[0]) + whiteFolder + '/index.php', 'a','utf-8')
                myf_new.write(memoW)
                myf_new.close()

            # архивация
            shutil.make_archive(str(i[0]),'zip',str(i[0]))


# удаляем все папки,оставляем только архивы   
def del_folders():
    folder = os.walk(path)      
    count = 0
    for i in folder:
        count = count + 1
        if count != 1:
            shutil.rmtree(i[0])
    # global arrOfZips 

# auth
def ftpAccess():
    # auth
    ftp = ftplib.FTP(host,login,password) 
    # проверка соединения
    text = ftp.getwelcome()
    print(text,'\n')
    # работа с ftp
    return ftp     

def listOfZips():
    return  [f for f in os.listdir(path) if f.endswith('.zip')]


# Удаление директории на хосте
def delFilesFromDirOnHost(pathToDir):
    ftp = ftpAccess()
    ftp.cwd('/')

    dirsOnHost = apiBeget()

    # i = 0
    # for key, value in dirsOnHost.items():    
    #     print(i, " - " ,key ," | " ,value)
    #     i = i + 1
    
    # print("\n Какую директорию почистить? (Через пробел цифры ввести)>> ")
    # clearDirs = list(map(int,input().split()))

    ftp.cwd(pathToDir)

    print(ftp.pwd())
    ftp.cwd('..')
    # print(ftp.pwd())
    recurse(ftp)
    ftp.mkd('public_html')

    ftp.cwd('/')
    # print(ftp.pwd())

def downLoadFilesFtp():
    os.system('cls')
    listOfCommands = ['Загрузить zip в директорию определенную(все файлы будут удалены,будет добавление в Клоаку)']

    while True:
        # вывод меню
        i = 0
        for listOfCommand in listOfCommands:
            
            print(str(i) + ')' + listOfCommand,'\n')
            i = i+1

        command = input(">>")

        # Удаление файлов в директории
        if command == '0':
            # удаляем файлы в директории
            # delFilesFromDirOnHost()
            # загружаем и разархивируем архив
            downloadToHostAndUnzip()


        else:
            break
        
# загрузка на хост архива,распаковка
def downloadToHostAndUnzip():
    ftp = ftpAccess()
    i = 0 
    arrOfZip = []
    # print(listOfZips())
    for listOfZip in listOfZips():
        print(i,' - ',listOfZip,'\n')
        i = i + 1
        arrOfZip.append(listOfZip)

    # howZip = int(input("какой zip грузим? >>"))

    print("\n какой zip грузим? (Через пробел цифры ввести)>> ")
    howZips = list(map(int,input().split()))

    dirsOnHost = apiBeget()
    i = 0
    for key, value in dirsOnHost.items():    
        print(i, " - " ,key ," | " ,value)
        i = i+1
    
    # howSites = int(input("На какие сайты?(Через пробел) >>"))

    print("\n На какие сайты? Не больше ",len(howZips)," >> ")
    howSites = list(map(int,input().split()))

    # dict(zip([1,2,3,4], [a,b,c,d]))
    zipsAndSites = dict(zip(howSites, howZips))
    print(zipsAndSites)

    # заливка на хост архива и распаковка
    ftp.cwd('/')
    for key, value in zipsAndSites.items():

        # удаляем файлы
        delFilesFromDirOnHost(list(dirsOnHost)[key])

        print("\n Архив ",listOfZips()[value]," переносим в директорию ",list(dirsOnHost)[key]," сайта ", dirsOnHost.get(list(dirsOnHost)[key]))

        # загружаем zip в директорию
        ftp.cwd(str(list(dirsOnHost)[key]))  
        f = open(path + listOfZips()[value] , "rb")
        ftp.storbinary("STOR " + listOfZips()[value], f)
        f.close()
        ftp.cwd('/')

        pathOnHost = list(dirsOnHost)[key]
        pathsOnHost = pathOnHost.split('/')
        
        # распаковка zip в директории
        print("\n Распаковываем его")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=host, username=login, password=password, port=22)
        # print('cd ' + pathsOnHost[0] + ';cd ' + pathsOnHost[1] + ';unzip ' +  listOfZips()[value])
        stdin, stdout, stderr = client.exec_command('cd ' + pathsOnHost[0] + ' ; cd ' + pathsOnHost[1] + ' ;unzip ' +  listOfZips()[value] )
        
        data = stdout.read() + stderr.read()
        # print(data)
        client.close()

        # добавляем в клоаку домен
        cloaka(dirsOnHost.get(list(dirsOnHost)[key]),listOfZips()[value])

        print("\n Готово!") 
        
# возвращает все домены и пути к ним(словарь)
def apiBeget():
    api_url =  'https://api.beget.com/api/site/getList?login='+ login +'&passwd=' + password + '&output_format=json'
    response = requests.get(api_url)

    pathAndDomen = {}
    if response.status_code == 200:
        results = json.loads(response.content)
        
        for result in results["answer"]["result"]:
            i = 0

            if result["path"] and result["domains"]:
                if(result["domains"][i]["fqdn"]) == 'smmsmart.ru.com':
                    # print(result["domains"][i]["fqdn"])
                    continue                
                else:
                    pathAndDomen[result["path"]] = result["domains"][i]["fqdn"]            
            i = i + 1

    else:
        return None

    return pathAndDomen

#1 удаление директорий
def recurse(ftp):
    print (ftp.pwd())
    for d in ftp.nlst():
        try:
            ftp.cwd(d)
            cleanOut(ftp)
            ftp.cwd('..')
            ftp.rmd(d)
        except:
            pass
        else:
            try:
                ftp.cwd(d)
                recurse(ftp)
                ftp.cwd('..')
            except:
                pass # not a directory; ignore

#2 удаление директорий
def cleanOut(ftp):
    print ('cleanout ',ftp.pwd())
    for d in ftp.nlst():
        try:
            ftp.delete(d) # delete the file
            print(d)
        except:
            ftp.cwd(d) # it's actually a directory; clean it
            cleanOut(ftp)
            ftp.cwd('..')
            ftp.rmd(d)

# подключение к БД
def dbKlo():

    # Подключение к БД
    HOST = "bogdanbc.beget.tech"
    PORT = 3306
    USER = "bogdanbc_cloaka"
    PASSWORD = "171297Fe"
    DB = "bogdanbc_cloaka"

    connection = mysql.connector.connect(host=HOST,
                                             database=DB,
                                             user=USER,
                                             password=PASSWORD)
    return connection

# Удаление домена из клоаки
def delKlo():
    connection = dbKlo()

    try:
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)

            cursor = connection.cursor(buffered=True)
            cursor.execute('select domain from domains;')

            arrOfDomains = {}
            records = cursor.fetchall()
            sameDomen = ""
            i = 0
            for record in records:
                if sameDomen == record:
                    continue
                else:
                    print([i]," - ",record[0])
                    arrOfDomains[i] = record[0]
                    i = i + 1
                sameDomen = record

            delDomen = int(input("\n Какой домен удалить? >>"))

            # print
            print(arrOfDomains[delDomen])
            # input()

            cursor.execute("DELETE from domains WHERE domain = '"+ arrOfDomains[delDomen] + "'")
            connection.commit()



    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        print(connection)
        if (connection.is_connected()):
            cursor.close()
            connection.close()
        print("MySQL connection is closed")

# crud для Klo
def crudKlo():
    os.system('cls')


    listOfCommands = ['Удалить домен',
                    'добавить язык в определенный домен',
                    'удалить язык в определенном домене',
                    ]

    while True:
        # вывод меню
        i = 0
        for list in listOfCommands:
            
            print(str(i) + ')' + list,'\n')
            i = i+1

        command = input("Введите цифру >> ")

        # локально с файлами
        if command == '0':
            delKlo()
        elif command == '1':
            print("CRUD Klo")
        elif command == "2":
            print("CRUD Klo")
        else:
            break


# def cloudFlare(domen):


# работа с клоакой
def cloaka(domen,zipFile):
    connection = dbKlo()
    print()
    try:
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            # cursor = connection.cursor()
            cursor = connection.cursor(buffered=True)
            cursor.execute('select code,alpha2,langEN from countries;')

            records = cursor.fetchall()
            for record in records:
                print(record[0],' - ',record[1]," | ",record[2])

            print("Для архива ",zipFile," введите номера языков,которые будут добавлены в клоаку :")
            numLangs = list(map(int,input().split()))
            # print(lang)
            # [0, 4 ,8 ,12, 13]
            langs = []
            for record in records:
                j = 0
                while j != len(numLangs):
                    # print(j)
                    if numLangs[j] == record[0]:
                        langs.append(record[1])
                    j = j+1
            print(langs)


            cursor.execute("SET SESSION wait_timeout = 60")
            cursor.execute("SHOW VARIABLES LIKE 'wait_timeout';")
            

            for lang in langs:
                cursor.execute("INSERT INTO domains(domain,link, white_link,traf,status,country) VALUES ( '" + domen + "', 'black', 'white','1','0','" + lang  + "')")
                connection.commit()

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        print(connection)
        if (connection.is_connected()):
            cursor.close()
            connection.close()
        print("MySQL connection is closed")

def menu():

    os.system('cls')
    listOfCommand = ['работаем локально с файлами на пк',
                    'работа с сервером',
                    'работа с клоакой',
                    'Очистить экран']

    while True:
        # вывод меню
        i = 0
        for list in listOfCommand:
            
            print(str(i) + ')' + list,'\n')
            i = i+1

        command = input(">>")

        # локально с файлами
        if command == '0':
            print("Преобразование файлов ... ")
            localWorkArchive = threading.Thread(target=localWork)
            localWorkArchive.start()
            localWorkArchive.join()

            print("удаление папок ...")
            # del_folder = threading.Thread(target=del_folders)
            # del_folder.start()
            # del_folder.join()

        elif command == '1':

            print("\n Соединяюсь с сервером...\n")
            downLoadFilesFtp()

        elif command == "2":
            crudKlo()
        else:
            break
    # apiBeget()
if __name__ == "__main__":  
    menu = menu()   