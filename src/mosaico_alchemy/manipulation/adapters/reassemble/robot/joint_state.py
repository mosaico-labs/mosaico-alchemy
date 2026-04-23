from mosaicolabs import Message, RobotJoint

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleJointStateAdapter(BaseAdapter):
    adapter_id = "reassemble.joint_state"
    ontology_type = RobotJoint

    JOINT_NAMES = [f"joint_{i}" for i in range(1, 8)]

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=RobotJoint(
                names=cls.JOINT_NAMES,
                positions=payload.get("position"),
                velocities=payload.get("velocity"),
                efforts=payload.get("effort"),
            ),
        )
