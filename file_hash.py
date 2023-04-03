from flask import Flask, render_template, request, send_file,g
from init_db import init_db,get_db,close_db,add_file
import os
import zipfile
from datetime import datetime
app = Flask(__name__)

init_db()
count=0
@app.route('/')
def index():
    return render_template("upload.html")
@app.route('/upload', methods=["POST"])
def upload():
    file = request.files["file"]
    file.save(os.path.join("uploads", file.filename))
    
    file_type = file.content_type
    #파일 이름,파일,파일 타입 넣기
    add_file(g.db,file.filename,file_type)

    # 파일 생성 시간과 접근 시간을 확인
    file_ctime = datetime.fromtimestamp(os.path.getctime(os.path.join("uploads", file.filename)))
    file_atime = datetime.fromtimestamp(os.path.getatime(os.path.join("uploads", file.filename)))

    return render_template("result.html", file_name=file.filename, file_type=file_type,
                           file_ctime=file_ctime, file_atime=file_atime)

@app.before_request # 요청이 오기 직전에 db 연결
def before_request():
    get_db()

@app.teardown_request # 요청이 끝난 직후에 db 연결 해제
def teardown_request(exception):
    close_db()

if __name__ == '__main__':
    app.run(debug=True)