from flask import g,Blueprint
from contextlib import nullcontext
from pymysql import cursors, connect
import pymysql
import bcrypt
import pandas as pd
def init_db():

    db = connect(host='127.0.0.1', user='root', password='root', db='mydb', charset='utf8',cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()   #커서
   
    with db.cursor() as cursor: #DB가 없으면 만들어라.
        sql = "CREATE DATABASE IF NOT EXISTS mydb "
        cursor.execute(sql)
    db.commit()

    db.select_db('mydb')
    
    with db.cursor() as cursor: #DB가 없으면 만들어라.
        sql1= "CREATE TABLE IF NOT EXISTS mydb.`uploadfile` (`filenumber` int(100) NOT NULL AUTO_INCREMENT, `filename` VARCHAR(100) NOT NULL, `filetype` VARCHAR(100) NOT NULL ,`file_show` INT(100),PRIMARY KEY (`filenumber`))"

        cursor.execute(sql1)   

    db.commit
    db.close

def get_db(): #이거 개중요
    if 'db' not in g:     # 플라스크의 전역변수 g 속에 db 가 없으면
        g.db = connect(host='127.0.0.1', user='root', password='root', db='mydb', charset="utf8mb4", cursorclass=pymysql.cursors.DictCursor)
        # 내꺼 db에 접속.

def close_db(): #db 연결 종료
    db=g.pop('db',None) #db라는 거를 팝.
    if db is not None: #팝 한게 비어있지 않으면
        if db.open: #db가 열려있으면
            db.close() #종료해라


#파일 이름, 파일 타입, 입력하기
def add_file(db, filename, filetype):
    with db.cursor() as cursor:
        sql = "insert into mydb.uploadfile values(NULL,%s, %s,0)"
        data = (filename, filetype) 
        cursor.execute(sql, data)
    db.commit()

#조회수 업데이트하기
def add_show(db,file_show,filename):
    with db.cursor() as cursor:
        sql="update uploadfile set  files_show=%s where filename_id=%s"
        data=(file_show,filename)
        cursor.execute(sql,data)
    db.commit()