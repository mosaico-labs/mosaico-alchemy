from mosaicolabs import Message, Point3d, Pose, Quaternion
from scipy.spatial.transform import Rotation as R

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidPoseAdapter(BaseAdapter[Pose]):
    """
    Adapter for `pose` data in DROID datasets.

    Translates `pose` data from the dataset's message format to the
    `mosaicolabs.Pose` ontology type.
    """

    adapter_id = "droid.pose"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp", "pose")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `pose` payload into a `mosaicolabs.Pose` message.

        Args:
            payload: Raw payload from the `pose` topic.

        Returns:
            A `Message` containing the `mosaicolabs.Pose` data.
        """
        cls._validate_payload(payload=payload, constraints={"pose": {"len": 6}})
        x, y, z, rx, ry, rz = payload["pose"]
        quat = R.from_euler("xyz", [rx, ry, rz]).as_quat()

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Pose(
                position=Point3d(x=x, y=y, z=z),
                orientation=Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3]),
            ),
        )
