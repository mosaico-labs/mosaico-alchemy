"""
Reassemble dataset plugin.

This module maps Reassemble HDF5 recordings to the generic ingestion descriptors
consumed by the manipulation runner. The plugin keeps dataset-specific path and
sensor knowledge in one place so the rest of the pipeline stays backend-agnostic.
"""

from pathlib import Path

from mosaicolabs import CompressedImage, ForceTorque, Pose, RobotJoint, Velocity

from mosaicopacks.manipulation.contracts import SequenceDescriptor, TopicDescriptor
from mosaicopacks.manipulation.datasets.reassemble.iterators import (
    count_audio,
    count_event_frames,
    count_records,
    count_video_frames,
    iter_audio,
    iter_event_frames,
    iter_records,
    iter_video_frames,
)
from mosaicopacks.manipulation.ontology.audio import AudioDataStamped
from mosaicopacks.manipulation.ontology.end_effector import EndEffector
from mosaicopacks.manipulation.ontology.event_camera import EventCamera


class ReassemblePlugin:
    """
    Dataset plugin for Reassemble HDF5 recordings.

    Reassemble sequences are represented as standalone `.h5` files with a known set
    of datasets for camera, event, audio, and robot-state streams. This plugin
    translates that fixed layout into the descriptor model used by the generic runner.
    """

    dataset_id = "reassemble"

    def supports(self, root: Path) -> bool:
        """
        Returns whether the root looks like a Reassemble dataset directory.

        Reassemble data is currently recognized purely by the presence of HDF5
        sequence files at the root level.
        """
        return any(root.glob("*.h5"))

    def discover_sequences(self, root: Path) -> list[Path]:
        """Returns the Reassemble sequence files that should be ingested."""
        return sorted(root.glob("*.h5"))

    def _find_missing_paths(
        self, sequence_path: Path, required_paths: tuple[str, ...]
    ) -> tuple[str, ...]:
        from mosaicopacks.manipulation.readers import HDF5Reader

        with HDF5Reader(sequence_path) as reader:
            return reader.missing_paths(required_paths)

    def create_ingestion_plan(self, sequence_path: Path) -> SequenceDescriptor:
        """
        Builds the declarative ingestion plan for one Reassemble sequence file.

        The returned descriptor captures both the shared sequence metadata and the
        topic-by-topic mapping from HDF5 paths to ontology messages. Keeping this
        plan fully declarative lets the generic file executor validate inputs and
        ingest the sequence without dataset-specific branching.

        Args:
            sequence_path: Reassemble `.h5` file discovered under the dataset root.

        Returns:
            The sequence descriptor consumed by the file-backed ingestion runner.
        """
        return SequenceDescriptor(
            sequence_name=f"{self.dataset_id}_{sequence_path.stem}",
            sequence_metadata={
                "dataset_id": self.dataset_id,
                "ingestion_backend": "file",
                "source_file": sequence_path.name,
            },
            find_missing_paths=self._find_missing_paths,
            topics=[
                TopicDescriptor(
                    topic_name="capture_node-camera-image",
                    ontology_type=CompressedImage,
                    adapter_id=f"{self.dataset_id}.video_frame",
                    payload_iter=iter_video_frames(
                        video_path="capture_node-camera-image",
                        timestamps_path="timestamps/capture_node-camera-image",
                    ),
                    message_count=count_video_frames(
                        "timestamps/capture_node-camera-image"
                    ),
                    metadata={
                        "sensor_model": "iniVation DAVIS346",
                        "sensor_type": "event_camera",
                        "resolution": "[346, 260]",
                        "frame_sensor": "APS grayscale",
                        "datasheet": "https://inivation.com/wp-content/uploads/2019/08/DAVIS346.pdf",
                    },
                    required_paths=(
                        "capture_node-camera-image",
                        "timestamps/capture_node-camera-image",
                    ),
                ),
                TopicDescriptor(
                    topic_name="events",
                    ontology_type=EventCamera,
                    adapter_id=f"{self.dataset_id}.events",
                    payload_iter=iter_event_frames(
                        events_path="events",
                        timestamps_path="timestamps/events",
                    ),
                    message_count=count_event_frames("timestamps/events"),
                    metadata={
                        "sensor_model": "iniVation DAVIS346",
                        "sensor_type": "event_camera",
                        "resolution": "[346, 260]",
                        "representation": "33ms event window with raw events",
                        "window_ms": 33,
                    },
                    required_paths=("events", "timestamps/events"),
                ),
                TopicDescriptor(
                    topic_name="hama1",
                    ontology_type=CompressedImage,
                    adapter_id=f"{self.dataset_id}.video_frame",
                    payload_iter=iter_video_frames(
                        video_path="hama1",
                        timestamps_path="timestamps/hama1",
                    ),
                    message_count=count_video_frames("timestamps/hama1"),
                    required_paths=("hama1", "timestamps/hama1"),
                ),
                TopicDescriptor(
                    topic_name="hama1_audio",
                    ontology_type=AudioDataStamped,
                    adapter_id=f"{self.dataset_id}.audio",
                    payload_iter=iter_audio(
                        audio_path="hama1_audio",
                        timestamps_path="timestamps/hama1",
                    ),
                    message_count=count_audio(
                        audio_path="hama1_audio",
                        timestamps_path="timestamps/hama1",
                    ),
                    required_paths=("hama1_audio", "timestamps/hama1"),
                ),
                TopicDescriptor(
                    topic_name="hama2",
                    ontology_type=CompressedImage,
                    adapter_id=f"{self.dataset_id}.video_frame",
                    payload_iter=iter_video_frames(
                        video_path="hama2",
                        timestamps_path="timestamps/hama2",
                    ),
                    message_count=count_video_frames("timestamps/hama2"),
                    required_paths=("hama2", "timestamps/hama2"),
                ),
                TopicDescriptor(
                    topic_name="hama2_audio",
                    ontology_type=AudioDataStamped,
                    adapter_id=f"{self.dataset_id}.audio",
                    payload_iter=iter_audio(
                        audio_path="hama2_audio",
                        timestamps_path="timestamps/hama2",
                    ),
                    message_count=count_audio(
                        audio_path="hama2_audio",
                        timestamps_path="timestamps/hama2",
                    ),
                    required_paths=("hama2_audio", "timestamps/hama2"),
                ),
                TopicDescriptor(
                    topic_name="hand",
                    ontology_type=CompressedImage,
                    adapter_id=f"{self.dataset_id}.video_frame",
                    payload_iter=iter_video_frames(
                        video_path="hand",
                        timestamps_path="timestamps/hand",
                    ),
                    message_count=count_video_frames("timestamps/hand"),
                    required_paths=("hand", "timestamps/hand"),
                ),
                TopicDescriptor(
                    topic_name="hand_audio",
                    ontology_type=AudioDataStamped,
                    adapter_id=f"{self.dataset_id}.audio",
                    payload_iter=iter_audio(
                        audio_path="hand_audio",
                        timestamps_path="timestamps/hand",
                    ),
                    message_count=count_audio(
                        audio_path="hand_audio",
                        timestamps_path="timestamps/hand",
                    ),
                    required_paths=("hand_audio", "timestamps/hand"),
                ),
                TopicDescriptor(
                    topic_name="robot_state/joint_state",
                    ontology_type=RobotJoint,
                    adapter_id=f"{self.dataset_id}.joint_state",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/joint_positions",
                        fields={
                            "position": "robot_state/joint_positions",
                            "velocity": "robot_state/joint_velocities",
                            "effort": "robot_state/joint_efforts",
                        },
                    ),
                    message_count=count_records("timestamps/joint_positions"),
                    metadata={"n_joints": 7},
                    required_paths=(
                        "timestamps/joint_positions",
                        "robot_state/joint_positions",
                        "robot_state/joint_velocities",
                        "robot_state/joint_efforts",
                    ),
                ),
                TopicDescriptor(
                    topic_name="robot_state/pose",
                    ontology_type=Pose,
                    adapter_id=f"{self.dataset_id}.pose",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/pose",
                        fields={"pose": "robot_state/pose"},
                    ),
                    message_count=count_records("timestamps/pose"),
                    required_paths=("timestamps/pose", "robot_state/pose"),
                ),
                TopicDescriptor(
                    topic_name="robot_state/velocity",
                    ontology_type=Velocity,
                    adapter_id=f"{self.dataset_id}.velocity",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/velocity",
                        fields={"velocity": "robot_state/velocity"},
                    ),
                    message_count=count_records("timestamps/velocity"),
                    required_paths=("timestamps/velocity", "robot_state/velocity"),
                ),
                TopicDescriptor(
                    topic_name="robot_state/compensated_base_force_torque",
                    ontology_type=ForceTorque,
                    adapter_id=f"{self.dataset_id}.compensated_base_force_torque",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/compensated_base_force",
                        fields={
                            "compensated_base_force": "robot_state/compensated_base_force",
                            "compensated_base_torque": "robot_state/compensated_base_torque",
                        },
                    ),
                    message_count=count_records("timestamps/compensated_base_force"),
                    required_paths=(
                        "timestamps/compensated_base_force",
                        "robot_state/compensated_base_force",
                        "robot_state/compensated_base_torque",
                    ),
                ),
                TopicDescriptor(
                    topic_name="robot_state/measured_force_torque",
                    ontology_type=ForceTorque,
                    adapter_id=f"{self.dataset_id}.measured_force_torque",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/measured_force",
                        fields={
                            "measured_force": "robot_state/measured_force",
                            "measured_torque": "robot_state/measured_torque",
                        },
                    ),
                    message_count=count_records("timestamps/measured_force"),
                    required_paths=(
                        "timestamps/measured_force",
                        "robot_state/measured_force",
                        "robot_state/measured_torque",
                    ),
                ),
                TopicDescriptor(
                    topic_name="robot_state/end_effector",
                    ontology_type=EndEffector,
                    adapter_id=f"{self.dataset_id}.end_effector",
                    payload_iter=iter_records(
                        timestamps_path="timestamps/gripper_efforts",
                        fields={
                            "gripper_efforts": "robot_state/gripper_efforts",
                            "gripper_positions": "robot_state/gripper_positions",
                            "gripper_velocities": "robot_state/gripper_velocities",
                        },
                    ),
                    message_count=count_records("timestamps/gripper_efforts"),
                    required_paths=(
                        "timestamps/gripper_efforts",
                        "robot_state/gripper_efforts",
                        "robot_state/gripper_positions",
                        "robot_state/gripper_velocities",
                    ),
                ),
            ],
        )
