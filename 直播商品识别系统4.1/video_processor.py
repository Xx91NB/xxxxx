import cv2

class VideoProcessor:
    def __init__(self):
        self.cap = None
    
    def open(self, source):
        if source == "0" or source == "1":
            self.cap = cv2.VideoCapture(int(source))
        else:
            self.cap = cv2.VideoCapture(source)
        return self.cap.isOpened()
    
    def read_frame(self):
        if self.cap:
            return self.cap.read()
        return False, None
    
    def release(self):
        if self.cap:
            self.cap.release()