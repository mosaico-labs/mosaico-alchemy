from mosaicolabs import Message, RobotJoint

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class DroidJointStateAdapter(BaseAdapter):
    adapter_id = "droid.joint_state"
    ontology_type = RobotJoint

    JOINT_NAMES = [f"joint_{i}" for i in range(1, 8)]

    @classmethod
    def translate(cls, payload: dict) -> Message:
        pos = payload.get("position", [])
        vel = payload.get("velocity", [])

        pos = list(pos) if pos is not None else []
        vel = list(vel) if vel is not None else []

        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=RobotJoint(
                names=cls.JOINT_NAMES if len(pos) else [],
                positions=pos,
                velocities=vel if len(vel) > 0 else [0.0] * len(pos),
                efforts=[0.0] * len(pos),
            ),
        )
