#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from numpy import sign

class ClosedLoopRobot:
    def __init__(self):
        rospy.init_node('closed_loop_control')
        self.robot_name = "mybota002446"
        
        # --- YOUR CALIBRATED VALUES ---
        self.TICKS_PER_METER = 1688  # Fixed from your 0.80m test
        self.TICKS_PER_DEGREE = 4.5  # Estimated; we will calibrate this next!
        self.TRIM_OMEGA = -0.1       # Fixed your left drift
        
        self.current_ticks = 0
        self.cmd_pub = rospy.Publisher(f'/{self.robot_name}/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber(f'/{self.robot_name}/right_wheel_encoder_node/tick', WheelEncoderStamped, self.encoder_cb)
        
        rospy.loginfo("Robot Ready.")
        rospy.sleep(1)

    def encoder_cb(self, msg):
        self.current_ticks = msg.data

    def stop_robot(self):
        self.cmd_pub.publish(Twist2DStamped(v=0, omega=0))
        rospy.sleep(0.5) # Settle time

    # --- TASK: CLOSED LOOP STRAIGHTS ---
    def move_straight(self, distance, speed):
        start_ticks = self.current_ticks
        target_ticks = abs(distance * self.TICKS_PER_METER)
        
        msg = Twist2DStamped()
        msg.v = abs(speed) * sign(distance) # Correctly handles forward/backward
        msg.omega = self.TRIM_OMEGA if distance > 0 else -self.TRIM_OMEGA
        
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if abs(self.current_ticks - start_ticks) >= target_ticks:
                break
            self.cmd_pub.publish(msg)
            rate.sleep()
        self.stop_robot()

    # --- TASK: CLOSED LOOP ROTATIONS ---
    def rotate_in_place(self, angle, speed):
        start_ticks = self.current_ticks
        target_ticks = abs(angle * self.TICKS_PER_DEGREE)
        
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = abs(speed) * sign(angle) # Positive = CCW (Left), Negative = CW (Right)
        
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            if abs(self.current_ticks - start_ticks) >= target_ticks:
                break
            self.cmd_pub.publish(msg)
            rate.sleep()
        self.stop_robot()

if __name__ == '__main__':
    try:
        bot = ClosedLoopRobot()
        
        # --- DEMO 1: Straights (2 speeds, Fwd/Bwd) ---
        rospy.loginfo("Demo: Straight 0.5m Slow Forward")
        bot.move_straight(0.5, 0.2)
        
        rospy.loginfo("Demo: Straight 0.5m Fast Backward")
        bot.move_straight(-0.5, 0.5)
        
        # --- DEMO 2: Rotations (2 speeds, CW/CCW) ---
        rospy.loginfo("Demo: Rotate 90 deg Slow CCW (Left)")
        bot.rotate_in_place(90, 0.6)
        
        rospy.loginfo("Demo: Rotate 90 deg Fast CW (Right)")
        bot.rotate_in_place(-90, 1.2)
        
    except rospy.ROSInterruptException:
        pass
