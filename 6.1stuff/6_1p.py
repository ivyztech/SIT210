#!/usr/bin/env python3

# Python Libs
import sys
import time

# numpy
import numpy as np

# OpenCV
import cv2
from cv_bridge import CvBridge

# ROS Libraries
import rospy
import roslib

# ROS Message Types
from sensor_msgs.msg import CompressedImage

class Lane_Detector:
    def __init__(self):
        # 1. Initialize the node FIRST
        rospy.init_node("my_lane_detector")
        self.cv_bridge = CvBridge()

        # 2. Updated topic name to match your bag file exactly
        self.image_sub = rospy.Subscriber('/akanb/camera_node/image/compressed', CompressedImage, self.image_callback, queue_size=1)
        
        rospy.loginfo("Lane Detector Node Initialized. Waiting for images...")

    def image_callback(self, msg):
        # Heartbeat print
        print("Image received")
        
        try:
            # 1. Convert ROS message to OpenCV BGR format
            img = self.cv_bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
            
            # 2. CROP: Keep only the bottom half
            height, width = img.shape[:2]
            cropped = img[int(height/2):height, 0:width]

            # 3. HSV CONVERSION
            hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

            # 4. COLOR FILTERING
            lower_white = np.array([0, 0, 150])
            upper_white = np.array([180, 50, 255])
            
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([35, 255, 255])

            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

            # 5. CANNY EDGE DETECTION
            edges = cv2.Canny(hsv, 100, 200)

            # 6. HOUGH TRANSFORM
            lines_white = cv2.HoughLinesP(mask_white, 1, np.pi/180, 30, minLineLength=20, maxLineGap=10)
            lines_yellow = cv2.HoughLinesP(mask_yellow, 1, np.pi/180, 30, minLineLength=20, maxLineGap=10)

            # 7. DRAWING
            final_output = self.draw_lines(cropped, lines_white, (0, 255, 0)) # Green for White lines
            final_output = self.draw_lines(final_output, lines_yellow, (0, 0, 255)) # Red for Yellow lines

            # 8. DISPLAY: Increased waitKey to 30ms to allow smoother rendering
            cv2.imshow('1_White_Filter', mask_white)
            cv2.imshow('2_Yellow_Filter', mask_yellow)
            cv2.imshow('3_Final_Hough_Lines', final_output)
            cv2.waitKey(30)

        except Exception as e:
            print(f"Error in image_callback: {e}")

    def draw_lines(self, img, lines, color):
        """Helper function to draw Hough lines on an image"""
        out = np.copy(img)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(out, (x1, y1), (x2, y2), color, 3)
        return out

    def run(self):
        rospy.spin()

if __name__ == "__main__":
    try:
        lane_detector_instance = Lane_Detector()
        lane_detector_instance.run()
    except rospy.ROSInterruptException:
        pass
