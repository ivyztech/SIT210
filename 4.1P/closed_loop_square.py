#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped

class ClosedLoopSquare:
    def __init__(self):
        rospy.init_node('closed_loop_square')
        
        # --- CALIBRATION CONSTANTS ---
        # Update these by driving 1m and checking the tick diff
        self.TICKS_PER_METER = 1000 
        self.TICKS_PER_90_DEG = 500  

        # State tracking
        self.current_ticks = 0
        self.start_ticks = 0
        self.is_moving = False
        self.goal_ticks = 0
        
        # ROS Infrastructure
        self.pub = rospy.Publisher('~car_cmd', Twist2DStamped, queue_size=1)
        # Using the right wheel encoder for distance
        rospy.Subscriber('~right_wheel_encoder_node/tick', WheelEncoderStamped, self.encoder_callback)

    def encoder_callback(self, msg):
        self.current_ticks = msg.data
        
        if self.is_moving:
            # Check if we have reached or exceeded the goal
            ticks_traveled = abs(self.current_ticks - self.start_ticks)
            
            if ticks_traveled >= self.goal_ticks:
                self.stop_robot()
                self.is_moving = False
                rospy.loginfo("Goal Reached!")

    def move_straight(self, distance_m):
        rospy.loginfo(f"Moving straight {distance_m}m")
        self.start_ticks = self.current_ticks
        self.goal_ticks = distance_m * self.TICKS_PER_METER
        self.is_moving = True
        
        # Command movement
        cmd = Twist2DStamped()
        cmd.v = 0.4
        cmd.omega = 0.0
        self.pub.publish(cmd)

    def rotate_in_place(self, degrees):
        rospy.loginfo(f"Rotating {degrees} degrees")
        self.start_ticks = self.current_ticks
        # Simple ratio: (degrees / 90) * TICKS_PER_90_DEG
        self.goal_ticks = (degrees / 90.0) * self.TICKS_PER_90_DEG
        self.is_moving = True
        
        cmd = Twist2DStamped()
        cmd.v = 0.0
        cmd.omega = 1.0 # Adjust sign for direction
        self.pub.publish(cmd)

    def stop_robot(self):
        cmd = Twist2DStamped()
        cmd.v = 0.0
        cmd.omega = 0.0
        self.pub.publish(cmd)

    def run_square(self):
        # In a real state machine, you'd use a counter to cycle 
        # through 4 iterations of move -> rotate
        for i in range(4):
            self.move_straight(1.0)
            while self.is_moving and not rospy.is_shutdown():
                rospy.sleep(0.1) # Busy-wait while callback handles the stop
            
            self.rotate_in_place(90)
            while self.is_moving and not rospy.is_shutdown():
                rospy.sleep(0.1)

if __name__ == '__main__':
    node = ClosedLoopSquare()
    rospy.sleep(1) # Let subscribers initialize
    node.run_square()
