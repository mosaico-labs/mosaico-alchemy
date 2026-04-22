from mosaicolabs import Message, Vector3d, Velocity

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class DroidVelocityAdapter(BaseAdapter):
    adapter_id = "droid.velocity"
    ontology_type = Velocity

    @classmethod
    def translate(cls, payload: dict) -> Message:
        velocity = payload.get("velocity")
        if velocity is None or len(velocity) != 6:
            velocity = [0.0] * 6

        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=Velocity(
                linear=Vector3d(
                    x=velocity[0],
                    y=velocity[1],
                    z=velocity[2],
                ),
                angular=Vector3d(
                    x=velocity[3],
                    y=velocity[4],
                    z=velocity[5],
                ),
            ),
        )
