#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
 
class Drive_Square:
    def __init__(self):
        #Initialize global class variables
        self.cmd_msg = Twist2DStamped()

        #Initialize ROS node
        rospy.init_node('drive_square_node', anonymous=True)
        
        #Initialize Pub/Subs
        self.pub = rospy.Publisher('/mybota002446/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/mybota002446/fsm_node/mode', FSMState, self.fsm_callback, queue_size=1)
        
    # robot only moves when lane following is selected on the duckiebot joystick app
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)
        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()
        elif msg.state == "LANE_FOLLOWING":            
            rospy.sleep(1) # Wait for a sec for the node to be ready
            self.move_robot()
 
    # Sends zero velocities to stop the robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)
 
    # Spin forever but listen to message callbacks
    def run(self):
    	rospy.spin() # keeps node from exiting until node has shutdown

    # Robot drives in a square and then stops
    def move_robot(self):
        # 1. Defining calibrated "ideal" values
        # These values must be tweaked during  first few runs on the lab floor !!!!! 
        one_meter_timeout = 2.8  # How long to drive to hit 1m
        ninety_degree_timeout = 1.2 # How long to turn to hit 90 deg
        
        v_speed = 0.4      # Constant linear speed
        omega_speed = 1.0  # Constant angular speed

        for side in range(4):
            rospy.loginfo(f"Driving side {side + 1} of the square")

            # --- STEP 1: DUCKIEBOT DRIVES 1 METER ---
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = v_speed
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)
            rospy.sleep(one_meter_timeout)
            
            # Stop to settle
            self.stop_robot()
            rospy.sleep(0.5)

            # --- STEP 2: DUCKIEBOT TURNS 90 DEGREES ---
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = omega_speed
            self.pub.publish(self.cmd_msg)
            rospy.sleep(ninety_degree_timeout)
            
            # Stop to settle before the next straight
            self.stop_robot()
            rospy.sleep(0.5)

        rospy.loginfo("Finished the square!")
        self.stop_robot()
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.5 # striaght line velocity
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)
        rospy.loginfo("Forward!")
        rospy.sleep(1) # straight line driving time
        
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = -0.5 # striaght line velocity
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)
        rospy.loginfo("Backward!")
        rospy.sleep(1) # straight line driving time
        
        ######################
                
        self.stop_robot()

if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
