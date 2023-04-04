from flask import Flask, render_template, request, send_file,g,redirect,session
from init_db import init_db,get_db,close_db,add_file,search_show,search_file,add_show,delete_file,find_file,get_login,add_user,find_user,find_name
import os
import zipfile
from datetime import datetime
import datetime
import random


app = Flask(__name__)
app.secret_key="@!$qefq34@$1234wefQA#$233ASEDFs"

init_db()
@app.route('/',methods=['GET','POST'])
def login():
    if request.method =='GET' :
        return render_template("login.html")
    else:
        user_id=request.form['login_id']
        user_password=request.form['login_pw']
        if not (user_id and user_password) : #둘중 하나라도 입력 안되면
            return "<script type='text/javascript'>alert('모두 입력해주세요.');document.location.href='/';</script>" 
        find_id=find_user(g.db,user_id)    #db에서 관리자 아이디 가져오기
        #db에서 아이디와 비밀번호로 정보 가져오기
    
        if (find_id) : #정보가 존재하면
            if(get_login(g.db, user_id, user_password)):  #true 혹은 false
                session['user_id']=user_id
                return redirect("/index")   #관리자 메인 페이지 이동
            else : 
                return "<script type='text/javascript'>alert('아이디나 비밀번호가 틀립니다.');document.location.href='/';</script>"
        else : #정보가 존재하지 않으면 
            return "<script type='text/javascript'>alert('아이디나 비밀번호가 틀립니다.');document.location.href='/';</script>"


@app.route("/logout")
def logout():
    session.pop('user_id',None)
    return redirect("/")

@app.route("/join",methods=['GET','POST'])
def join():
    if request.method=='GET':
        return render_template("join.html")
    else:
        user_line=request.form['login_id']
        user_admin=request.form['login_pw']
        nickname=request.form['name']
        if not (user_line and user_admin and nickname) : 
            return "<script type='text/javascript'>alert('모두 입력해주세요.');document.location.href='/join';</script>" 
        

        add_user(g.db, user_line, user_admin, nickname)
        return "<script type='text/javascript'>alert('가입 완료');document.location.href='/';</script>"

#맨 처음 페이지 이때 지금까지의 uploads파일에 있는거 보여주기
@app.route('/index')
def index():
    uploads_dir = "uploads"
    files = []
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            ctime = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%d-%m-%y %H:%M') 
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%y %H:%M')
            file_show=search_show(g.db,file)
            if (file_show):
                name=find_name(g.db,file_show[0]['user_id'])
                file_show=file_show[0]["file_show"]
                name=name[0]['name']
            else:
                file_show=0
                name='없음'
            files.append((file, os.path.getsize(file_path), ctime,mtime,file_show,name))
    return render_template("list_result.html", files=files)

@app.route('/upload', methods=["POST"])
def upload():
    file = request.files["file"]
    file.save(os.path.join("uploads", file.filename))
    
    file_type = file.content_type
    #파일 이름,파일,파일 타입 넣기
    search=search_file(g.db,file.filename)
    print(search)
    if search==():
        add_file(g.db,file.filename,file_type,session['user_id'])
    elif search[0]["filename"]==file.filename:
        return "<script type='text/javascript'>alert('파일이 있습니다');document.location.href='/';</script>" 

    return redirect("/index")


@app.route("/compress", methods=["POST"])
def compress():
    uploads_dir = "uploads"
    files = request.form.getlist("files")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    random_number=random.random()
    zip_path = os.path.join(uploads_dir, f"{random_number}compressed_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            zip_file.write(file_path, file)

    #compressed_file = f"compressed_{timestamp}.zip"
    compressed_file = os.path.basename(zip_path)
    add_file(g.db,compressed_file,zip,session['user_id'])

    return render_template("list_result.html", compressed_file=compressed_file)


@app.route("/delete", methods=["POST"])
def delete():
    uploads_dir = "uploads"
    file_name = request.form.get("file")
    file_path = os.path.join(uploads_dir, file_name)
    delete_file(g.db,file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        return "File deleted successfully."
    else:
        return "File not found."
    
@app.route('/delete_all',methods=['POST'])
def delete_all():
    uploads_dir = "uploads"
    files = []
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        delete_file(g.db,file)
        if os.path.exists(file_path):
            os.remove(file_path)
    return "삭제완료"
#

@app.route("/download")
def download():
    uploads_dir = "uploads"
    compressed_file = request.args.get("file")
    add=add_show(g.db,compressed_file)
    zip_path = os.path.join(uploads_dir, compressed_file)
    return send_file(zip_path, as_attachment=True)

@app.route("/searchfile", methods=['POST'])
def searchfile():
    uploads_dir = "uploads"
    search=request.form['search']
    print(search)
    if not (search):
        return redirect("/index")
           
    find_filename = find_file(g.db, search)
  
    if (find_filename) : #정보가 존재하면
        files=[]
        for file in os.listdir(uploads_dir):
            file_path = os.path.join(uploads_dir, file)
            if os.path.isfile(file_path):
                ctime = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%d-%m-%y %H:%M') 
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%y %H:%M')
                file_show=search_show(g.db,file)
                if (file_show):
                    file_show=file_show[0]["file_show"]
                else:
                    file_show=0
                if file==find_filename[0]['filename']:
                    files.append((file, os.path.getsize(file_path), ctime,mtime,file_show,session['user_id']))
        return render_template('list_result.html',files=files)   
    else : #정보가 존재하지 않으면 
        return "<script type='text/javascript'>alert('파일이 없습니다');document.location.href='/index';</script>"

@app.before_request # 요청이 오기 직전에 db 연결
def before_request():
    get_db()

@app.teardown_request # 요청이 끝난 직후에 db 연결 해제
def teardown_request(exception):
    close_db()

if __name__ == '__main__':
    app.run(debug=True)