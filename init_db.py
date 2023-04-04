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
        sql1= "CREATE TABLE IF NOT EXISTS mydb.`uploadfile` (`filenumber` int(100) NOT NULL AUTO_INCREMENT, `filename` VARCHAR(100) NOT NULL, `filetype` VARCHAR(100) NOT NULL ,`file_show` INT(100),`user_id` VARCHAR(100),`date` TIMESTAMP DEFAULT NOW(),PRIMARY KEY (`filenumber`))"
        sql2= "CREATE TABLE IF NOT EXISTS mydb.`user` (`user_id` VARCHAR(100) NOT NULL,`user_pw` VARCHAR(100) NOT NULL, `name` VARCHAR(100) NOT NULL,PRIMARY KEY (`user_id`) )"
        cursor.execute(sql1)  
        cursor.execute(sql2)   

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
def add_file(db, filename, filetype,user_id):
    with db.cursor() as cursor:
        sql = "insert into mydb.uploadfile values(NULL,%s, %s,0,%s,DEFAULT)"
        data = (filename, filetype,user_id) 
        cursor.execute(sql, data)
    db.commit()

#조회수 업데이트하기
def add_show(db,filename):
    with db.cursor() as cursor:
        sql="update uploadfile set  file_show=file_show+1 where filename=%s"
        data=(filename)
        cursor.execute(sql,data)
    db.commit()

#조회수 가져오기
def search_show(db,filename):
    with db.cursor() as cursor:
        sql="select * from mydb.uploadfile where filename=%s"
        data=(filename)
        cursor.execute(sql,data)
        result = cursor.fetchall()
        return result
#중복 여부 가져오기
def search_file(db,filename):
    with db.cursor() as cursor:
        sql="select filename from mydb.uploadfile where filename=%s"
        data=(filename)
        cursor.execute(sql,data)
        result = cursor.fetchall()
        return result
    
#파일 삭제
def delete_file(db, filename):
    with db.cursor() as cursor:
        sql = "delete from mydb.uploadfile where filename=%s"
        data = (filename)
        cursor.execute(sql, data)
        db.commit()
#파일 가져오기
def find_file(db,filename):
    with db.cursor() as cursor:
        sql="select * from mydb.uploadfile where filename=%s"
        data=(filename)
        cursor.execute(sql,data)
        result = cursor.fetchall()
        return result
    
#아이디 찾기
def find_user(db, user_id):
    with db.cursor() as cursor:
        sql= "select user_id from mydb.user where user_id=%s"
        cursor.execute(sql, user_id)
        result = cursor.fetchall()
        #db에 id가 존재함
        return result    

def find_name(db, user_id):
    with db.cursor() as cursor:
        sql= "select name from mydb.user where user_id=%s"
        cursor.execute(sql, user_id)
        result = cursor.fetchall()
        #db에 id가 존재함
        return result    
    
#admin id로 pw 찾아서 db와 비교후 반환 반환 값 true 또는 false
def get_login(db,user_id, user_pw):
    with db.cursor() as cursor:
        sql = "select user_pw from mydb.user where user_id=%s"
        data = (user_id) 
        cursor.execute(sql, data)
        db_password = cursor.fetchone() #db에 저장되어있는 비밀번호    
        bytes_db_password=db_password['user_pw'].encode('utf-8')
        bytes_admin_password=user_pw.encode('utf-8')
        
        result = bcrypt.checkpw(bytes_admin_password ,bytes_db_password )           
    return result    #일치하면 true 반환

#admin 계정 추가
def add_user(db, admin_id, admin_pw,name):
    with db.cursor() as cursor:

        if (find_user(db,admin_id)):        #db에 이미 계정이 존재하면
            return 
        else:
            encode_pw=admin_pw.encode('utf-8') #bytes 타입 변환
            salt = bcrypt.gensalt()
            hashed_pw=bcrypt.hashpw(encode_pw, salt) #해쉬키로 암호화
            decode_pw = hashed_pw.decode()   #db에 저장하기 전 unicode로 타입 변환
            sql = "insert into mydb.user values(%s, %s, %s)"
            data = (admin_id, decode_pw, name) 
            cursor.execute(sql, data)
            db.commit()