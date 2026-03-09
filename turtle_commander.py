#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64

def commander():
    rospy.init_node('turtle_commander', anonymous=True)
    dist_pub = rospy.Publisher('/goal_distance', Float64, queue_size=10)
    angle_pub = rospy.Publisher('/goal_angle', Float64, queue_size=10)
    
    while not rospy.is_shutdown():
        print("\n--- Turtle Command Center ---")
        print("1. Move Distance")
        print("2. Set Angle (Radians)")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            val = float(input("Enter distance (e.g. 2.0): "))
            dist_pub.publish(val)
        elif choice == '2':
            val = float(input("Enter angle in radians (-3.14 to 3.14): "))
            angle_pub.publish(val)
        elif choice == '3':
            break

if __name__ == '__main__':
    commander()
