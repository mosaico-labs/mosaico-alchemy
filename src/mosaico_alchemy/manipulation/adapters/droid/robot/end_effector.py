import numpy as np
from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.end_effector import EndEffector


class DroidEndEffectorAdapter(BaseAdapter):
    adapter_id = "droid.end_effector"
    ontology_type = EndEffector

    @classmethod
    def translate(cls, payload: dict) -> Message:
        pos = payload.get("position", 0.0)
        vel = payload.get("velocity", 0.0)

        positions = (
            [float(pos)]
            if not isinstance(pos, (list, tuple, np.ndarray))
            else list(pos)
        )
        velocities = (
            [float(vel)]
            if not isinstance(vel, (list, tuple, np.ndarray))
            else list(vel)
        )

        return Message(
            timestamp_ns=int(payload.get("timestamp", 0.0) * 1e9),
            data=EndEffector(
                positions=positions,
                velocities=velocities,
                # Efforts are not provided in DROID, so we set them to zero
                efforts=[0.0] * len(positions),
            ),
        )
