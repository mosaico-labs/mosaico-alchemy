from mosaicolabs import Message, Point3d, Pose, Quaternion

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class FractalRT1PoseAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.pose"
    ontology_type = Pose

    @classmethod
    def translate(cls, payload: dict) -> Message:
        pose = payload.get("pose")

        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=Pose(
                position=Point3d(x=pose[0], y=pose[1], z=pose[2]),
                orientation=Quaternion(
                    x=pose[3],
                    y=pose[4],
                    z=pose[5],
                    w=pose[6],
                ),
            ),
        )
