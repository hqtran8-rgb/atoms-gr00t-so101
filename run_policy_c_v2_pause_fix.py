import os
import select
import sys
import termios
import time
import tty

from gr00t.eval.real_robot.SO100.eval_so100 import So100Adapter
from gr00t.policy.server_client import PolicyClient
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig


TASK = "pick up the green cylinder and place it in the black bowl on the left"

EXECUTION_HORIZON = 4
MAX_INFERENCE_CYCLES = 60
CONTROL_PERIOD = 0.12

MANUAL_OPEN_STEP = 4.0
MANUAL_OPEN_LIMIT = 35.0

STATE_KEYS = [
    "shoulder_pan.pos",
    "shoulder_lift.pos",
    "elbow_flex.pos",
    "wrist_flex.pos",
    "wrist_roll.pos",
    "gripper.pos",
]

START_RANGES = {
    "shoulder_pan.pos": (-20.0, 35.0),
    "shoulder_lift.pos": (-70.0, -25.0),
    "elbow_flex.pos": (20.0, 80.0),
    "wrist_flex.pos": (35.0, 80.0),
    "wrist_roll.pos": (-20.0, 20.0),
    "gripper.pos": (0.0, 45.0),
}

cameras = {
    "front": OpenCVCameraConfig(
        index_or_path="/dev/video_front",
        width=640,
        height=480,
        fps=30,
    ),
    "wrist": OpenCVCameraConfig(
        index_or_path="/dev/video_handeye",
        width=640,
        height=480,
        fps=30,
    ),
}

robot_config = SO101FollowerConfig(
    id="my_follower",
    port="/dev/ttyACM1",
    cameras=cameras,
    max_relative_target=4.0,
    disable_torque_on_disconnect=True,
    use_degrees=False,
)

robot = SO101Follower(robot_config)

client = PolicyClient(
    host="127.0.0.1",
    port=5555,
)

adapter = So100Adapter(client)

connected = False
hotkeys_enabled = False
terminal_state = None


def state_from_observation(observation):
    return {
        key: float(observation[key])
        for key in STATE_KEYS
    }


def print_state(title, state):
    print("\n" + title)

    for key in STATE_KEYS:
        print(f"  {key:20}: {state[key]:8.3f}")


def validate_start(state):
    errors = []

    for key, value in state.items():
        lower, upper = START_RANGES[key]

        if value < lower or value > upper:
            errors.append(
                f"{key}={value:.3f}; required [{lower:.1f}, {upper:.1f}]"
            )

    if errors:
        print("\nSTARTING POSE IS OUTSIDE THE SAFE WINDOW")

        for error in errors:
            print(" ", error)

        raise RuntimeError(
            "Move the torque-disabled arm back to thelower:.1f}, {upper:.1f}]"
            )

    if errors:
        print("\nSTARTING POSE IS OUTSIDE THE SAFE demonstrated start pose."
        )


def validate_position(state):
    for key in STATE_KEYS[:5]:
        value = state[key]

        # Stop before the previous 92-degree boundary failure.
        if value < -88.0 or value > 88.0:
            raise RuntimeError(
                f"{key} approached the soft joint boundary: {value:.3f}"
            )

    gripper = state["gripper.pos"]

    if gripper < -2.0 or gripper > 102.0:
        raise RuntimeError(
            f"Gripper approached a boundary: {gripper:.3f}"
        )


def enable_hotkeys():
    global terminal_state

    if not sys.stdin.isatty():
        raise RuntimeError("Hotkeys require an interactive terminal.")

    terminal_state = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())


def restore_hotkeys():
    global terminal_state

    if terminal_state is not None:
        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            terminal_state,
        )
        terminal_state = None


def poll_key():
    ready, _, _ = select.select([sys.stdin], [], [], 0.0)

    if not ready:
        return None

    return sys.stdin.read(1).lower()


def pause_fix():
    current = state_from_observation(robot.get_observation())

    # Hold the follower at its current pose.
    robot.send_action(current)
    time.sleep(0.25)

    print("\n" + "=" * 72)
    print("ROLLOUT PAUSED")
    print("o = open gripper by 4")
    print("r = resume with a fresh prediction")
    print("q = stop safely")
    print("=" * 72)

    while True:
        key = sys.stdin.read(1).lower()

        if key in ("r", " "):
            print("\nResuming with a fresh observation...")
            return

        if key == "q":
            raise KeyboardInterrupt

        if key == "o":
            current = state_from_observation(
                robot.get_observation()
            )

            before = current["gripper.pos"]
            target = min(
                MANUAL_OPEN_LIMIT,
                before + MANUAL_OPEN_STEP,
            )

            action = dict(current)
            action["gripper.pos"] = target

            robot.send_action(action)
            time.sleep(0.35)

            after = state_from_observation(
                robot.get_observation()
            )

            print(
                f"\nManual gripper opening: "
                f"{before:.3f} -> {after['gripper.pos']:.3f}"
            )


print("=" * 72)
print("POLICY C V2 PAUSE-FIX ROLLOUT")
print("=" * 72)
print("Task:", TASK)
print("Actions per prediction:", EXECUTION_HORIZON)
print("Maximum inference cycles:", MAX_INFERENCE_CYCLES)
print("Maximum physical actions:",
      EXECUTION_HORIZON * MAX_INFERENCE_CYCLES)
print("Control period:", CONTROL_PERIOD, "seconds")

try:
    print("\nKeep the padded support under the arm.")
    print("Connecting robot and enabling torque...")

    robot.connect(calibrate=False)
    connected = True

    observation = robot.get_observation()
    start_state = state_from_observation(observation)

    print_state("STARTING POSITION", start_state)
    validate_start(start_state)

    robot.send_action(start_state)
    time.sleep(1.0)

    held_state = state_from_observation(
        robot.get_observation()
    )

    print_state("POSITION WITH TORQUE ENABLED", held_state)
    validate_start(held_state)

    print("\nRobot is holding its starting position.")
    print("Remove the support and clear the workspace.")

    input("\nPress Enter to begin the rollout...")

    enable_hotkeys()
    hotkeys_enabled = True

    print("\nLIVE CONTROLS")
    print("p = pause")
    print("q = stop")
    print("During pause: o = open, r = resume")

    physical_action_count = 0

    for cycle in range(1, MAX_INFERENCE_CYCLES + 1):
        observation = robot.get_observation()
        observation["lang"] = TASK

        action_chunk = adapter.get_action(observation)

        actions_to_execute = min(
            EXECUTION_HORIZON,
            len(action_chunk),
        )

        print("\n" + "-" * 72)
        print(
            f"Inference cycle {cycle:02d}/"
            f"{MAX_INFERENCE_CYCLES}"
        )
        print(
            f"Received {len(action_chunk)} actions; "
            f"executing {actions_to_execute}"
        )

        for chunk_index in range(actions_to_execute):
            key = poll_key()

            if key == "p":
                pause_fix()

                # Discard remaining stale actions and replan.
                break

            if key == "q":
                raise KeyboardInterrupt

            action = action_chunk[chunk_index]

            robot.send_action(action)
            time.sleep(CONTROL_PERIOD)

            after = state_from_observation(
                robot.get_observation()
            )

            validate_position(after)

            physical_action_count += 1

            print(
                f"  Action {physical_action_count:03d} "
                f"(chunk {chunk_index + 1}/"
                f"{actions_to_execute})"
            )

    print("\nPOLICY C V2 ROLLOUT COMPLETED")

except KeyboardInterrupt:
    print("\nPolicy C v2 stopped by user.")

except Exception as error:
    print("\nPOLICY C V2 SAFETY STOP:")
    print(error)

finally:
    if hotkeys_enabled:
        restore_hotkeys()

    if connected:
        print("\nDisconnecting robot and disabling torque...")

        try:
            robot.disconnect()
            print("Robot disconnected. Torque disabled.")

        except Exception as disconnect_error:
            print("WARNING: automatic disconnect failed:")
            print(disconnect_error)
            print("TURN OFF FOLLOWER ARM POWER MANUALLY.")

            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(2)
