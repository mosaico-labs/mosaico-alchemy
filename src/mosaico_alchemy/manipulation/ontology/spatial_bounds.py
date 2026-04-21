"""
Spatial Bounds Data Structures.

This module defines ontology models for workspace limits and axis-aligned spatial
frames. The structures preserve simple spatial constraints that appear in
manipulation datasets without forcing them into a richer calibration or robot model.
"""

from mosaicolabs import MosaicoField, MosaicoType, Serializable, Vector3d


class Vector3dBounds(Serializable):
    """Describe lower and upper limits for a 3D vector quantity.

    This model exists for datasets that publish workspace or action limits directly
    as min/max vectors, which is often more faithful than wrapping them in a richer
    task-specific structure.

    Attributes:
        min: Lower bound vector.
        max: Upper bound vector.
    """

    __ontology_tag__ = "vector3d_bounds"

    min: Vector3d = MosaicoField(description="Minimum vector limits.")
    max: Vector3d = MosaicoField(description="Maximum vector limits.")


class Vector3dFrame(Serializable):
    """Describe a 3D frame using explicit axis vectors.

    Some datasets expose basis vectors directly instead of a full transform object.
    This model preserves that convention rather than inferring translation or pose
    semantics that are not present in the source.

    Attributes:
        x_axis: X-axis basis vector.
        y_axis: Y-axis basis vector.
        z_axis: Z-axis basis vector.
    """

    __ontology_tag__ = "vector3d_frame"

    x_axis: Vector3d = MosaicoField(description="X-axis vector component.")
    y_axis: Vector3d = MosaicoField(description="Y-axis vector component.")
    z_axis: Vector3d = MosaicoField(description="Z-axis vector component.")


class WorkspaceBounds(Serializable):
    """Store workspace bounds as a fixed 3x3 numeric layout.

    This representation exists because several manipulation datasets publish
    workspace limits as dense numeric matrices rather than named axis objects.
    Keeping the compact layout avoids inventing semantic labels during ingestion and
    makes the adapter's transformation from source arrays to ontology nearly
    lossless.

    Attributes:
        values: Dense 3x3 numeric layout describing workspace bounds.
    """

    __ontology_tag__ = "workspace_bounds"

    values: MosaicoType.list_(
        MosaicoType.list_(MosaicoType.float64, list_size=3),
        list_size=3,
    ) = MosaicoField(description="Values defining the workspace bounds.")
