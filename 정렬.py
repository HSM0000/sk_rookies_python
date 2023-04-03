from flask import Flask, render_template, request, send_file
import os
import zipfile
import datetime

app = Flask(__name__)

@app.route("/")
def list():
    upload_dir = "uploads"
    files = []
    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    return render_template("list.html",files=files)

@app.route("/compress", methods=["POST"])
def compress():
    uploads_dir="uploads"
    files = request.form.getlist("files")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_path = os.path.join(uploads_dir, f"compressed_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for file in files:
            file_path =os.path.join(uploads_dir, file)
            zip_file.write(file_path,file)
    return render_template("list.html",compressed_file=f"compressed_{timestamp}.zip")

@app.route("/download")
def download():
    uploads_dir="uploads"
    compressed_file=request.args.get("file")
    zip_path = os.path.join(uploads_dir, compressed_file)
    return send_file(zip_path, as_attachment=True)

#---------------------------------여기서 부터 추가--------------------------------

#조회순 생각중
#뭔가 날로먹은 느낌이...

#최신순 정렬
@app.route("/list_latest_time")
def list_time():
    upload_dir = "uploads"
    files = []
    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    files=sorted(files, key=lambda x:x[2], reverse=True)
    return render_template("list.html",files=files)

#과거순 정렬
@app.route("/list_old_time")
def list_old_time():
    upload_dir = "uploads"
    files = []
    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    files=sorted(files, key=lambda x:x[2])
    return render_template("list.html",files=files)

#파일 크기가 큰 것 부터 정렬
@app.route("/list_bigsize")
def list_bigsize():
    upload_dir = "uploads"
    files = []
    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    files=sorted(files, key=lambda x:x[1], reverse=True)
    return render_template("list.html",files=files)

#파일 크기가 작은 것 부터 정렬
@app.route("/list_smallsize")
def list_smallsize():
    upload_dir = "uploads"
    files = []
    for file in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    files=sorted(files, key=lambda x:x[1])
    return render_template("list.html",files=files)

#----------------------------여기까지 추가--------------------------------


if __name__ == '__main__':
    app.run(debug=True)