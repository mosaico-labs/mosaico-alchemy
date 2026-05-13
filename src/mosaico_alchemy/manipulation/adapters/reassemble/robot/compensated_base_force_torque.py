from mosaicolabs import ForceTorque, Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter


class ReassembleCompensatedBaseForceTorqueAdapter(BaseAdapter[ForceTorque]):
    """
    Adapter for `compensated_base_force_torque` topic from Reassemble datasets.

    Translated from `compensated_base_force_torque` message (custom Protocol Buffers) to
    `mosaicolabs.ForceTorque`.
    """

    adapter_id = "reassemble.compensated_base_force_torque"
    _REQUIRED_KEYS: tuple[str, ...] = (
        "timestamp",
        "compensated_base_force",
        "compensated_base_torque",
    )

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `compensated_base_force_torque` payload into a `mosaicolabs.ForceTorque` message.

        Args:
            payload: Raw payload from the `compensated_base_force_torque` topic.

        Returns:
            A `Message` containing the `mosaicolabs.ForceTorque` data.
        """
        cls._validate_payload(
            payload=payload,
            constraints={
                "compensated_base_force": {"len": 3},
                "compensated_base_torque": {"len": 3},
            },
        )

        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9),
            data=ForceTorque(
                force=Vector3d.from_list(payload["compensated_base_force"]),
                torque=Vector3d.from_list(payload["compensated_base_torque"]),
            ),
        )
