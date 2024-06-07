import asyncio
import json
import logging

from robomaster import config
from robomaster.robot import Robot

from .environment import Environment
from .envvars import *

log = logging.getLogger(__name__)


def _dist_yaw(src, tgt):
    return ((tgt-src+180) % 360)-180


class RobotEnv(Environment):
    """
    This class provides the primitive actions to control the actual robomaster
    """

    def __init__(self, uri: str, robot_sn: str, robot_ip: str, local_ip: str) -> None:
        # initialize websocket with competition server
        super().__init__(uri)

        self._init_params()
        # === Initialize robot ===
        config.LOCAL_IP_STR = local_ip
        config.ROBOT_IP_STR = robot_ip
        self.robot = Robot()
        self.loop = asyncio.get_event_loop()

        self.robot.initialize(conn_type="sta", sn=robot_sn)
        self.robot.set_robot_mode(mode="free")
        self.robot.gimbal.recenter().wait_for_completed()
        self.robot.gimbal.move(pitch=15).wait_for_completed()

        # keep track of angle from gimbal
        self.camera_yaw = 0

        # NOTE: We didn't change it :)
        # this is responsible for updating the position on the simulator
        # as such, DO NOT TOUCH THIS
        def sub_data_handler(angle_info):
            _, self.camera_yaw, _, _ = angle_info

            # log.info(f"yaw: {self.camera_yaw}")
            # responsible for updating the server
            self.loop.create_task(
                self.send_websocket(
                    json.dumps(
                        {
                            "type": "update",
                            "yaw": self.camera_yaw,
                        }
                    )
                )
            )

        # DO NOT TOUCH THIS EITHER
        self.robot.gimbal.sub_angle(freq=20, callback=sub_data_handler)

    async def wait_for_action(action):
        while not action.is_completed:
            await asyncio.sleep(0)

    # NOTE: we use moveto since that is the robot's guarantee that it will go to that heading.
    async def pan_cannon(self, change) -> None:
        """Pans the cannon in the horizontal direction"""
        while abs(_dist_yaw(self.camera_yaw, change)) > YAW_TOL:
            await RobotEnv.wait_for_action(self.robot.gimbal.moveto(yaw=change, yaw_speed=YAW_SPEED))

    # NOTE: moveto was used instead of recenter to avoid changing pitch.
    async def reset_pan_cannon(self) -> None:
        await RobotEnv.wait_for_action(self.robot.gimbal.moveto(yaw=0))

    async def exit(self) -> None:
        """
        Disconnect the robot
        """
        self.robot.gimbal.unsub_angle()
        self.robot.close()

        await self._close_websocket()

    def stop_cannon(self):
        self.robot.gimbal.drive_speed(yaw_speed=0)

    def get_yaw(self) -> float:
        return self.camera_yaw
