from mosaicolabs import ForceTorque, Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleMeasuredForceTorqueAdapter(BaseAdapter):
    adapter_id = "reassemble.measured_force_torque"
    ontology_type = ForceTorque

    @classmethod
    def translate(cls, payload: dict) -> Message:
        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=ForceTorque(
                force=Vector3d(
                    x=payload.get("measured_force")[0],
                    y=payload.get("measured_force")[1],
                    z=payload.get("measured_force")[2],
                ),
                torque=Vector3d(
                    x=payload.get("measured_torque")[0],
                    y=payload.get("measured_torque")[1],
                    z=payload.get("measured_torque")[2],
                ),
            ),
        )
