import os

from dotenv import load_dotenv

load_dotenv()

TEAM_NAME = os.getenv("TEAM_NAME", "Team Name")
SERVER_IP = os.getenv("COMPETITION_SERVER_IP", "host.docker.internal")
SERVER_PORT = os.getenv("COMPETITION_SERVER_PORT", "8000")
ROBOT_IP = os.getenv("ROBOT_IP", "192.168.10.10")
ROBOT_SN = os.getenv("ROBOT_SN", "ABC123")
USE_ROBOT = os.getenv("USE_ROBOT", "false").lower() in [
    "true", "1", "t", "y", "yes"]

# https://robomaster-dev.readthedocs.io/en/latest/python_sdk/robomaster.html#robomaster.gimbal.Gimbal.moveto
# TODO: Use env var on irl session to test the maximum speed
YAW_SPEED = int(os.getenv("YAW_SPEED", 60))
YAW_TOL = int(os.getenv("YAW_TOL", 2))
