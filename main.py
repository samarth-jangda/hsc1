import cv2
import numpy as np
from face_recognition import face_encodings, face_locations, compare_faces, face_distance
import os
from datetime import datetime, date
from keyboard import is_pressed
from flask import Flask, render_template

app = Flask(__name__)
app.config["Secret_Key"] = "6a79852e71abd3dc5e4d#"
#megrun_with_ngrok(app)
app.debug = True
app.secret_key = "AsdHahD12@!#@3@#@#554"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSORD'] = ''
app.config["MYSQL_DB"] = 'register'
app.config["SQLALCHEMY_DATABASE_URL"] = "http://localhost/phpmyadmin/tbl_structure.php?db=register&table=register"
app.config["MYSQL CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            d = date.today()
            f.writelines(f'\n{name},{d},{dtString}')
#This is the database code yahan se data db main jaega

@app.route("/", methods=(["GET", "POST"]))
def index():
    # form = loginform()
    try:
        con = mysql.connection.cursor()
        print("Connected to database")
    except Exception as e:

        sys.exit(e)
    # cur = con.cursor()
    con.execute("SELECT * FROM logins")
    data = DataFrame(data=con.fetchall())

    if request.method == "POST":

        Name = request.form['Name']
        Password = request.form["Password"]

        cur = mysql.connection.cursor()

        if username in list(data[0]):
            if password not in list(data[1]):
                flash("You need to log in")
                return render_template("login.html")

                flash('User already exist')
                return render_template('login.html')
                cur.execute("INSERT INTO logins(username,password,c_password) VALUES (%s,%s,%s)",
                            (username, password, c_password))
                mysql.connection.commit()
                cur.close()
        else:
            flash("Both evoc-id does no match")
            return render_template("login.html", output_data=data)
            # if cur.username != username:
            # flash("you writtern wrong evoc_id")

            flash("Submission-Successful")
            return render_template("login.html")
    return render_template("login.html")


path = 'database_images'


@app.route("/start")
def detect_faces():
    images = []
    classNames = []
    myList = os.listdir(path)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    # print(classNames)
    encodeListKnown = findEncodings(images)
    print('Encoding Complete')
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_locations(imgS)
        encodesCurFrame = face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = compare_faces(encodeListKnown, encodeFace)
            faceDis = face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

        cv2.imshow('Webcam', img)
        if is_pressed("esc"):
            return "Face is scanned"
            exit()
        cv2.waitKey(1)


if __name__ == '__main__':
    # detect_faces()

    app.run()
