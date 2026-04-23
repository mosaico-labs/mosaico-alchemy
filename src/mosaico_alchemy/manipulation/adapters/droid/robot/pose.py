from mosaicolabs import Message, Point3d, Pose, Quaternion
from scipy.spatial.transform import Rotation as R

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class DroidPoseAdapter(BaseAdapter):
    adapter_id = "droid.pose"
    ontology_type = Pose

    @classmethod
    def translate(cls, payload: dict) -> Message:
        pose = payload.get("pose")

        if pose is None or len(pose) != 6:
            pose = [0.0] * 6

        x, y, z, rx, ry, rz = pose
        quat = R.from_euler("xyz", [rx, ry, rz]).as_quat()

        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Pose(
                position=Point3d(x=x, y=y, z=z),
                orientation=Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3]),
            ),
        )
