"""
MML rosbag dataset plugin.

This module maps MML bag recordings to the rosbag-specific ingestion descriptor
consumed by the manipulation runner. Unlike file-backed plugins, MML delegates the
topic-by-topic translation work to the ROS bridge and rosbag executor.
"""

from pathlib import Path

from rosbags.highlevel import AnyReader

from mosaico_alchemy.manipulation.adapters.mml import (
    AudioDataAdapter,
    AudioInfoAdapter,
    JointTorqueCommandAdapter,
    TekscanSensorAdapter,
)
from mosaico_alchemy.manipulation.contracts import (
    RosbagSequenceDescriptor,
    normalize_topic_name,
)


class MMLPlugin:
    """
    Dataset plugin for MML rosbag recordings.

    MML sequences are ingested through the rosbag execution path rather than through
    per-topic payload iterators. The plugin therefore focuses on recognizing the bag,
    selecting the topics that define a valid MML recording, and providing adapter
    overrides for the ROS messages that need custom ontology mappings.
    """

    dataset_id = "mml"

    SIGNATURE_TOPICS = (
        "/allegro_hand_right/joint_states",
        "/iiwa/TorqueController/command",
        "/tekscan/frame",
    )

    DEFAULT_TOPICS = (
        "/allegro_hand_right/joint_states",
        "/audio/audio",
        "/audio/audio_info",
        "/iiwa/TorqueController/command",
        "/iiwa/eePose",
        "/iiwa/joint_states",
        "/tekscan/frame",
        "/trialInfo",
    )

    def supports(self, root: Path) -> bool:
        """
        Returns whether the root contains at least one bag that matches the MML signature.

        The plugin probes discovered bag files and requires a small set of signature
        topics before claiming support. This keeps the registry from treating generic
        rosbag folders as MML datasets by accident.
        """
        bag_paths = self.discover_sequences(root)
        if not bag_paths:
            return False

        for bag_path in bag_paths:
            try:
                with AnyReader([bag_path]) as reader:
                    available_topics = {
                        normalize_topic_name(connection.topic)
                        for connection in reader.connections
                    }
            except Exception:
                continue

            if set(self.SIGNATURE_TOPICS).issubset(available_topics):
                return True

        return False

    def discover_sequences(self, root: Path) -> list[Path]:
        """Returns the candidate `.bag` files that should be considered as MML sequences."""
        return sorted(
            sequence_path
            for sequence_path in root.glob("*.bag")
            if not sequence_path.name.startswith("._")
        )

    def create_ingestion_plan(self, sequence_path: Path) -> RosbagSequenceDescriptor:
        """
        Builds the rosbag ingestion descriptor for one MML recording.

        The descriptor captures the sequence identity, the default topics to replay,
        and the adapter overrides required for topics whose ROS messages do not map
        directly to the default bridge adapters.

        Args:
            sequence_path: Bag file selected during discovery.

        Returns:
            The rosbag descriptor consumed by the rosbag executor.
        """
        return RosbagSequenceDescriptor(
            bag_path=sequence_path,
            sequence_name=f"{self.dataset_id}_{sequence_path.stem}",
            sequence_metadata={
                "dataset_id": self.dataset_id,
                "ingestion_backend": "rosbag",
                "source_file": sequence_path.name,
                "source_path": str(sequence_path),
            },
            default_topics=self.DEFAULT_TOPICS,
            adapter_overrides={
                "/audio/audio": AudioDataAdapter,
                "/audio/audio_info": AudioInfoAdapter,
                "/iiwa/TorqueController/command": JointTorqueCommandAdapter,
                "/tekscan/frame": TekscanSensorAdapter,
            },
        )
