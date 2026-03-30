#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from numpy import sign

class ClosedLoopSquare:
    def __init__(self):
        rospy.init_node('closed_loop_control')
        
        # --- CALIBRATION (Update these values after testing!) ---
        self.TICKS_PER_METER = 1350  
        self.TICKS_PER_DEGREE = 4.2   
        
        # State Variables
        self.current_ticks = 0
        self.cmd_pub = rospy.Publisher('/akandb/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        
        # Subscribe to one encoder (right wheel)
        rospy.Subscriber('/akandb/right_wheel_encoder_node/tick', WheelEncoderStamped, self.encoder_cb)
        
        rospy.loginfo("Encoder node initialized. Waiting for ticks...")
        rospy.sleep(1) # Wait for subscriber to connect

    def encoder_cb(self, msg):
        self.current_ticks = msg.data

    def stop_robot(self):
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = 0.0
        self.cmd_pub.publish(msg)

    def move_straight(self, distance, speed):
        """
        Moves robot a specific distance (meters) at a given speed.
        Handles negative distance/speed for backward motion.
        """
        start_ticks = self.current_ticks
        target_ticks = abs(distance * self.TICKS_PER_METER)
        
        msg = Twist2DStamped()
        msg.v = speed * sign(distance) # Handle direction
        msg.omega = 0.0
        
        rospy.loginfo(f"Moving {distance}m at speed {speed}")
        
        # Loop until the difference in ticks matches the target
        while abs(self.current_ticks - start_ticks) < target_ticks and not rospy.is_shutdown():
            self.cmd_pub.publish(msg)
            rospy.sleep(0.01) # Small delay to prevent CPU hogging
            
        self.stop_robot()
        rospy.sleep(0.5) # Settle time

    def rotate_in_place(self, angle, speed):
        """
        Rotates robot a specific angle (degrees) at a given angular speed.
        """
        start_ticks = self.current_ticks
        target_ticks = abs(angle * self.TICKS_PER_DEGREE)
        
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = speed * sign(angle)
        
        rospy.loginfo(f"Rotating {angle} degrees")
        
        while abs(self.current_ticks - start_ticks) < target_ticks and not rospy.is_shutdown():
            self.cmd_pub.publish(msg)
            rospy.sleep(0.01)
            
        self.stop_robot()
        rospy.sleep(0.5)

    def run_square(self):
        # Draw a 1-meter square
        for side in range(4):
            rospy.loginfo(f"Side {side + 1}")
            self.move_straight(1.0, 0.4)
            self.rotate_in_place(90, 1.2)
        
        rospy.loginfo("Square complete!")

if __name__ == '__main__':
    try:
        controller = ClosedLoopSquare()
        
        # Demonstration 1: Forward and Backward at different speeds
        rospy.loginfo("--- DEMO: Forward/Backward ---")
        controller.move_straight(0.5, 0.3)  # Slow forward
        controller.move_straight(-0.5, 0.6) # Fast backward
        
        # Demonstration 2: The Square
        rospy.loginfo("--- DEMO: Closed Loop Square ---")
        controller.run_square()
        
    except rospy.ROSInterruptException:
        pass
