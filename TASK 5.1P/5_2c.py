#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        
        #Initialize ROS node
        rospy.init_node('target_follower_node', anonymous=True)

        # When shutdown signal is received, we run clean_shutdown function
        rospy.on_shutdown(self.clean_shutdown)
        
        ###### Init Pub/Subs. 
        self.cmd_vel_pub = rospy.Publisher('/mybota002446/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/mybota002446/apriltag_detector_node/detections', AprilTagDetectionArray, self.tag_callback, queue_size=1)

        rospy.spin() # Spin forever but listen to message callbacks

    # Apriltag Detection Callback
    def tag_callback(self, msg):
        self.move_robot(msg.detections)
 
    # Stopping Robot before node has shut down. This ensures the robot keep moving with the latest velocity command
    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    # Sends zero velocity to stop the robot
    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):

        #### s222615433 program for 5.2C ####

        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()

        # 1) If no object is detected, stay completely stationary
        if len(detections) == 0:
            cmd_msg.v = 0.0
            cmd_msg.omega = 0.0 
            self.cmd_vel_pub.publish(cmd_msg)
            return

        # 2) Object detected. Extract X (left/right) and Z (distance)
        x = detections[0].transform.translation.x
        y = detections[0].transform.translation.y
        z = detections[0].transform.translation.z

        rospy.loginfo("Target acquired! x: %f, z(distance): %f", x, z)

        # --- TUNING PARAMETERS ---
        # Target distance in meters (e.g., 0.4 = 40cm)
        target_distance = 0.4  
        
        # Proportional gains
        k_p_v = 1.0      # Gain for forward/backward speed must be adjusted
        k_p_omega = 2.0  # Gain for left/right rotation must aslo be adjusted

        # Calculate Distance Error
        error_z = z - target_distance

        # Apply control loops
        cmd_msg.v = k_p_v * error_z
        cmd_msg.omega = -k_p_omega * x 
        
        # Preventing the robot from shooting forward too fast
        # if the tag is detected very far away.
        if cmd_msg.v > 0.5:
            cmd_msg.v = 0.5
        elif cmd_msg.v < -0.5:
            cmd_msg.v = -0.5

        self.cmd_vel_pub.publish(cmd_msg)

        #############################

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass
