import cv2
import numpy as np
import mediapipe as mp
import time

class handTracker():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5,modelComplexity=1,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        
    def handsFinder(self,image,draw=True):
        imageRGB = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)
        return image

    def positionFinder(self,image, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hand.landmark):
                h,w,c = image.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                lmlist.append([id,cx,cy])
            if draw:
                cv2.circle(image,(cx,cy), 15 , (255,0,255), cv2.FILLED)

        return lmlist

    def grab(self, lmList,ballx,bally):
        fingers = [4,8,12,16,20]
        for i in fingers:
            if not (lmList[i][1] >= ballx-95 and lmList[i][1] <=ballx+95 and lmList[i][2] >=bally-95 and lmList[i][2] <=bally+95):
                return False
        return True

def main():
    cap = cv2.VideoCapture(0)
    tracker = handTracker()
    ballx = 80
    bally = 80
    prevx = 80
    prevy = 80
    ballspeedx = 0
    ballspeedy = 0
    blue = (255,0,0)
    green = (0,255,0)
    color = blue
    font = cv2.FONT_HERSHEY_SIMPLEX  
    move = False
    while True:
        success,image = cap.read()
        image = tracker.handsFinder(image)
        lmList = tracker.positionFinder(image)
        color = blue
        if len(lmList) != 0:
            if tracker.grab(lmList, ballx, bally):
                move=False
                prevx = ballx
                prevy = bally
                ballx = int((lmList[3][1] + lmList[17][1])/2)
                bally = lmList[12][2]+60
                color = green
                ballspeedx = (ballx-prevx)*2
                ballspeedy = (bally-prevy)*2
                print(str((ballspeedx**2+ballspeedy**2)**0.5))
            # if ((ballspeedx**2+ballspeedy**2)**0.5) >= 56:
            #     ballx += ballspeedx
            #     bally += ballspeedy
            else:
                move =True
            print(lmList[4])
        if move:
            ballx += ballspeedx
            bally += ballspeedy
        if ballspeedx !=0:
            ballspeedx = int(ballspeedx/1.2)
        if ballspeedy !=0:
            ballspeedy = int(ballspeedy/1.2)
        if ballspeedx and ballspeedy ==0:
            move = False
        cv2.circle(image,(ballx,bally), 55, color, 3)
        cv2.circle(image,(500,500),100,(0,0,255), 3)
        if ballx > 400 and ballx < 600 and bally >400:
            cv2.putText(image, "YOU WIN!!!", (40,250),font, 3, blue)
       
        cv2.imshow("Video",image)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()