from mosaicolabs import Message, RobotJoint

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleJointStateAdapter(BaseAdapter[RobotJoint]):
    """
    Adapter for `joint_state` topic from Reassemble datasets.

    Translated from `joint_state` message (custom Protocol Buffers) to
    `mosaicolabs.RobotJoint`.
    """

    adapter_id = "reassemble.joint_state"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "position", "velocity", "effort")
    JOINT_NAMES = [f"joint_{i}" for i in range(1, 8)]

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `joint_state` payload into a `mosaicolabs.RobotJoint` message.

        Args:
            payload: Raw payload from the `joint_state` topic.

        Returns:
            A `Message` containing the `mosaicolabs.RobotJoint` data.
        """
        cls._validate_payload(
            payload=payload,
            constraints={
                "position": {"not_empty": True},
                "velocity": {"not_empty": True},
                "effort": {"not_empty": True},
            },
        )

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=RobotJoint(
                names=cls.JOINT_NAMES,
                positions=payload["position"],
                velocities=payload["velocity"],
                efforts=payload["effort"],
            ),
        )
