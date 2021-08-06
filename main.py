import cv2
from flask import Flask, render_template,request,redirect, url_for, send_from_directory,session
from process_img import gen_ans
from werkzeug import secure_filename
import pandas as pd
import csv
import os
from flask_session import Session
USERNAME ="admin"
PASSWORD ="admin"
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.getenv("SECRET", "not a secret")

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg','csv'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
@app.route('/', methods=['GET', 'POST'])
def start():
    session['plt']=[]
    session['dapan']=""
    return redirect('/main')
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template("main.html")
@app.route('/bridge',methods=['GET','POST'])
def bridge():
    if request.method=="POST":
        # print(request.form['check'])
        if request.form['check']=="start":
            return redirect('/chamthi')
        elif request.form['check']=="save":
            return redirect('/download')
        elif request.form['check']=="csv":
            return redirect('/dapan')
        elif request.form['check']=="res":
            return redirect('/dashboard')
        elif request.form['check']=="back":
            return redirect('/main')
        else:
            return redirect('/main')
    else:
        return redirect('/')
@app.route('/chamthi',methods=['GET', 'POST'])
def index():
    return render_template('point.html')

    # else:
    #     return redirect('/')
@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html',lres=session['kq'],lans=get_list())
def get_list():
    # session['db'] = []
    df = pd.read_csv('./uploads/dapan.csv')
    # session['db']=df['Answer']
    # session['ques']= df['Question']
    return df['Answer']



@app.route('/dapan',methods =['GET','POST'])
def dapan():
    return render_template('dapan.html')
@app.route('/upload_ans', methods=['POST'])
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_files',
                                filename=filename))
@app.route('/upload_ans/<filename>')
def uploaded_files(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    # df = pd.read_csv("ketqua.csv")
    TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2)]
    for image_path in TEST_IMAGE_PATHS:
        session['dapan'] = image_path
        print(session['dapan'])
    return redirect('/main')

@app.route('/upload', methods=['POST'])
def uploads():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file',
                                filename=filename))
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    PATH_TO_TEST_IMAGES_DIR = app.config['UPLOAD_FOLDER']
    # df = pd.read_csv("ketqua.csv")
    TEST_IMAGE_PATHS = [os.path.join(PATH_TO_TEST_IMAGES_DIR,filename.format(i)) for i in range(1, 2)]
    session['point'] = []
    for image_path in TEST_IMAGE_PATHS:
        score,res = gen_ans(session['dapan'],image_path)
        dfp = pd.DataFrame(res)    
        dfp.to_csv('{}.csv'.format(image_path))
        dd="{}.csv".format(image_path)
        session['point'].append([image_path+'.csv',score])
        session['kq']= res
        session['plt'].append(score)      
    session['filesave']=dd
    with open('../db/result.csv', 'a') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(session['point'])
        f_object.close()  
    session['point']=[]
    return redirect('/chamthi')
@app.route('/download',methods=['GET'])
def download_file():
    return render_template('download.html',value=session['filesave'])
app.run(host = '0.0.0.0',port = 1024)
