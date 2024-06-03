import json
import logging
from asyncio import sleep

from .environment import Environment
from .envvars import *

log = logging.getLogger(__name__)


def _dist_yaw(src, tgt):
    return ((tgt-src+180) % 360)-180


class SimEnv(Environment):
    """
    This class abstracts out the robomaster code for testing.
    """

    def __init__(self, uri: str) -> None:
        super().__init__(uri)

        self.update_freq = 20
        self.velocity = YAW_SPEED / self.update_freq
        # initialize yaw
        self.camera_yaw = 0

    async def update_sim(self) -> None:
        # log.info("sending data")
        await self.send_websocket(
            json.dumps({"type": "update", "yaw": self.camera_yaw})
        )

    # MOVEMENT CODE
    async def pan_cannon(self, change):
        """Pans the cannon in the horizontal direction"""
        while abs(diff := _dist_yaw(self.camera_yaw, change)) > YAW_TOL:
            await sleep(1 / self.update_freq)
            sign = 1 if diff > 0 else -1
            self.camera_yaw += min(abs(diff), self.velocity) * sign
            await self.update_sim()

    async def reset_pan_cannon(self):
        await self.pan_cannon(-self.camera_yaw)

    def stop_cannon(self):
        """Stop the cannon and reset the velocity"""
        pass

    async def exit(self):
        """Clean up and exit"""
        await self._close_websocket()

    def get_yaw(self):
        return self.camera_yaw
