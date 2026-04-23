from mosaicolabs import Message, Point3d, Pose, Quaternion

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassemblePoseAdapter(BaseAdapter):
    adapter_id = "reassemble.pose"
    ontology_type = Pose

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Pose(
                position=Point3d(
                    x=payload.get("pose")[0],
                    y=payload.get("pose")[1],
                    z=payload.get("pose")[2],
                ),
                orientation=Quaternion(
                    x=payload.get("pose")[3],
                    y=payload.get("pose")[4],
                    z=payload.get("pose")[5],
                    w=payload.get("pose")[6],
                ),
            ),
        )
