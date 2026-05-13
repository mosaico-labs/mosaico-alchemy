from mosaicolabs import ForceTorque, Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleMeasuredForceTorqueAdapter(BaseAdapter[ForceTorque]):
    """
    Adapter for `measured_force_torque` topic from Reassemble datasets.

    Translated from `measured_force_torque` message (custom Protocol Buffers) to
    `mosaicolabs.ForceTorque`.
    """

    adapter_id = "reassemble.measured_force_torque"
    _REQUIRED_KEYS: tuple[str, ...] = (
        "timestamp",
        "measured_force",
        "measured_torque",
    )

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `measured_force_torque` payload into a `mosaicolabs.ForceTorque` message.

        Args:
            payload: Raw payload from the `measured_force_torque` topic.

        Returns:
            A `Message` containing the `mosaicolabs.ForceTorque` data.
        """
        cls._validate_payload(
            payload=payload,
            constraints={
                "measured_force": {"len": 3},
                "measured_torque": {"len": 3},
            },
        )

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=ForceTorque(
                force=Vector3d.from_list(payload["measured_force"]),
                torque=Vector3d.from_list(payload["measured_torque"]),
            ),
        )
