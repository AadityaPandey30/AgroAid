# Import necessary libraries
import cv2
import time
from datetime import datetime
import pandas as pd
import winsound


def play_buzzer():
    frequency = 2000  # Set frequency (2500 Hz)
    duration = 500  # Set duration (1000 ms = 1 second)
    winsound.Beep(frequency, duration)

first_frame = None;
status_list=[None, None]
times = []
df = pd.DataFrame(columns=["Start", "End"])

video = cv2.VideoCapture(0)

while True:
    check, frame = video.read() # this rads the very first frame of the video
    status = 0
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray,(21,21),0)
    
    if first_frame is None:
        first_frame = gray
        continue
        
    delta_frame = cv2.absdiff(first_frame, gray)
    
    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2) # Remove black holes from weaker white areas
    
    (cnts,_) = cv2.findContours(thresh_frame.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        status = 1
        play_buzzer()  # Call the function to play the buzzer sound
        (x,y,w,h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 3)
        
    status_list.append(status)
    status_list = status_list[-2:]
                                
    if status_list[-1] == 1 and status_list[-2]==0:
        times.append(datetime.now())
    if status_list[-1] == 0 and status_list[-2]==1:
        times.append(datetime.now())
        
    cv2.imshow("Gray Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        if status==1:
            times.append(datetime.now())
        break
        
# print(status_list)
# print(times)

for i in range(0,len(times)-1,2):
    df = df.append({"Start":times[i],"End":times[i+1]},ignore_index=True)
    
df.to_csv("Times.csv")
        
video.release()
cv2.destroyAllWindows()

print(df)