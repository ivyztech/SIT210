#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from numpy import sign

class RobustAutoCalibration:
    def __init__(self):
        rospy.init_node('auto_calibration')
        self.robot_name = "mybota002446"
        
        # --- NEW CALIBRATED CONSTANTS ---
        # Calculation: 1350 / 0.80 = 1687.5
        self.TICKS_PER_METER = 1688 
        
        # --- DRIFT COMPENSATION (TRIM) ---
        # If drifting LEFT, use a small negative omega (right-hand steer)
        # Try values between -0.05 and -0.2
        self.TRIM_OMEGA = -0.1 

        self.current_ticks = 0
        self.cmd_pub = rospy.Publisher(f'/{self.robot_name}/car_cmd_switch_node/cmd', 
                                       Twist2DStamped, queue_size=1)
        
        # Using Right wheel as the master reference
        rospy.Subscriber(f'/{self.robot_name}/right_wheel_encoder_node/tick', 
                         WheelEncoderStamped, self.encoder_cb)
        
        rospy.loginfo("Node initialized. Ready for 1.0m test.")
        rospy.sleep(1.5)

    def encoder_cb(self, msg):
        self.current_ticks = msg.data

    def stop_robot(self):
        stop_msg = Twist2DStamped()
        stop_msg.v = 0.0
        stop_msg.omega = 0.0
        self.cmd_pub.publish(stop_msg)

    def drive_distance(self, meters, speed):
        start_ticks = self.current_ticks
        target_ticks = abs(meters * self.TICKS_PER_METER)
        
        msg = Twist2DStamped()
        msg.v = speed * sign(meters)
        msg.omega = self.TRIM_OMEGA # Applying the anti-drift correction
        
        rospy.loginfo(f"Executing {meters}m move. Target Ticks: {int(target_ticks)}")
        
        rate = rospy.Rate(50) # 50Hz control loop
        while not rospy.is_shutdown():
            # Check progress
            traveled = abs(self.current_ticks - start_ticks)
            
            if traveled >= target_ticks:
                break
                
            self.cmd_pub.publish(msg)
            rate.sleep()

        self.stop_robot()
        rospy.loginfo(f"Test Complete. Final Ticks: {abs(self.current_ticks - start_ticks)}")

if __name__ == '__main__':
    try:
        calibrator = RobustAutoCalibration()
        
        # Test 1: Straight 1.0 Meter
        # If it still drifts left, decrease TRIM_OMEGA (e.g., -0.15)
        # If it now drifts right, increase TRIM_OMEGA (e.g., -0.05)
        calibrator.drive_distance(meters=1.0, speed=0.4)
        
    except rospy.ROSInterruptException:
        pass
