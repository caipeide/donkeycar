
import settings

import io
import os
import time
import threading
from itertools import cycle

from PIL import Image

from utils import image as image_utils


from threading import Thread
 
class PiVideoStream:
    def __init__(self, resolution=(320, 240), framerate=32):
        from picamera.array import PiRGBArray
        from picamera import PiCamera

        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)
 
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        
        print('PiVideoStream loaded.. .warming camera')

        time.sleep(2)
        self.start()




    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(1)
        return self
 
    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
 
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame
 
    def capture_img(self):
        arr = self.read()

    
        print(arr.shape)
        img = Image.fromarray(arr)
        return img

    def capture_binary(self):
        '''return binary stream of image for webserver'''
        img = self.capture_img()
        return image_utils.img_to_binary(img)

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True




class FakeCamera():
    ''' 
    Class that acts like a PiCamera but reads files from a dir.
    Used for testing on non-Pi devices.
    '''
    def __init__(self):
        print('loading FakeCamera')
        print(settings)
        self.file_list = os.listdir(settings.FAKE_CAMERA_IMG_DIR)
        self.file_cycle = cycle(self.file_list) #create infinite iterator
        self.counter = 0

    def capture_img(self):

        #print('capturing file: %s' % self.file_list[self.counter])

        img = Image.open("img/" + next(self.file_cycle))
        self.counter += 1
        return normalize(img)
        
    def capture_binary(self):

        img = self.capture_img()
        return image_utils.img_to_binary(img)



def normalize(img):
    '''
    The way I've chosen to normalize all images.

    Accepts and returns PIL image.
    '''
    img = image_utils.square(img)
    img = image_utils.scale(img, 128)
    return img
