#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
from turtlesim.msg import Pose

def commander():
    rospy.init_node('turtle_commander', anonymous=True)
    
    # Publishers for the different control modes
    dist_pub = rospy.Publisher('/goal_distance', Float64, queue_size=10)
    angle_pub = rospy.Publisher('/goal_angle', Float64, queue_size=10)
    point_pub = rospy.Publisher('/goal_point', Pose, queue_size=10)
    
    rospy.sleep(1) # Wait for connections
    
    while not rospy.is_shutdown():
        print("\n" + "="*30)
        print("   TURTLE COMMAND CENTER")
        print("="*30)
        print("1. Move Specific Distance (Forward/Backward)")
        print("2. Rotate to Absolute Angle (Radians)")
        print("3. Navigate to (X, Y) Coordinate")
        print("4. Exit")
        
        choice = input("\nSelect an option: ")

        try:
            if choice == '1':
                d = float(input("Enter distance (e.g., 2.0 or -1.5): "))
                dist_pub.publish(d)
            elif choice == '2':
                a = float(input("Enter angle in radians (-3.14 to 3.14): "))
                angle_pub.publish(a)
            elif choice == '3':
                target = Pose()
                target.x = float(input("Target X (0-11): "))
                target.y = float(input("Target Y (0-11): "))
                point_pub.publish(target)
            elif choice == '4':
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Error: Please enter a numeric value.")

if __name__ == '__main__':
    try:
        commander()
    except rospy.ROSInterruptException:
        pass
