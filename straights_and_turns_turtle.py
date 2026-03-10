#!/usr/bin/env python3

import rospy 
import math
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose

class TurtlesimStraightsAndTurns:
    def __init__(self):
        # State variables
        self.last_total_distance = 0.0
        self.start_distance_for_goal = 0.0
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        
        self.goal_distance = 0.0
        self.goal_theta = 0.0
        
        self.dist_goal_active = False
        self.angle_goal_active = False

        rospy.init_node('turtlesim_straights_and_turns_node', anonymous=True)

        # Subscribers
        rospy.Subscriber("/turtle_dist", Float64, self.distance_callback)
        rospy.Subscriber("/goal_angle", Float64, self.goal_angle_callback)
        rospy.Subscriber("/goal_distance", Float64, self.goal_distance_callback)
        rospy.Subscriber("/turtle1/pose", Pose, self.pose_callback)
        
        # Subscriber for X,Y Navigation
        rospy.Subscriber("/goal_point", Pose, self.goal_point_callback)

        # Publisher
        self.velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

        # Timer: 100Hz
        rospy.Timer(rospy.Duration(0.01), self.timer_callback)

        rospy.loginfo("Full Control Node Initialized!")
        rospy.spin()

    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta

    def distance_callback(self, msg):
        self.last_total_distance = msg.data

    def goal_angle_callback(self, msg):
        self.goal_theta = msg.data
        self.angle_goal_active = True
        self.dist_goal_active = False
        rospy.loginfo("Rotating to: %.2f rad", self.goal_theta)

    def goal_distance_callback(self, msg):
        self.start_distance_for_goal = self.last_total_distance
        self.goal_distance = msg.data # Can be negative for backward
        self.dist_goal_active = True
        self.angle_goal_active = False
        rospy.loginfo("Moving distance: %.2f units", msg.data)

    def goal_point_callback(self, msg):
        # Calculate angle and distance to (x,y)
        dx = msg.x - self.current_x
        dy = msg.y - self.current_y
        self.goal_theta = math.atan2(dy, dx)
        self.goal_distance = math.sqrt(dx**2 + dy**2)
        
        # Starting sequence by turning to specific angle
        self.angle_goal_active = True
        self.dist_goal_active = False # Will be triggered once turn finishes
        rospy.loginfo("Navigating to Point: (%.2f, %.2f)", msg.x, msg.y)

    def timer_callback(self, event):
        move_cmd = Twist()

        # 1. HANDLE ROTATION
        if self.angle_goal_active:
            angle_error = self.goal_theta - self.current_theta
            
            # Shortest Path Wraparound Logic
            if angle_error > math.pi: angle_error -= 2 * math.pi
            if angle_error < -math.pi: angle_error += 2 * math.pi

            if abs(angle_error) < 0.01:
                self.angle_goal_active = False
                # If turtle navigating to a point, it starts moving forward
                if hasattr(self, 'goal_distance') and self.goal_distance != 0:
                    self.start_distance_for_goal = self.last_total_distance
                    self.dist_goal_active = True
                rospy.loginfo("Rotation Reached.")
            else:
                move_cmd.angular.z = 1.0 if angle_error > 0 else -1.0
        
        # 2. HANDLE LINEAR MOVEMENT
        elif self.dist_goal_active:
            distance_traveled = abs(self.last_total_distance - self.start_distance_for_goal)
            
            if distance_traveled >= abs(self.goal_distance):
                self.dist_goal_active = False
                self.goal_distance = 0 # Reset
                rospy.loginfo("Distance Reached.")
            else:
                # Speed direction matches the sign of goal_distance
                move_cmd.linear.x = 1.0 if self.goal_distance > 0 else -1.0

        self.velocity_publisher.publish(move_cmd)

if __name__ == '__main__': 
    try: 
        TurtlesimStraightsAndTurns()
    except rospy.ROSInterruptException: 
        pass
