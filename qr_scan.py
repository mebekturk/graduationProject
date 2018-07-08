from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import RPi.GPIO as GPIO
import time

IRTrackingPin_Right = 11
IRTrackingPin_Left = 13

Motor1A = 16
Motor1B = 18
Motor1E = 22

Motor2A = 29
Motor2B = 31
Motor2E = 33

GPIO.setmode(GPIO.BOARD) # Set the GPIO pins as numbering
GPIO.setup(IRTrackingPin_Right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IRTrackingPin_Left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)
GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)
GPIO.setup(03, GPIO.OUT)
pwm = GPIO.PWM(03, 50)
pwm.start(0)

ball_color = ''


def SetAngle(angle):
    duty = (angle / 18) + 2
    GPIO.output(03, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    GPIO.output(03, False)
    pwm.ChangeDutyCycle(0)


def grab():
    SetAngle(30)


def rel():
    SetAngle(110)



def forward():
    #for i in range(1, 10):
        print ('FORWARD FUNK')
        GPIO.output(Motor1A,GPIO.HIGH)
        GPIO.output(Motor1B,GPIO.LOW)
        GPIO.output(Motor1E,GPIO.HIGH)
        GPIO.output(Motor2A,GPIO.HIGH)
        GPIO.output(Motor2B,GPIO.LOW)
        GPIO.output(Motor2E,GPIO.HIGH) 

def loop():    
    flag = True
    stop_count = 0
    while True:
        if GPIO.input(IRTrackingPin_Right) == True and GPIO.input(IRTrackingPin_Left) == True and flag:
            if stop_count == 2000:
                print ('STOP')
                GPIO.output(Motor1E,GPIO.LOW)
                GPIO.output(Motor2E,GPIO.LOW)
                data = read_qr()
                ob_type, ob_color = data.split(',')
                print ('type: ' , ob_type)
                print ('color: ', ob_color)
            
                if ob_type == 'Ball':
                    ball_color = ob_color
                    grab()
                
                
                elif ob_type == 'Box' and ob_color == ball_color:
                    rel()

                flag = False

            else:
                stop_count += 1
                print('*************************************', stop_count)
                forward()
                
        elif GPIO.input(IRTrackingPin_Right) == True and GPIO.input(IRTrackingPin_Left) == False and flag:
            print ('RIGTH')
            #GPIO.output(Motor2A,GPIO.LOW)
            #GPIO.output(Motor2B,GPIO.HIGH)
            GPIO.output(Motor2E,GPIO.LOW)
            GPIO.output(Motor1A,GPIO.HIGH)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor1E,GPIO.HIGH)
            stop_count = 0
            
             
        elif GPIO.input(IRTrackingPin_Right) == False and GPIO.input(IRTrackingPin_Left) == True and flag:    
            print ('LEFT')
            #GPIO.output(Motor1A,GPIO.LOW)
            #GPIO.output(Motor1B,GPIO.HIGH)
            GPIO.output(Motor1E,GPIO.LOW)
            GPIO.output(Motor2A,GPIO.HIGH)
            GPIO.output(Motor2B,GPIO.LOW)
            GPIO.output(Motor2E,GPIO.HIGH)
            stop_count = 0

             
        elif flag:
             forward()
             stop_count = 0
             
        elif not flag:
            while GPIO.input(IRTrackingPin_Right) == True or GPIO.input(IRTrackingPin_Left) == True:
                forward()
            flag = True
    GPIO.cleanup() # Release resource
 
def decode(im) : 
  # Find barcodes and QR codes
  decodedObjects = pyzbar.decode(im)
 
  # return the first object detected
  for obj in decodedObjects:
    #print('Type : ', obj.type)
    #print('Data : ', obj.data,'\n')

    return decodedObjects, obj.data
 
  return decodedObjects , None

# Display barcode and QR code location  
def display(im, decodedObjects):
 
  # Loop over all decoded objects
  for decodedObject in decodedObjects: 
    points = decodedObject.location
 
    # If the points do not form a quad, find convex hull
    if len(points) > 4 : 
      hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
      hull = list(map(tuple, np.squeeze(hull)))
    else : 
      hull = points;
     
    # Number of points in the convex hull
    n = len(hull)
 
    # Draw the convext hull
    for j in range(0,n):
      cv2.line(im, hull[j], hull[ (j+1) % n], (255,0,0), 3)
 
  # Display results 
  #cv2.imshow("Results", im);
  #cv2.waitKey(0);


def read_qr():
  cap = cv2.VideoCapture(0)
  while(True):
    ret, im = cap.read()
    decodedObjects, data = decode(im)
    display(im, decodedObjects)
    #h, w = im.shape[:2]
    #cv2.resize(im, (w/10, h/10), interpolation=cv2.INTER_AREA)
    cv2.imshow('result', im);
    cv2.waitKey(15)
    if len(decodedObjects):
      #print (data)
      return data
      

# Main 
if __name__ == '__main__':
  while True:
    loop()
  
