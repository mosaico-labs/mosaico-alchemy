from mosaicolabs import Message, Vector3d, Velocity

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class ReassembleVelocityAdapter(BaseAdapter):
    adapter_id = "reassemble.velocity"
    ontology_type = Velocity

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Velocity(
                linear=Vector3d(
                    x=payload.get("velocity")[0],
                    y=payload.get("velocity")[1],
                    z=payload.get("velocity")[2],
                ),
                angular=Vector3d(
                    x=payload.get("velocity")[3],
                    y=payload.get("velocity")[4],
                    z=payload.get("velocity")[5],
                ),
            ),
        )
