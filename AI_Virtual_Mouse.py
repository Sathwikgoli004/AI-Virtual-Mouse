import cv2
import time
import math
import handtrackingmodule as htm
import numpy as np
import pyautogui
import cvzone

from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480
frameR = 100
smoothening = 5
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(detectionCon=0.60,maxHands=1)
wScr, hScr = pyautogui.size()

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0


while True:
    
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    
    if len(lmList) != 0:
        x1,y1 = lmList[8][1:]
        x2,y2 = lmList[12][1:]
        

        
        fingers = detector.fingersUp()
    
        
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),(255, 0, 255), 2)
        
        
        if fingers[1] == 1 and fingers[2] == 0:
            
            
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            
            
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            
            
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

         
        if fingers[4] == 1 and fingers[3] == 0 and fingers[2] == 0 and fingers[1] == 0 and fingers[0] == 1:
            x1,y1 = lmList[4][1], lmList[4][2]
            x2,y2 = lmList[20][1], lmList[20][2]
            cx,cy = (x1+x2)//2 , (y1+y2)//2
            cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)
            cv2.circle(img,(x2,y2),15,(255,0,255),cv2.FILLED)
            cv2.line(img,(x1,y1),(x2,y2),(2555,0,255),3)
            cv2.circle(img,(cx,cy),15,(255,0,255),cv2.FILLED)
            length2 =math.hypot(x2-x1,y2-y1)
            #print(length2)
            vol = np.interp(length2,[133,265],[minVol, maxVol])
            volBar = np.interp(length2,[133,265], [400,150])
            volPer = np.interp(length2,[133,265], [0,100])
            #print(int(length2), vol)
            volume.SetMasterVolumeLevel(vol, None)

            if length2 < 133:
                    cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
            
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                1, (0,255, 0), 3)


        
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3    ] == 0 and fingers[4] == 0:    
            
            
            length3, img, lineInfo_1 = detector.findDistance(8, 4, img)
            #print(length3)

            
            if length3 < 70:
                cv2.circle(img, (lineInfo_1[4], lineInfo_1[5]),15, (0, 255, 0), cv2.FILLED)
                pyautogui.rightClick()



        
        if fingers[1] == 1 and fingers[2] == 1:    
            
            
            length, img, lineInfo = detector.findDistance(8, 12, img)
            #print(length)

            
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]),15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()

        
        if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            pyautogui.screenshot('ScreenShot.png')
    
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 0), 3)
   
    
    cv2.imshow("Image", img)
    cv2.waitKey(1)