import numpy as np
from mosaicolabs import Message

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology.end_effector import EndEffector


class DroidEndEffectorAdapter(BaseAdapter[EndEffector]):
    """
    Adapter for `end_effector` data in DROID datasets.

    Translates `end_effector` data from the dataset's message format to the
    `EndEffector` ontology type.
    """

    adapter_id = "droid.end_effector"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp",)
    _AT_LEAST_ONE: tuple[str, ...] = ("position", "velocity")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `end_effector` payload into a `EndEffector` message.

        Args:
            payload: Raw payload from the `end_effector` topic.

        Returns:
            A `Message` containing the `EndEffector` data.
        """
        cls._validate_payload(
            payload=payload,
        )
        position = payload.get("position")
        velocity = payload.get("velocity")

        tstamp_sec = payload["timestamp"]

        positions = (
            (
                [float(position)]
                if not isinstance(position, (list, tuple, np.ndarray))
                else list(position)
            )
            if position
            else []
        )
        velocities = (
            (
                [float(velocity)]
                if not isinstance(velocity, (list, tuple, np.ndarray))
                else list(velocity)
            )
            if velocity
            else []
        )

        return Message(
            timestamp_ns=int(tstamp_sec * 1e9),
            data=EndEffector(
                positions=positions,
                velocities=velocities,
                # Efforts are not provided in DROID, so we set them to zero
                efforts=[],
            ),
        )
