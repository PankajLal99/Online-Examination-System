def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype=dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords

def eye_on_mask(mask, side,shape):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask

def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
    except:
        pass
    
def donothing(x):
    pass

class VideoCamera(object):

    def __init__(self):
        print("[INFO] starting video stream...")
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def start(self):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('Exam/shape_predictor_68_face_landmarks.dat')

        left = [36, 37, 38, 39, 40, 41]
        right = [42, 43, 44, 45, 46, 47]

        ret, img = self.video.read()
        thresh = img.copy()

        cv2.namedWindow('image')
        kernel = np.ones((9, 9), np.uint8)

        cv2.createTrackbar('threshold', 'eyes', 75, 255,donothing)
        while(True):
            ret,img = self.video.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)
            for rect in rects:
                shape = predictor(gray, rect)
                shape = shape_to_np(shape)
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                mask = eye_on_mask(mask, left,shape)
                mask = eye_on_mask(mask, right,shape)
                mask = cv2.dilate(mask, kernel, 5)
                eyes = cv2.bitwise_and(img, img, mask=mask)
                mask = (eyes == [0, 0, 0]).all(axis=2)
                eyes[mask] = [255, 255, 255]
                mid = (shape[42][0] + shape[39][0]) // 2
                eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
                threshold = cv2.getTrackbarPos('threshold', 'image')
                _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
                thresh = cv2.erode(thresh, None, iterations=2) #1
                thresh = cv2.dilate(thresh, None, iterations=4) #2
                thresh = cv2.medianBlur(thresh, 3) #3
                thresh = cv2.bitwise_not(thresh)
                contouring(thresh[:, 0:mid], mid, img)
                contouring(thresh[:, mid:], mid, img, True)
                resize=cv2.resize(img, (480,320), interpolation = cv2.INTER_LINEAR)
            ret,frame = cv2.imencode('.jpg',resize)
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