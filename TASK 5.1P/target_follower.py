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
        ################################################################

        rospy.spin() # Spin forever but listen to message callbacks

    # Apriltag Detection Callback
    def tag_callback(self, msg):
        self.move_robot(msg.detections)
 
    # Stop Robot before node has shut down. This ensures the robot keep moving with the latest velocity command
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

        #### s222615433 program for 5.1P ####

        # Prepare the velocity command message
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0 # Feature requires NO forward/backward movement

        # 1) "Seek an object" Feature
        if len(detections) == 0:
            rospy.loginfo("No object detected. Seeking...")
            # Set a constant angular velocity to rotate in place
            cmd_msg.omega = 0.5 
            self.cmd_vel_pub.publish(cmd_msg)
            return

        # 2) "Look at the Object" Feature
        # If we reach here, an object is detected
        x = detections[0].transform.translation.x
        y = detections[0].transform.translation.y
        z = detections[0].transform.translation.z

        rospy.loginfo("Target acquired! x,y,z: %f %f %f", x, y, z)

        # Proportional Gain for turning. 
        # You will need to tune this value during your physical experiment.
        k_p = 2.0 

        # Calculate angular velocity. 
        # In typical camera frames, x is the horizontal offset (left/right).
        # We multiply by -k_p because if x is positive (tag to the right), 
        # the robot needs a negative angular velocity to turn right.
        # *Note: If the robot turns away from the tag, change this to +k_p
        cmd_msg.omega = -k_p * x 
        
        self.cmd_vel_pub.publish(cmd_msg)

        #############################

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass