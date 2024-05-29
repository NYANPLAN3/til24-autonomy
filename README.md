# til24-autonomy

Template for FastAPI-based API server. Features:

- Supports both CPU/GPU-accelerated setups automatically.
- Poetry for package management.
- Ruff for formatting & linting.
- VSCode debugging tasks.
- Other QoL packages.

Oh yeah, this template should work with the fancy "Dev Containers: Clone Repository
in Container Volume..." feature.

## Usage Instructions

- Replace all instances of `til24-autonomy`. Optionally, rename `src` to a nicer name.
  - Tip: Rename the `src` folder first for auto-refactoring.

## Useful Commands

Ensure the virtual environment is active and `poetry install` has been run before using the below:

```sh
# Launch debugging server, use VSCode's debug task instead by pressing F5.
poe dev
# Run any tests.
poe test
# Build docker image for deployment; will also be tagged as latest.
poe build {insert_version_like_0.1.0}
# Run the latest image locally.
poe prod
# Publish the latest image.
poe publish
```

# TIL-Autonomy

This is the container responsible for controlling your robot, and should at minimum be able to handle:

- turning to a particular heading, and
- taking a snapshot from the simulator.

The main entrypoint is `autonomy.py`, which uses all the OS environment variables passed in from the `.env` through the `docker-compose.yml` in the parent directory to configure the required connections (e.g. to the robot, to the competition server, etc). The other files are:

- `environment.py` defines an abstract class of functions that the other two environments must fulfill. It handles the WebSocket connection to the competition server autonomy endpoint.
- `robot_env.py` defines the autonomy environment controlling the actual robot. The robot's gimbal rotation is used to update the simulator
- `sim_env.py` defines the autonomy environment controlling the simulator directly.

## Setup

You can build the autonomy Docker container individually with `docker build -t autonomy .` or you can set up the whole system by running `docker compose up` from the main directory.

## Notes

The pitch is set to 15 because an air defense turret should aim upwards. Any pitch rotations you make will not modify the display on the simulator, and are thus unnecessary.
