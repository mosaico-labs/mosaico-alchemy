"""
Fractal RT-1 dataset plugin.

This module maps Fractal RT-1 TFDS episodes to the generic ingestion descriptors
consumed by the manipulation runner. The plugin hides the dataset-specific TFDS
layout and exposes each episode as a regular sequence from the runner's perspective.
"""

from pathlib import Path

from mosaicolabs import (
    Boolean,
    CompressedImage,
    Floating32,
    Pose,
    Quaternion,
    String,
    Vector2d,
    Vector3d,
)

from mosaicopacks.manipulation.contracts import SequenceDescriptor, TopicDescriptor
from mosaicopacks.manipulation.datasets.fractal_rt1.iterators import (
    STEP_RATE_HZ,
    average_episode_size_bytes,
    count_steps,
    iter_step_image,
    iter_step_pose,
    iter_step_scalar,
    iter_step_terminate_episode,
    iter_step_value,
    iter_step_values,
    iter_step_vector,
    make_virtual_sequence_path,
)
from mosaicopacks.manipulation.ontology import (
    TerminateEpisode,
    TextEmbedding,
    Vector3dBounds,
    Vector3dFrame,
    WorkspaceBounds,
)


class FractalRT1Plugin:
    """
    Dataset plugin for Fractal RT-1 TensorFlow Datasets exports.

    Fractal RT-1 data is stored as TFDS shards rather than as one file per sequence.
    This plugin therefore synthesizes virtual sequence paths for each available
    episode and translates TFDS features into the descriptor model used by the runner.
    """

    dataset_id = "fractal_rt1"

    def supports(self, root: Path) -> bool:
        """
        Returns whether the root looks like a Fractal RT-1 TFDS export.

        The check deliberately uses cheap filesystem signals only: metadata files and
        at least one expected TFRecord shard for the train split.
        """
        if not root.is_dir():
            return False

        required = (
            root / "dataset_info.json",
            root / "features.json",
        )
        if not all(path.exists() for path in required):
            return False

        return any(root.glob("fractal20220817_data-train.tfrecord-*"))

    def discover_sequences(self, root: Path) -> list[Path]:
        """
        Returns one virtual sequence path for each available TFDS episode.

        Fractal RT-1 does not expose episodes as standalone files, so discovery
        synthesizes stable path-like identifiers that can still flow through the
        generic runner and reporting layers.
        """
        from mosaicopacks.manipulation.datasets.fractal_rt1.iterators import (
            available_episodes,
        )

        return [
            make_virtual_sequence_path(root, episode_index)
            for episode_index in available_episodes(root)
        ]

    def _find_missing_paths(
        self, sequence_path: Path, required_paths: tuple[str, ...]
    ) -> tuple[str, ...]:
        from mosaicopacks.manipulation.datasets.fractal_rt1.iterators import (
            _dataset_feature_paths,
            parse_virtual_sequence_path,
        )

        root, _episode_index = parse_virtual_sequence_path(sequence_path)
        available_paths = _dataset_feature_paths(str(root))
        return tuple(path for path in required_paths if path not in available_paths)

    def create_ingestion_plan(self, sequence_path: Path) -> SequenceDescriptor:
        """
        Builds the declarative ingestion plan for one Fractal RT-1 episode.

        The descriptor records both the synthetic identity of the episode and the
        topic mapping from TFDS feature paths to ontology messages. This keeps the
        runner generic even though the underlying data is loaded through TFDS rather
        than from one concrete source file per sequence.

        Args:
            sequence_path: Virtual path identifying the episode to ingest.

        Returns:
            The sequence descriptor consumed by the file-style ingestion runner.
        """
        from mosaicopacks.manipulation.datasets.fractal_rt1.iterators import (
            parse_virtual_sequence_path,
        )

        _root, episode_index = parse_virtual_sequence_path(sequence_path)
        split_name = sequence_path.name.split("@@", 1)[0]

        return SequenceDescriptor(
            sequence_name=f"{self.dataset_id}_{split_name}_ep{episode_index}",
            sequence_metadata={
                "dataset_id": self.dataset_id,
                "estimated_local_size_bytes": average_episode_size_bytes(
                    str(sequence_path.parent)
                ),
                "episode_index": episode_index,
                "ingestion_backend": "tfds",
                "source_path": str(sequence_path.parent),
                "source_sequence": sequence_path.name,
                "synthetic_step_timestamps": True,
                "step_rate_hz": STEP_RATE_HZ,
            },
            find_missing_paths=self._find_missing_paths,
            topics=[
                TopicDescriptor(
                    topic_name="step/is_first",
                    ontology_type=Boolean,
                    adapter_id="fractal_rt1.boolean",
                    payload_iter=iter_step_scalar("is_first"),
                    message_count=count_steps(),
                    required_paths=("steps.is_first",),
                ),
                TopicDescriptor(
                    topic_name="step/is_last",
                    ontology_type=Boolean,
                    adapter_id="fractal_rt1.boolean",
                    payload_iter=iter_step_scalar("is_last"),
                    message_count=count_steps(),
                    required_paths=("steps.is_last",),
                ),
                TopicDescriptor(
                    topic_name="step/is_terminal",
                    ontology_type=Boolean,
                    adapter_id="fractal_rt1.boolean",
                    payload_iter=iter_step_scalar("is_terminal"),
                    message_count=count_steps(),
                    required_paths=("steps.is_terminal",),
                ),
                TopicDescriptor(
                    topic_name="step/reward",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar("reward"),
                    message_count=count_steps(),
                    required_paths=("steps.reward",),
                ),
                TopicDescriptor(
                    topic_name="step/action/base_displacement_vector",
                    ontology_type=Vector2d,
                    adapter_id="fractal_rt1.vector2d",
                    payload_iter=iter_step_vector("action.base_displacement_vector"),
                    message_count=count_steps(),
                    required_paths=("steps.action.base_displacement_vector",),
                ),
                TopicDescriptor(
                    topic_name="step/action/base_displacement_vertical_rotation",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar(
                        "action.base_displacement_vertical_rotation"
                    ),
                    message_count=count_steps(),
                    required_paths=(
                        "steps.action.base_displacement_vertical_rotation",
                    ),
                ),
                TopicDescriptor(
                    topic_name="step/action/gripper_closedness_action",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar("action.gripper_closedness_action"),
                    message_count=count_steps(),
                    required_paths=("steps.action.gripper_closedness_action",),
                ),
                TopicDescriptor(
                    topic_name="step/action/rotation_delta",
                    ontology_type=Vector3d,
                    adapter_id="fractal_rt1.vector3d",
                    payload_iter=iter_step_vector("action.rotation_delta"),
                    message_count=count_steps(),
                    required_paths=("steps.action.rotation_delta",),
                ),
                TopicDescriptor(
                    topic_name="step/action/terminate_episode",
                    ontology_type=TerminateEpisode,
                    adapter_id="fractal_rt1.terminate_episode",
                    payload_iter=iter_step_terminate_episode(
                        "action.terminate_episode"
                    ),
                    message_count=count_steps(),
                    required_paths=("steps.action.terminate_episode",),
                ),
                TopicDescriptor(
                    topic_name="step/action/world_vector",
                    ontology_type=Vector3d,
                    adapter_id="fractal_rt1.vector3d",
                    payload_iter=iter_step_vector("action.world_vector"),
                    message_count=count_steps(),
                    required_paths=("steps.action.world_vector",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/base_pose_tool_reached",
                    ontology_type=Pose,
                    adapter_id="fractal_rt1.pose",
                    payload_iter=iter_step_pose("observation.base_pose_tool_reached"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.base_pose_tool_reached",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/gripper_closed",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar("observation.gripper_closed"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.gripper_closed",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/gripper_closedness_commanded",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar(
                        "observation.gripper_closedness_commanded"
                    ),
                    message_count=count_steps(),
                    required_paths=("steps.observation.gripper_closedness_commanded",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/height_to_bottom",
                    ontology_type=Floating32,
                    adapter_id="fractal_rt1.floating32",
                    payload_iter=iter_step_scalar("observation.height_to_bottom"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.height_to_bottom",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/image",
                    ontology_type=CompressedImage,
                    adapter_id="fractal_rt1.video_frame",
                    payload_iter=iter_step_image("observation.image"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.image",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/natural_language_embedding",
                    ontology_type=TextEmbedding,
                    adapter_id="fractal_rt1.text_embedding",
                    payload_iter=iter_step_value(
                        "observation.natural_language_embedding",
                        payload_key="values",
                    ),
                    message_count=count_steps(),
                    required_paths=("steps.observation.natural_language_embedding",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/natural_language_instruction",
                    ontology_type=String,
                    adapter_id="fractal_rt1.string",
                    payload_iter=iter_step_value(
                        "observation.natural_language_instruction",
                        payload_key="value",
                    ),
                    message_count=count_steps(),
                    required_paths=("steps.observation.natural_language_instruction",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/orientation_box",
                    ontology_type=Vector3dBounds,
                    adapter_id="fractal_rt1.orientation_box",
                    payload_iter=iter_step_values("observation.orientation_box"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.orientation_box",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/orientation_start",
                    ontology_type=Quaternion,
                    adapter_id="fractal_rt1.quaternion",
                    payload_iter=iter_step_vector("observation.orientation_start"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.orientation_start",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/robot_orientation_positions_box",
                    ontology_type=Vector3dFrame,
                    adapter_id="fractal_rt1.robot_orientation_positions_box",
                    payload_iter=iter_step_values(
                        "observation.robot_orientation_positions_box"
                    ),
                    message_count=count_steps(),
                    required_paths=(
                        "steps.observation.robot_orientation_positions_box",
                    ),
                ),
                TopicDescriptor(
                    topic_name="step/observation/rotation_delta_to_go",
                    ontology_type=Vector3d,
                    adapter_id="fractal_rt1.vector3d",
                    payload_iter=iter_step_vector("observation.rotation_delta_to_go"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.rotation_delta_to_go",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/src_rotation",
                    ontology_type=Quaternion,
                    adapter_id="fractal_rt1.quaternion",
                    payload_iter=iter_step_vector("observation.src_rotation"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.src_rotation",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/vector_to_go",
                    ontology_type=Vector3d,
                    adapter_id="fractal_rt1.vector3d",
                    payload_iter=iter_step_vector("observation.vector_to_go"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.vector_to_go",),
                ),
                TopicDescriptor(
                    topic_name="step/observation/workspace_bounds",
                    ontology_type=WorkspaceBounds,
                    adapter_id="fractal_rt1.workspace_bounds",
                    payload_iter=iter_step_values("observation.workspace_bounds"),
                    message_count=count_steps(),
                    required_paths=("steps.observation.workspace_bounds",),
                ),
            ],
        )
