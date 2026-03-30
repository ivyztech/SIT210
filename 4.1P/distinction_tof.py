#!/usr/bin/env python3
import rospy
from duckietown_msgs.msg import Twist2DStamped, WheelEncoderStamped
from sensor_msgs.msg import Range # ToF sensor uses the standard Range message
from numpy import sign

class CollisionAwareSquare:
    def __init__(self):
        rospy.init_node('collision_aware_control')
        
        # --- Constants & Thresholds ---
        self.TICKS_PER_METER = 1350
        self.TICKS_PER_DEGREE = 4.2
        self.STOP_THRESHOLD = 0.15 # 15cm stopping distance
        
        # State Variables
        self.current_ticks = 0
        self.tof_range = 1.0 # Initialize with a clear path
        self.is_paused = False
        
        # Pubs/Subs
        self.cmd_pub = rospy.Publisher('/akandb/car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('/akandb/right_wheel_encoder_node/tick', WheelEncoderStamped, self.encoder_cb)
        rospy.Subscriber('/akandb/front_center_tof_driver_node/range', Range, self.tof_cb)
        
        rospy.sleep(1)

    def encoder_cb(self, msg):
        self.current_ticks = msg.data

    def tof_cb(self, msg):
        self.tof_range = msg.range

    def stop_robot(self):
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = 0.0
        self.cmd_pub.publish(msg)

    def move_straight(self, distance, speed):
        start_ticks = self.current_ticks
        target_ticks = abs(distance * self.TICKS_PER_METER)
        traveled_ticks = 0
        
        rospy.loginfo(f"Moving {distance}m. Collision prevention ACTIVE.")

        while traveled_ticks < target_ticks and not rospy.is_shutdown():
            # Check for obstacle (only if moving forward)
            if distance > 0 and self.tof_range < self.STOP_THRESHOLD:
                if not self.is_paused:
                    rospy.logwarn("Obstacle detected! Braking...")
                    self.is_paused = True
                self.stop_robot()
            else:
                if self.is_paused:
                    rospy.loginfo("Path clear. Resuming...")
                    self.is_paused = False
                
                # Command movement
                msg = Twist2DStamped()
                msg.v = speed * sign(distance)
                msg.omega = 0.0
                self.cmd_pub.publish(msg)
                
                # Update progress only when moving
                traveled_ticks = abs(self.current_ticks - start_ticks)
            
            rospy.sleep(0.01)
            
        self.stop_robot()
        rospy.sleep(0.5)

    def rotate_in_place(self, angle, speed):
        # Collision prevention NOT active here as per requirements
        start_ticks = self.current_ticks
        target_ticks = abs(angle * self.TICKS_PER_DEGREE)
        
        msg = Twist2DStamped()
        msg.v = 0.0
        msg.omega = speed * sign(angle)
        
        while abs(self.current_ticks - start_ticks) < target_ticks and not rospy.is_shutdown():
            self.cmd_pub.publish(msg)
            rospy.sleep(0.01)
            
        self.stop_robot()
        rospy.sleep(0.5)

    def run_square(self):
        for side in range(4):
            self.move_straight(1.0, 0.4)
            self.rotate_in_place(90, 1.2)

if __name__ == '__main__':
    try:
        node = CollisionAwareSquare()
        node.run_square()
    except rospy.ROSInterruptException:
        pass
