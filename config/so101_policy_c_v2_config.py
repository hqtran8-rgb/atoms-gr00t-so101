from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


policy_c_v2_config = {
    "video": ModalityConfig(
        delta_indices=[0],
        modality_keys=[
            "front",
            "wrist",
        ],
    ),

    "state": ModalityConfig(
        delta_indices=[0],
        modality_keys=[
            "single_arm",
            "gripper",
        ],
    ),

    "action": ModalityConfig(
        # Preserve the original Policy C execution horizon.
        delta_indices=list(range(16)),
        modality_keys=[
            "single_arm",
            "gripper",
        ],
        action_configs=[
            # Five arm joints: convert absolute dataset targets to relative actions.
            ActionConfig(
                rep=ActionRepresentation.RELATIVE,
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),

            # Gripper remains an absolute target.
            ActionConfig(
                rep=ActionRepresentation.ABSOLUTE,
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),
        ],
    ),

    "language": ModalityConfig(
        delta_indices=[0],
        modality_keys=[
            "annotation.human.task_description",
        ],
    ),
}


register_modality_config(
    policy_c_v2_config,
    embodiment_tag=EmbodimentTag.NEW_EMBODIMENT,
)
