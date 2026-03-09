#!/usr/bin/env python3

# Import Dependencies
import rospy 
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64
from turtlesim.msg import Pose
import math  # Imported for the square root function

class DistanceReader:
    def __init__(self):
        # Initialize the node
        rospy.init_node('turtlesim_distance_node', anonymous=True)

        # Variables to store the state of the turtle
        self.total_distance = 0.0
        self.prev_x = None
        self.prev_y = None

        # Initialize subscriber
        rospy.Subscriber("/turtle1/pose", Pose, self.callback)

        # Initialize publisher
        self.distance_publisher = rospy.Publisher('/turtle_dist', Float64, queue_size=10)

        rospy.loginfo("Distance Node Initialized! Start moving the turtle to see the odometer increase.")
        
        # Keeps python from exiting
        rospy.spin()

    def callback(self, msg):
        ########## DOMINIQUE VILLAFUERTE 222615433 CODE ##########
           # 1. If this is the first message received, record the position and wait for the next one
        if self.prev_x is None or self.prev_y is None:
            self.prev_x = msg.x
            self.prev_y = msg.y
            return

        # 2. Calculate the distance between the last pose and current pose
        # Using the Euclidean distance formula: sqrt((x2-x1)^2 + (y2-y1)^2)
        dist_increment = math.sqrt((msg.x - self.prev_x)**2 + (msg.y - self.prev_y)**2)

        # 3. Add the increment to our total distance
        self.total_distance += dist_increment

        # 4. Update the "previous" values for the next callback
        self.prev_x = msg.x
        self.prev_y = msg.y

        # 5. Publish the total distance
        # We must wrap the float in a Float64 object
        dist_msg = Float64()
        dist_msg.data = self.total_distance
        self.distance_publisher.publish(dist_msg)

        # Log the distance to the terminal
        rospy.loginfo("Total Distance: %.4f", self.total_distance)

        ###########################################

if __name__ == '__main__': 
    try: 
        distance_reader_class_instance = DistanceReader()
    except rospy.ROSInterruptException: 
        pass

