from mosaicolabs import Message, RobotJoint

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidJointStateAdapter(BaseAdapter[RobotJoint]):
    """
    Adapter for `joint_state` topic from DROID datasets.

    Translated from `joint_state` message (custom Protocol Buffers) to
    `mosaicolabs.RobotJoint`.
    """

    adapter_id = "droid.joint_state"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp",)
    _AT_LEAST_ONE: tuple[str, ...] = ("position", "velocity")

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
        )
        positions = list(payload.get("position", []))
        velocities = list(payload.get("velocity", []))

        tstamp_sec = payload["timestamp"]

        return Message(
            timestamp_ns=int(tstamp_sec * 1e9),
            data=RobotJoint(
                names=cls.JOINT_NAMES,
                positions=positions,
                velocities=velocities,
                # Efforts are not provided in DROID, so we set them to zero
                efforts=[],
            ),
        )
