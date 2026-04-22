from mosaicolabs import ForceTorque, Message, Vector3d

from mosaicopacks.manipulation.adapters.base import BaseAdapter


class ReassembleCompensatedBaseForceTorqueAdapter(BaseAdapter):
    adapter_id = "reassemble.compensated_base_force_torque"
    ontology_type = ForceTorque

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=ForceTorque(
                force=Vector3d(
                    x=payload.get("compensated_base_force")[0],
                    y=payload.get("compensated_base_force")[1],
                    z=payload.get("compensated_base_force")[2],
                ),
                torque=Vector3d(
                    x=payload.get("compensated_base_torque")[0],
                    y=payload.get("compensated_base_torque")[1],
                    z=payload.get("compensated_base_torque")[2],
                ),
            ),
        )
