from mosaicolabs import Message, Vector3d

from mosaico_alchemy.manipulation.adapters.base import BaseAdapter
from mosaico_alchemy.manipulation.ontology import (
    Vector3dBounds,
    Vector3dFrame,
    WorkspaceBounds,
)


class FractalRT1OrientationBoxAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.orientation_box"
    ontology_type = Vector3dBounds

    @classmethod
    def translate(cls, payload: dict) -> Message:
        values = [float(v) for v in payload.get("values", [])]

        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=cls.ontology_type(
                min=Vector3d(x=values[0], y=values[1], z=values[2]),
                max=Vector3d(x=values[3], y=values[4], z=values[5]),
            ),
        )


class FractalRT1RobotOrientationPositionsBoxAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.robot_orientation_positions_box"
    ontology_type = Vector3dFrame

    @classmethod
    def translate(cls, payload: dict) -> Message:
        values = [float(v) for v in payload.get("values", [])]

        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=cls.ontology_type(
                x_axis=Vector3d(x=values[0], y=values[1], z=values[2]),
                y_axis=Vector3d(x=values[3], y=values[4], z=values[5]),
                z_axis=Vector3d(x=values[6], y=values[7], z=values[8]),
            ),
        )


class FractalRT1WorkspaceBoundsAdapter(BaseAdapter):
    adapter_id = "fractal_rt1.workspace_bounds"
    ontology_type = WorkspaceBounds

    @classmethod
    def translate(cls, payload: dict) -> Message:
        values = [float(v) for v in payload.get("values", [])]
        matrix = [values[i : i + 3] for i in range(0, len(values), 3)]
        return Message(
            timestamp_ns=int(payload.get("timestamp_ns", 0.0)),
            data=cls.ontology_type(values=matrix),
        )
