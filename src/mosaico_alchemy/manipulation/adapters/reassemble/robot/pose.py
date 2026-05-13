from mosaicolabs import Message, Point3d, Pose, Quaternion

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassemblePoseAdapter(BaseAdapter[Pose]):
    """
    Adapter for `pose` data in Reassemble datasets.

    Translates `pose` data from the dataset's message format to the
    `mosaicolabs.Pose` ontology type.
    """

    adapter_id = "reassemble.pose"
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
        cls._validate_payload(
            payload=payload,
            constraints={
                "pose": {"len": 7},
            },
        )

        pose = payload["pose"]

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=Pose(
                position=Point3d.from_list(pose[:3]),
                orientation=Quaternion.from_list(pose[3:]),
            ),
        )
