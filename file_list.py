from flask import Flask, render_template, request, send_file
import os
import zipfile
import datetime

app = Flask(__name__)

@app.route("/")
def list():
    uploads_dir = "uploads"
    files = []
    for file in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, file)
        if os.path.isfile(file_path):
            files.append((file, os.path.getsize(file_path),os.path.getctime(file_path)))
    return render_template("list.html", files=files)

@app.route("/compress", methods=["POST"])
def compress():
    uploads_dir = "uploads"
    files = request.form.getlist("files")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    zip_path = os.path.join(uploads_dir, f"compressed_{timestamp}.zip")
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            zip_file.write(file_path, file)

    #compressed_file = f"compressed_{timestamp}.zip"
    compressed_file = os.path.basename(zip_path)

    return render_template("list.html", compressed_file=compressed_file)

@app.route("/download")
def download():
    uploads_dir = "uploads"
    compressed_file = request.args.get("file")
    zip_path = os.path.join(uploads_dir, compressed_file)
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)