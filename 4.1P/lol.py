#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from numpy import sign

class ClosedLoopRobot:
    def __init__(self):
        rospy.init_node('closed_loop_control')
        self.robot_name = "mybota002446"
        
        # --- CALIBRATED CONSTANTS ---
        self.TICKS_PER_METER = 1688   # Based on your 0.80m test
        self.TICKS_PER_DEGREE = 4.5    # Starting guess for rotation
        self.TRIM_OMEGA = -0.1         # Corrects left drift
        
        # Encoder states
        self.left_ticks = 0
        self.right_ticks = 0
        
        # Publisher
        self.cmd_pub = rospy.Publisher(f'/{self.robot_name}/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        
        # Subscribers for BOTH wheels to prevent "stuck" logic
        rospy.Subscriber(f'/{self.robot_name}/left_wheel_encoder_node/tick', WheelEncoderStamped, self.left_cb)
        rospy.Subscriber(f'/{self.robot_name}/right_wheel_encoder_node/tick', WheelEncoderStamped, self.right_cb)
        
        rospy.loginfo("Robot initialized and listening to both encoders.")
        rospy.sleep(1)

    def left_cb(self, msg):
        self.left_ticks = msg.data

    def right_cb(self, msg):
        self.right_ticks = msg.data

    def stop_robot(self):
        self.cmd_pub.publish(Twist2DStamped(v=0, omega=0))
        rospy.sleep(0.5)

    def move_straight(self, distance, speed):
        # Use average of both wheels for linear distance
        start_avg = (self.left_ticks + self.right_ticks) / 2.0
        target_ticks = abs(distance * self.TICKS_PER_METER)
        
        msg = Twist2DStamped()
        msg.v = abs(speed) * sign(distance)
        msg.omega = self.TRIM_OMEGA if distance > 0 else -self.TRIM_OMEGA
        
        rate = rospy.Rate(50)
        while not rospy.is_shutdown():
            current_avg = (self.left_ticks + self.right_ticks) / 2.0
            if abs(current_avg - start_avg) >= target_ticks:
                break
            self.cmd_pub.publish(msg)
            rate.sleep()
        self.stop_robot()

    def rotate_in_place(self, angle, speed):
        # During rotation, wheels move in opposite directions. 
        # We track the absolute change in the right wheel specifically, 
        # but the timeout ensures we don't get stuck.
        start_r = self.right_ticks
        start_l = self.left_ticks
        target_ticks = abs(angle * self.TICKS_PER_DEGREE)
        
        msg = Twist2DStamped(v=0.0, omega=abs(speed) * sign(angle))
        
        rate = rospy.Rate(50)
        timeout_start = rospy.get_time()

        while not rospy.is_shutdown():
            # If the right wheel is stuck, we use the left wheel as a backup
            dist_r = abs(self.right_ticks - start_r)
            dist_l = abs(self.left_ticks - start_l)
            max_dist = max(dist_r, dist_l)

            if max_dist >= target_ticks:
                break
            
            if rospy.get_time() - timeout_start > 10.0:
                rospy.logwarn("Rotation Timeout - Check hardware!")
                break

            self.cmd_pub.publish(msg)
            rate.sleep()
        self.stop_robot()

    def run_square(self):
        rospy.loginfo("Starting 1m Square Task...")
        for side in range(4):
            rospy.loginfo(f"Driving Side {side + 1}")
            self.move_straight(1.0, 0.4)
            rospy.loginfo(f"Turning Corner {side + 1}")
            self.rotate_in_place(90, 0.8)
        rospy.loginfo("Square Complete!")

if __name__ == '__main__':
    try:
        bot = ClosedLoopRobot()
        
        # Demo 1: Straights
        bot.move_straight(0.5, 0.3)
        bot.move_straight(-0.5, 0.3)
        
        # Demo 2: Rotations
        bot.rotate_in_place(90, 0.8)
        bot.rotate_in_place(-90, 0.8)
        
        # Final Task
        bot.run_square()
        
    except rospy.ROSInterruptException:
        pass
