import time

from gr00t.eval.real_robot.SO100.eval_so100 import So100Adapter
from gr00t.policy.server_client import PolicyClient
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import (
    SO101Follower,
    SO101FollowerConfig,
)

TASK = "pick up the green cylinder and place it in the black bowl on the left"

# Policy C predicts 16 actions.
# Execute 4, then capture new images and replan.
EXECUTION_HORIZON = 4
MAX_INFERENCE_CYCLES = 80
CONTROL_PERIOD = 0.12

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

    # Prevent a single command from producing a large jump.
    max_relative_target=4.0,

    # Always disable torque when the script stops.
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
                f"{key}={value:.3f}; "
                f"required [{lower:.1f}, {upper:.1f}]"
            )

    if errors:
        print("\nSTARTING POSE IS OUTSIDE THE SAFE WINDOW")

        for error in errors:
            print(" ", error)

        raise RuntimeError(
            "Move the torque-disabled arm back to mid-range."
        )


def validate_position(state):
    for key in STATE_KEYS[:5]:
        value = state[key]

        if value < -92.0 or value > 92.0:
            raise RuntimeError(
                f"{key} approached a joint boundary: {value:.3f}"
            )

    gripper = state["gripper.pos"]

    if gripper < -2.0 or gripper > 102.0:
        raise RuntimeError(
            f"Gripper approached a boundary: {gripper:.3f}"
        )


print("=" * 72)
print("POLICY C CHUNKED CLOSED-LOOP ROLLOUT")
print("=" * 72)
print("Task:", TASK)
print("Actions per prediction:", EXECUTION_HORIZON)
print("Maximum inference cycles:", MAX_INFERENCE_CYCLES)
print(
    "Maximum physical actions:",
    EXECUTION_HORIZON * MAX_INFERENCE_CYCLES,
)
print("Control period:", CONTROL_PERIOD, "seconds")
print("Press Ctrl+C at any time to stop safely.")

try:
    print("\nKeep the padded support under the arm.")
    print("Connecting robot and enabling torque...")

    robot.connect(calibrate=False)
    connected = True

    observation = robot.get_observation()
    start_state = state_from_observation(observation)

    print_state("STARTING POSITION", start_state)
    validate_start(start_state)

    # Command the current pose so the robot holds itself.
    robot.send_action(start_state)
    time.sleep(1.0)

    held_observation = robot.get_observation()
    held_state = state_from_observation(held_observation)

    print_state("POSITION WITH TORQUE ENABLED", held_state)
    validate_start(held_state)

    print("\nRobot is holding its starting pose.")
    print("Carefully remove the padded support.")
    print("Clear cables and obstacles from the workspace.")

    input("\nPress Enter to begin the Policy C rollout...")

    physical_action_count = 0

    for cycle in range(1, MAX_INFERENCE_CYCLES + 1):
        observation = robot.get_observation()
        observation["lang"] = TASK

        action_chunk = adapter.get_action(observation)

        available_actions = len(action_chunk)
        actions_to_execute = min(
            EXECUTION_HORIZON,
            available_actions,
        )

        print("\n" + "-" * 72)
        print(
            f"Inference cycle {cycle:02d}/"
            f"{MAX_INFERENCE_CYCLES}"
        )
        print(
            f"Received {available_actions} actions; "
            f"executing {actions_to_execute}"
        )

        for chunk_index in range(actions_to_execute):
            action = action_chunk[chunk_index]

            before_observation = robot.get_observation()
            before = state_from_observation(before_observation)

            robot.send_action(action)
            time.sleep(CONTROL_PERIOD)

            after_observation = robot.get_observation()
            after = state_from_observation(after_observation)

            validate_position(after)

            physical_action_count += 1

            changes = {
                key: after[key] - before[key]
                for key in STATE_KEYS
            }

            print(
                f"  Action {physical_action_count:03d} "
                f"(chunk {chunk_index + 1}/{actions_to_execute})"
            )
            print(
                "    "
                f"pan={changes['shoulder_pan.pos']:+.2f}, "
                f"lift={changes['shoulder_lift.pos']:+.2f}, "
                f"elbow={changes['elbow_flex.pos']:+.2f}, "
                f"wrist={changes['wrist_flex.pos']:+.2f}, "
                f"roll={changes['wrist_roll.pos']:+.2f}, "
                f"grip={changes['gripper.pos']:+.2f}"
            )

    print("\n" + "=" * 72)
    print("POLICY C CHUNKED ROLLOUT COMPLETED")
    print("Inference cycles:", MAX_INFERENCE_CYCLES)
    print("Physical actions:", physical_action_count)
    print("=" * 72)

except KeyboardInterrupt:
    print("\nPolicy C stopped by user.")

except Exception as error:
    print("\nPOLICY C SAFETY STOP:")
    print(error)

finally:
    if connected:
        print("\nDisconnecting robot and disabling torque...")
        try:
            robot.disconnect()
            print("Robot disconnected. Torque disabled.")
        except Exception as disconnect_error:
            print("WARNING: automatic disconnect failed:")
            print(disconnect_error)
            print("TURN OFF FOLLOWER ARM POWER MANUALLY.")
