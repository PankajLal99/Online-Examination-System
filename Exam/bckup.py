
#AI Proctoring .......................

class VideoCamera(object):

    def __init__(self):
        print("[INFO] starting video stream...")
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def start(self):
        vid = self.video
        while(True):
            ret,img = vid.read()
            ret,frame = cv2.imencode('.jpg',img)
            return frame.tobytes()

def opencv_stream(camera):
    while True:
        frame=camera.start()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def video(request):
    try:
        return StreamingHttpResponse(opencv_stream(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")