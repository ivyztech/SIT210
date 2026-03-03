#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class PerfectSquare:
    def __init__(self):
        rospy.init_node('perfect_square', anonymous=True)
        self.velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
        self.pose_subscriber = rospy.Subscriber('/turtle1/pose', Pose, self.update_pose)
        self.pose = Pose()
        self.rate = rospy.Rate(10)

    def update_pose(self, data):
        """Callback function to update the current position."""
        self.pose = data

    def move_forward(self, distance):
        x0, y0 = self.pose.x, self.pose.y
        vel_msg = Twist()
        vel_msg.linear.x = 2.0
        
        current_distance = 0
        while current_distance < distance and not rospy.is_shutdown():
            self.velocity_publisher.publish(vel_msg)
            current_distance = math.sqrt((self.pose.x - x0)**2 + (self.pose.y - y0)**2)
            self.rate.sleep()
        
        # Stop
        self.velocity_publisher.publish(Twist())

    def rotate(self, relative_angle_degree):
        vel_msg = Twist()
        vel_msg.angular.z = 0.5 # Slow turn for precision
        
        target_angle = self.pose.theta + (relative_angle_degree * math.pi / 180)
        
        while abs(self.pose.theta - target_angle) > 0.01 and not rospy.is_shutdown():
            self.velocity_publisher.publish(vel_msg)
            self.rate.sleep()
            
        self.velocity_publisher.publish(Twist())

    def run(self):
        # while loop for infinite
        while not rospy.is_shutdown():
            self.move_forward(2.0)
            rospy.sleep(0.5)
            self.rotate(90)
            rospy.sleep(0.5)

if __name__ == '__main__':
    try:
        ps = PerfectSquare()
        ps.run()
    except rospy.ROSInterruptException:
        pass