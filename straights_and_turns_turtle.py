#!/usr/bin/env python3
import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math 

class TurtlesimStraightsAndTurns:
    def __init__(self):
        # Initialize variables
        self.last_distance = 0.0
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

        # Publisher
        self.velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

        # Timer: 100Hz (0.01s)
        rospy.Timer(rospy.Duration(0.01), self.timer_callback)
        rospy.loginfo("Distinction Node Initialized!")
        rospy.spin()

    def pose_callback(self, msg):
        self.current_theta = msg.theta

    def distance_callback(self, msg):
        self.last_distance = msg.data

    def goal_angle_callback(self, msg):
        self.goal_theta = msg.data
        self.angle_goal_active = True
        self.dist_goal_active = False # Prioritize rotation
        rospy.loginfo("New Angle Goal: %.2f radians", self.goal_theta)

    def goal_distance_callback(self, msg):
        self.goal_distance = self.last_distance + msg.data
        self.dist_goal_active = True
        self.angle_goal_active = False # Prioritize movement
        rospy.loginfo("New Distance Goal: %.2f units", msg.data)

    def timer_callback(self, event):
        move_cmd = Twist()

        # Handle Rotation
        if self.angle_goal_active:
            angle_error = self.goal_theta - self.current_theta
            
            # Shortest Path Wraparound Logic 
            if angle_error > math.pi: angle_error -= 2 * math.pi
            if angle_error < -math.pi: angle_error += 2 * math.pi

            if abs(angle_error) < 0.01:
                self.angle_goal_active = False
                rospy.loginfo("Angle Reached!")
            else:
                # Proportional-ish turning
                move_cmd.angular.z = 1.0 if angle_error > 0 else -1.0
        
        # Handle Straight Movement
        elif self.dist_goal_active:
            if self.last_distance >= self.goal_distance:
                self.dist_goal_active = False
                rospy.loginfo("Distance Reached!")
            else:
                move_cmd.linear.x = 1.0

        self.velocity_publisher.publish(move_cmd)

if __name__ == '__main__': 
    try: 
        TurtlesimStraightsAndTurns()
    except rospy.ROSInterruptException: pass
