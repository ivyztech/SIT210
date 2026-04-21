#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from sensor_msgs.msg import Range  # Required for ToF sensor
from numpy import sign

class SynchronizedSquare:
    def __init__(self):
        rospy.init_node('synchronized_square_control')

        # --- CALIBRATION ---
        self.TICKS_PER_METER = 950
        self.TICKS_PER_DEGREE = 0.40
        self.STOP_THRESHOLD = 0.30  # Stop if obstacle is closer than 30cm

        # State Variables
        self.right_ticks = 0
        self.left_ticks = 0
        self.tof_distance = 10.0  # Initialize with a clear path value

        # Publishers
        self.cmd_pub = rospy.Publisher('/mybota002446/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)

        # Subscribers
        rospy.Subscriber('/mybota002446/right_wheel_encoder_node/tick', WheelEncoderStamped, self.right_cb)
        rospy.Subscriber('/mybota002446/left_wheel_encoder_node/tick', WheelEncoderStamped, self.left_cb)
        rospy.Subscriber('/mybota002446/front_center_tof_driver_node/range', Range, self.tof_cb)

        rospy.loginfo("Syncing sensors... Please wait.")
        rospy.sleep(2.0)

    def right_cb(self, msg):
        self.right_ticks = msg.data

    def left_cb(self, msg):
        self.left_ticks = msg.data

    def tof_cb(self, msg):
        # Updating the current distance from the ToF sensor
        self.tof_distance = msg.range

    def stop_robot(self):
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = 0.0
        self.cmd_pub.publish(msg)

    def move_straight(self, distance, speed):
        start_left = self.left_ticks
        start_right = self.right_ticks
        target_ticks = abs(distance * self.TICKS_PER_METER)
        kp = 0.0009
        rate = rospy.Rate(20)

        rospy.loginfo(f"Moving straight {distance}m")

        while not rospy.is_shutdown():
            # COLLISION PREVENTION LOGIC
            if self.tof_distance < self.STOP_THRESHOLD:
                rospy.logwarn(f"Obstacle at {self.tof_distance:.2f}m! Waiting...")
                self.stop_robot()
                rate.sleep()
                continue  # Skip movement calculation; stay in the loop until clear

            # Calculate distance traveled
            d_left = abs(self.left_ticks - start_left)
            d_right = abs(self.right_ticks - start_right)

            if (d_left + d_right) / 2 >= target_ticks:
                break

            # Drift Correction
            error = d_left - d_right
            msg = Twist2DStamped()
            msg.v = speed * sign(distance)
            msg.omega = error * kp

            self.cmd_pub.publish(msg)
            rate.sleep()

        self.stop_robot()
        rospy.sleep(0.8) # Allow momentum to dissipate after reaching target

    def rotate_in_place(self, angle, speed):
        # As per instructions, collision prevention is NOT active here
        start_right = self.right_ticks
        target_ticks = abs(angle * self.TICKS_PER_DEGREE)

        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = speed * sign(angle)

        rospy.loginfo(f"Rotating {angle} degrees")

        rate = rospy.Rate(20)
        while not rospy.is_shutdown():
            if abs(self.right_ticks - start_right) >= target_ticks:
                break
            self.cmd_pub.publish(msg)
            rate.sleep()

        self.stop_robot()
        rospy.sleep(0.8)

    def run_square(self, side_length):
        for side in range(4):
            if rospy.is_shutdown(): break
            rospy.loginfo(f"--- SIDE {side + 1} ---")
            self.move_straight(side_length, 0.4)
            self.rotate_in_place(90, 5.3)

        rospy.loginfo("Square completed successfully!")

if __name__ == '__main__':
    try:
        controller = SynchronizedSquare()
        controller.run_square(0.5) 
    except rospy.ROSInterruptException:
        pass
