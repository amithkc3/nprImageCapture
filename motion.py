import picamera
from time import sleep
import numpy as np
import io
import sys
import io
from PIL import Image
import requests


def rgb2gray(img):
    return np.dot(img[...,:3],[0.299,0.587,0.114])

def main(preview="preview"):
    
    resolution_r = 720
    resolution_c = 1280

    preview = str(preview)
    
    number_of_pixels = 80
    threshold = 32

    ip = "35.34.26.1"

    url = "http://" + ip + ":5000/get_plate_checkin"
    
        
    with picamera.PiCamera() as camera:
        camera.resolution = (resolution_c,resolution_r)
        camera.framerate = 20

        sleep(1)
        
        print("captured background")
        background = np.empty((resolution_r,resolution_c,3),dtype=np.uint8)
        camera.capture(background,'rgb',use_video_port=True)
        background_gray = rgb2gray(background)

        img_color = np.empty((resolution_r,resolution_c,3),dtype=np.uint8)
        img_gray = np.empty((resolution_r,resolution_c),dtype=np.uint8)
        diff = np.empty((resolution_r,resolution_c),dtype=np.uint8)
        
        
        try:
            if(preview == "preview"):
                camera.start_preview()
            while(True):
                pixels = 0
                camera.capture(img_color,'rgb',use_video_port = True)
                img_gray = rgb2gray(img_color)
                diff = np.absolute(background_gray-img_gray)

                diff2 = np.where(diff>threshold,1,0)
                pixels = len(diff2[diff2>0])
                
                if(pixels > number_of_pixels):
                    print("Motion detected")
                    print("pixels = "+str(pixels),end='   ')

                    im = Image.fromarray(img_color.astype("uint8"))
                    buff = io.BytesIO()
                    im.save(buff,"JPEG")
                    buff.seek(0)

                    response = requests.post(url,data=buff.read())
                    print(response)
                    
                    
                    camera.capture(img_color,'rgb',use_video_port = True)
                    img_gray = rgb2gray(img_color)
                background_gray = (img_gray)
                sleep(1)
                     
        finally:
            if(preview == "preview"):
                camera.stop_preview()
            print("Exiting")
            

if __name__ == "__main__":
    main()
    
       

        
