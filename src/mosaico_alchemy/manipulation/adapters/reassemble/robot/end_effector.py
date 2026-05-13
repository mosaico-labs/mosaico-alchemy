from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.end_effector import EndEffector


class ReassembleEndEffectorAdapter(BaseAdapter[EndEffector]):
    """
    Adapter for `end_effector` data in Reassemble datasets.

    Translates `end_effector` data from the dataset's message format to the
    `EndEffector` ontology type.
    """

    adapter_id = "reassemble.end_effector"
    _REQUIRED_KEYS: tuple[str, ...] = (
        "timestamp",
        "gripper_efforts",
        "gripper_positions",
        "gripper_velocities",
    )

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `end_effector` payload into a `EndEffector` message.

        Args:
            payload: Raw payload from the `end_effector` topic.

        Returns:
            A `Message` containing the `EndEffector` data.
        """
        cls._validate_payload(
            payload=payload,
            constraints={
                "gripper_positions": {"not_empty": True},
                "gripper_velocities": {"not_empty": True},
                "gripper_efforts": {"not_empty": True},
            },
        )

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=EndEffector(
                positions=payload["gripper_positions"],
                velocities=payload["gripper_velocities"],
                efforts=payload["gripper_efforts"],
            ),
        )
