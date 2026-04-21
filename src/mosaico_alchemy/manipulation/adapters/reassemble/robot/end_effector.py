from mosaicolabs import Message

from mosaicopacks.manipulation.adapters.base import BaseAdapter
from mosaicopacks.manipulation.ontology.end_effector import EndEffector


class ReassembleEndEffectorAdapter(BaseAdapter):
    adapter_id = "reassemble.end_effector"
    ontology_type = "end_effector"

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=EndEffector(
                efforts=payload.get("gripper_efforts"),
                positions=payload.get("gripper_positions"),
                velocities=payload.get("gripper_velocities"),
            ),
        )
