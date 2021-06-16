from flask import Flask, render_template, request, jsonify
import mysql.connector
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.resource(
    service_name = 's3',
    aws_access_key_id = os.getenv('awsKeyId'),
    aws_secret_access_key = os.getenv('awsKey'),
    )

mydb = mysql.connector.connect(
    user=os.getenv('sqlUser'),
    password=os.getenv('sqlPassword'),
    host=os.getenv('sqlHost'),
    database=os.getenv('sqlDatabase')
    )


mycursor = mydb.cursor(buffered=True)

app = Flask(__name__)


@app.route('/api/') 
def index():     
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():

    uploadFile = request.files['selectFile']
    fileName = request.files['selectFile'].filename
    fileContent = request.form.get('fileDescription')
    # print('static/img/' + test.filename)

    s3.Bucket('t3-upload-bucket').put_object(ACL= 'public-read', Key=uploadFile.filename, Body=uploadFile)
    # uploadFile.save('static/img/' + uploadFile.filename)

    mycursor.execute("INSERT INTO updateTable (name, content) VALUES (%s, %s)", (fileName, fileContent))
    mydb.commit()

    return jsonify({
        "imageFile": 'http://dqgc5yp61yvd.cloudfront.net/'+ uploadFile.filename,
        "description": fileContent
    })

@app.route('/api/loading', methods=["GET"])
def loading():
    mycursor.execute("Select * FROM updateTable")
    s3File = mycursor.fetchall()
    # print(s3File)

    loadingInfo = []
    for info in s3File:
        loadingDic = {
            "CFimageName": 'http://dqgc5yp61yvd.cloudfront.net/' + info[1],
            "CFimageContent": info[2]            
        }

        loadingData = loadingDic.copy()
        loadingInfo.append(loadingData)

    return jsonify({
        "allFile": loadingInfo
    })


    
if __name__ == '__main__': 
    app.run(host="0.0.0.0", port = 5500, debug = True) 