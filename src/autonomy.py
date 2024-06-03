from __future__ import annotations

if True:
    from .envvars import *

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response

from .environment import Environment
from .log import setup_logging
from .robot_env import RobotEnv
from .sim_env import SimEnv

env: Environment | None = None

setup_logging()
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global env
    # initialize websocket with competition server
    if USE_ROBOT:
        log.info("!!!Real robot mode!!!")
        assert ROBOT_IP, "No robot IP provided"
        assert ROBOT_SN, "No robot serial number provided"
        log.info(
            f"robot ip: {ROBOT_IP}; robot sn: {ROBOT_SN}; team name: {TEAM_NAME}; server: {SERVER_IP}:{SERVER_PORT}"
        )
        env = RobotEnv(
            uri=f"ws://{SERVER_IP}:{SERVER_PORT}/ws_auto/{TEAM_NAME}",
            robot_sn=ROBOT_SN,
            robot_ip=ROBOT_IP,
            local_ip="0.0.0.0",
        )
    else:
        log.info(f"using simulator at {SERVER_IP}:{SERVER_PORT}")
        env = SimEnv(f"ws://{SERVER_IP}:{SERVER_PORT}/ws_auto/{TEAM_NAME}")
    await env._init_websocket()
    yield
    await env.exit()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "This is the API service for TIL-autonomy"}


@app.get("/health")
async def health():
    if env.health():
        return {"health": "ok"}
    else:
        return HTTPException(503, "websocket not initialized")


@app.post("/send_heading")
async def send_heading(request: Request):
    request_dict = await request.json()

    heading = request_dict["heading"]
    # depends on how your team would like to implement the robotics component
    heading = int(heading)
    if heading > 180:
        heading -= 360
    # rotate to heading
    log.info(f"Rotating to heading: {request_dict['heading']} ({heading})")
    await env.pan_cannon(heading)
    log.info("Waiting for snapshot...")
    b_image: bytes = await env.take_snapshot()
    return Response(content=b_image, media_type="image/jpeg")


# optional, depends on how your team would like to implement the robotics component
@app.post("/reset_cannon")
async def reset_cannon():
    await env.reset_pan_cannon()
    return {"message": "done"}

log.info("Autonomy App Ready.")
