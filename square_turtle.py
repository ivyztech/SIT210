#!/usr/bin/env python3

# Import Dependencies
import rospy 
from geometry_msgs.msg import Twist 
import time 

def move_turtle_square(): 
    rospy.init_node('turtlesim_square_node', anonymous=True)
    
    # Init publisher
    velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10) 
    rospy.loginfo("Turtles are great at drawing squares!")

    ########## YOUR CODE GOES HERE ##########
    # Set the execution frequency
    rate = rospy.Rate(1) 
    
    while not rospy.is_shutdown():
        # 1. MOVE FORWARD
        move_cmd = Twist()
        move_cmd.linear.x = 2.0  # Go forward
        move_cmd.angular.z = 0.0
        velocity_publisher.publish(move_cmd)
        rospy.sleep(2.0) # Move for 2 seconds

        # 2. STOP
        stop_cmd = Twist()
        velocity_publisher.publish(stop_cmd)
        rospy.sleep(1.0) # Brief pause for stability

        # 3. TURN 90 DEGREES
        turn_cmd = Twist()
        turn_cmd.linear.x = 0.0
        # To turn 90 deg (pi/2) in 1 sec, set speed to 1.57 rad/s
        turn_cmd.angular.z = 1.57 
        velocity_publisher.publish(turn_cmd)
        rospy.sleep(1.0) # Turn for 1 second

        # 4. STOP AGAIN
        velocity_publisher.publish(stop_cmd)
        rospy.sleep(1.0)

        ###########################################

if __name__ == '__main__': 

    try: 
        move_turtle_square() 
    except rospy.ROSInterruptException: 
        pass
        
