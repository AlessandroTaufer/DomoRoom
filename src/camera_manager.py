#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import cv2
import datetime
import logging
import time
from threading import Thread


class CameraManager:
    def __init__(self, parent):
        self.parent = parent  # Class parent
        self.enabled = True  # CameraManager status
        self.logger = logging.getLogger("DomoRoom-camera_manager")  # Default logger
        self.cameras = []  # All the cameras in use
        self.motion_detection_status = False  # Is motion detection enabled?
        self.motion_threshold = 3000  # Minimum distance between images to trigger the motion detection
        self.motion_sleep = 2  # Interval (in seconds) between two motion detection shots
        self.motion_refresh_frequency = 4  # How many shots to refresh the first capture
        self.add_cam(0)  # Attach the default camera  TODO find a better way to initialize camera manager
        self.last_shot = None  # Last captured shot
        Thread(target=self.acquire_shot, args=[self.cameras[0]]).start()  # TODO manage multi camera option

    def add_cam(self, camera):  # Add a camera to the cameras list
        if isinstance(camera, Camera):
            self.cameras.append(camera)
            return True
        elif isinstance(camera, int):
            try:
                self.cameras.append(Camera(camera))
                return True
            except cv2.error:
                self.logger.warning("Could not open the camera")
        return False

    def remove_cam(self, id):  # Remove a camera from the cameras list
        if isinstance(id, Camera):
            self.cameras.remove(id)
            self.logger.debug("Removed camera: " + str(id))
            return True
        else:
            try:
                tmp_camera = self.cameras.pop(id)
                self.logger.debug("Removed camera " + str(tmp_camera) + " at position: " + str(id))
                return True
            except IndexError:
                self.logger.warning("Could not remove the camera")
        return False

    def shot(self, index=0):  # Shot a photo with the selected camera
        if 0 <= index < len(self.cameras):
            try:
                return self.cameras[index].capture_image()  # TODO why not last shot?
            except:
                self.logger.warning("An error occurred while taking a photo, cam: " + str(self.cameras[index]))
        return None

    def turn_on_motion_detection(self):  # Turn on the motion detection
        Thread(target=self.motion_detection, args=[0]).start()

    def turn_off_motion_detection(self):  # Turn off the motion detection
        self.motion_detection_status = False

    def acquire_shot(self, cam):  # Keeps emptying the camera buffer
        while self.enabled:
            self.last_shot = cam.capture_image()
            cv2.imshow("Motion scanner", self.last_shot)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def motion_detection(self, cam_pos, script=None):  # Detect motion on a given camera
        self.motion_detection_status = True
        self.logger.info("Enabling motion detection")
        if not (0 <= cam_pos < len(self.cameras)):
            self.logger.warning("Invalid camera pos")
            return
        time.sleep(5)
        frame1 = None
        refresh_frequency = 0
        self.logger.info("Motion detection enabled")
        while self.motion_detection_status:
            if frame1 is None or refresh_frequency == 0:
                frame1 = cv2.cvtColor(self.last_shot, cv2.COLOR_BGR2GRAY)
                refresh_frequency = self.motion_refresh_frequency
            frame2 = self.last_shot
            gray_frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            distance = cv2.norm(frame1, gray_frame2, cv2.NORM_L2)  # Manhattan norm
            # difference = cv2.absdiff(frame1, frame2) difference between the two images
            if distance > self.motion_threshold:
                print("Detected Motion at " + str(datetime.datetime.now()) + " distance: " + str(distance))
                self.parent.telegram_manager.broadcast_message("Detected motion! ")
                self.add_time(frame2)
                self.parent.telegram_manager.broadcast_image(frame2)
                if script is not None:
                    try:
                        script()
                    except:
                        self.logger.error("Failed to run the motion detection script")
                logging.info("Detected motion")
                refresh_frequency -= 1
            time.sleep(self.motion_sleep)
        self.logger.info("Motion detection disabled")

    @staticmethod
    def add_time(img):  # Put the current time on the image
        cv2.putText(img, datetime.datetime.now().strftime("%d %B %Y %I:%M:%S%p"),
                    (0, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, 3)


class Camera:
    def __init__(self, index=0):
        self.cam = cv2.VideoCapture(index)  # Camera VideoCapture object
        if not self.cam.isOpened():
            raise cv2.error

    def capture_image(self):  # Shot a photo  TODO addtime parameter
        ret, frame = self.cam.read()
        return frame


if __name__ == "__main__":
    pass
    # log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # logging.basicConfig(level=logging.DEBUG, format=log_format, filemode='w')
    # # -----
    # cam = Camera()
    # frame1 = cam.capture_image()
    # frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    # window_name = "Motion detection"
    # cv2.namedWindow(window_name)
    # while True:
    #     frame2 = cam.capture_image()
    #     #frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    #     distance = cv2.norm(frame1, frame2, cv2.NORM_L1)  # Manhattan norm
    #     print("manhattan norm: " + str(distance))
    #     cv2.imshow(window_name, d1)
    #
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
