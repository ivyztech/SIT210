#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped

class AutoCalibration:
    def __init__(self):
        rospy.init_node('auto_calibration')
        self.robot_name = "mybota002446" # Your specific robot
        
        self.current_ticks = 0
        self.cmd_pub = rospy.Publisher(f'/{self.robot_name}/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber(f'/{self.robot_name}/right_wheel_encoder_node/tick', WheelEncoderStamped, self.encoder_cb)
        
        rospy.loginfo("Calibration node started. Waiting for sync...")
        rospy.sleep(1)

    def encoder_cb(self, msg):
        self.current_ticks = msg.data

    def drive_test(self, target_ticks, speed):
        start_ticks = self.current_ticks
        msg = Twist2DStamped()
        msg.v = speed
        msg.omega = 0.0

        rospy.loginfo(f"Starting movement. Target: {target_ticks} ticks.")
        
        while abs(self.current_ticks - start_ticks) < target_ticks and not rospy.is_shutdown():
            self.cmd_pub.publish(msg)
            rospy.sleep(0.01)

        # Stop and report
        msg.v = 0.0
        self.cmd_pub.publish(msg)
        actual_ticks = abs(self.current_ticks - start_ticks)
        rospy.loginfo(f"STOPPED. Total Ticks Recorded: {actual_ticks}")
        rospy.loginfo("Now, measure the distance on the floor with a ruler!")

if __name__ == '__main__':
    try:
        calibrator = AutoCalibration()
        # Step 1: Drive what we THINK is 1 meter (1350 ticks)
        calibrator.drive_test(target_ticks=1350, speed=0.4)
    except rospy.ROSInterruptException:
        pass
