from flask import Flask, render_template, request, send_file,g,redirect
from init_db import init_db,get_db,close_db,add_file,search_show,search_file,add_show,delete_file
import os
import zipfile
from datetime import datetime
import datetime
import random
app = Flask(__name__)

init_db()

#맨 처음 페이지 이때 지금까지의 uploads파일에 있는거 보여주기
@app.route('/')
def index():
    uploads_dir = "uploads"
    files = []
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            ctime = datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%d-%m-%y %H:%M') 
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d-%m-%y %H:%M')
            file_show=search_show(g.db,file)
            file_show=file_show[0]["file_show"]
            files.append((file, os.path.getsize(file_path), ctime,mtime,file_show))
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
        add_file(g.db,file.filename,file_type)
    elif search[0]["filename"]==file.filename:
        return "<script type='text/javascript'>alert('파일이 있습니다');document.location.href='/';</script>" 

    return redirect("/")

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
    add_file(g.db,compressed_file,zip)

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
#
@app.route("/download")
def download():
    uploads_dir = "uploads"
    compressed_file = request.args.get("file")
    add=add_show(g.db,compressed_file)
    zip_path = os.path.join(uploads_dir, compressed_file)
    return send_file(zip_path, as_attachment=True)

@app.before_request # 요청이 오기 직전에 db 연결
def before_request():
    get_db()

@app.teardown_request # 요청이 끝난 직후에 db 연결 해제
def teardown_request(exception):
    close_db()

if __name__ == '__main__':
    app.run(debug=True)