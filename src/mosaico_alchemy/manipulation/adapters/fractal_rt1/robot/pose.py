from mosaicolabs import Message, Point3d, Pose, Quaternion

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class FractalRT1PoseAdapter(BaseAdapter[Pose]):
    """
    Adapter for `pose` topic from FractalRT1 datasets.

    Translated from `terminatposee_episode` message (custom Protocol Buffers) to
    `mosaicolabs.Pose`.
    """

    adapter_id = "fractal_rt1.pose"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "pose")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `pose` payload into a `mosaicolabs.Pose` message.

        Args:
            payload: Raw payload from the `pose` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Pose` data.
        """
        cls._validate_payload(payload=payload, constraints={"pose": {"len": 7}})
        pose = payload["pose"]
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Pose(
                position=Point3d.from_list(pose[:3]),
                orientation=Quaternion.from_list(pose[3:]),
            ),
        )
