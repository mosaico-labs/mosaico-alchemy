from mosaicolabs import Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology import (
    Vector3dBounds,
    Vector3dFrame,
    WorkspaceBounds,
)


class FractalRT1OrientationBoxAdapter(BaseAdapter[Vector3dBounds]):
    """
    Adapter for orientation box data in FractalRT1 datasets.

    Translates orientation box data from the dataset's message format to the
    `Vector3dBounds` ontology type.
    """

    adapter_id = "fractal_rt1.orientation_box"
    ontology_type = Vector3dBounds
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "values")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `orientation_box` payload into a `Vector3dBounds` message.

        Args:
            payload: Raw payload from the `orientation_box` topic.

        Returns:
            A `Message` containing the `Vector3dBounds` data.
        """
        cls._validate_payload(payload=payload, constraints={"values": {"len": 6}})
        values = [float(v) for v in payload["values"]]
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Vector3dBounds(
                min=Vector3d(x=values[0], y=values[1], z=values[2]),
                max=Vector3d(x=values[3], y=values[4], z=values[5]),
            ),
        )


class FractalRT1RobotOrientationPositionsBoxAdapter(BaseAdapter[Vector3dFrame]):
    """
    Adapter for orientation position box data in FractalRT1 datasets.

    Translates orientation position box data from the dataset's message format to the
    `Vector3dFrame` ontology type.
    """

    adapter_id = "fractal_rt1.robot_orientation_positions_box"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "values")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `robot_orientation_positions_box` payload
        into a `Vector3dFrame` message.

        Args:
            payload: Raw payload from the `robot_orientation_positions_box` topic.

        Returns:
            A `Message` containing the `Vector3dFrame` data.
        """
        cls._validate_payload(payload=payload, constraints={"values": {"len": 9}})
        values = [float(v) for v in payload["values"]]
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=Vector3dFrame(
                x_axis=Vector3d(x=values[0], y=values[1], z=values[2]),
                y_axis=Vector3d(x=values[3], y=values[4], z=values[5]),
                z_axis=Vector3d(x=values[6], y=values[7], z=values[8]),
            ),
        )


class FractalRT1WorkspaceBoundsAdapter(BaseAdapter[WorkspaceBounds]):
    """
    Adapter for workspace bounds data in FractalRT1 datasets.

    Translates workspace bounds data from the dataset's message format to the
    `WorkspaceBounds` ontology type.
    """

    adapter_id = "fractal_rt1.workspace_bounds"
    _REQUIRED_KEYS: tuple[str, ...] = ("timestamp_ns", "values")

    @classmethod
    def translate(cls, payload: dict) -> Message:
        """
        Translates a raw `workspace_bounds` payload
        into a `WorkspaceBounds` message.

        Args:
            payload: Raw payload from the `workspace_bounds` topic.

        Returns:
            A `Message` containing the `WorkspaceBounds` data.
        """
        cls._validate_payload(payload=payload, constraints={"values": {"len": 9}})
        values = [float(v) for v in payload["values"]]
        matrix = [values[i : i + 3] for i in range(0, len(values), 3)]
        return Message(
            timestamp_ns=int(payload["timestamp_ns"]),
            data=WorkspaceBounds(values=matrix),
        )
