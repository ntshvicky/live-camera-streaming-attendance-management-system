#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
import numpy as np 
import sqlite3
import os
from datetime import datetime
import concurrent.futures
import threading
import pyaudio

import speech_recognition as sr

#Initialize the Flask app
app = Flask(__name__,static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\def]/'

lock = threading.Lock()

audio1 = pyaudio.PyAudio()

'''
for ip camera use - rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' 
for local webcam use cv2.VideoCapture(0)
'''
camera = cv2.VideoCapture(0)

def gen_frames():
    
    fname = "trainingData.yml"
    if not os.path.isfile(fname):
        print("Please train the data first")
        exit(0)

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(fname)
    while True:
        success, frame = camera.read()  # read the camera frame

        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url  = {executor.submit(create_frame, recognizer, gray, frame, x,y,w,h): (x,y,w,h) for x,y,w,h in faces}
                for future in concurrent.futures.as_completed(future_to_url):
                    future.result()

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def create_frame(recognizer, gray, frame, x,y,w,h):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    c = conn.cursor()
    w1 = x+w
    h1 = y+h
    color = (0,255,255)
    #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
    ids,conf = recognizer.predict(gray[y:y+h,x:x+w])
    lock.acquire(True)
    createAtt = True
    c.execute("select name from users where id = (?);", (ids,))
    result = c.fetchall()
    c.close()
    c = conn.cursor()
    c.execute("select attendance_date from attendance where user_id = (?);", (ids,))
    att_result = c.fetchall()
    c.close()
    att_date = "Not Attended"
    if len(att_result)>0:
        if datetime.strptime(att_result[0][0], '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d"):
            createAtt = False
            att_date = att_result[0][0]
        else:
            createAtt = True
    else:
        createAtt = True

    name = result[0][0] + "\n" + "{:.2f}".format(conf) + "%" + "\nAttendance: " + "{}".format(att_date) + ""
    y0, dy = y, 40
    if conf < 60:
        for i, line in enumerate(name.split('\n')):
            y1 = y0 + i*dy
            cv2.putText(frame, line, (x+w+5,y1+25), cv2.FONT_HERSHEY_SIMPLEX, 1, (150,255,0),2)
            if createAtt == True:
                conn2 = sqlite3.connect('database.db', check_same_thread=False)
                c2 = conn2.cursor()
                c2.execute('INSERT INTO attendance (user_id) VALUES (?)', (ids,))
                conn2.commit()
                conn2.close()
                createAtt = False
    else:
        color = (0,0,255)
        cv2.putText(frame, 'No Match', (x+w+5,y+25), cv2.FONT_HERSHEY_SIMPLEX, 1, color,2)
        
    create_rectangle(frame,x,y,w1,h1, color, 5, 25)
    create_rectangle(frame,x+10,y+10,w1-10,h1-10, color, 2, 15)
    lock.release()
    conn.close()
    return frame

def create_rectangle(img,x,y,w,h,color=(0,255,255),thickness=1, distance=25):
    #################### Top - starting to below ############
    start_point = (x,y)
    end_point = (x, (y+distance))
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### Top - starting to right ############
    start_point = (x,y)
    end_point = ((x+distance),y)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### Top - end to left ############
    start_point = (w,y)
    end_point = (w-distance,y)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### Top - end to below ############
    start_point = (w,y)
    end_point = (w,y+distance)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### bottom - end to up ############
    start_point = (w,h)
    end_point = (w,h-distance)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### bottom - end to left ############
    start_point = (w,h)
    end_point = (w-distance,h)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### bottom - start to right ############
    start_point = (x,h)
    end_point = (x+distance,h)
    img = cv2.line(img, start_point, end_point, color, thickness)
    #################### bottom - start to up ############
    start_point = (x,h)
    end_point = (x,h-distance)
    img = cv2.line(img, start_point, end_point, color, thickness)
    return img



# custom function to update jinja template 
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv

#genenrator function to read data from database
def test_stream_gen():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            yield r.recognize_google(audio)
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/audio_feed')
def audio_feed():
    return Response(test_stream_gen(), mimetype='text')

if __name__ == "__main__":
    app.run(debug=True, port=5000)