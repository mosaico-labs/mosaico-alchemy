"""
File-backed sequence execution.

This module uploads sequences described by `SequenceDescriptor` plans. It keeps the
execution path for file-based datasets separate from the rosbag bridge so the runner
can choose the backend without mixing ingestion strategies.
"""

import logging
from pathlib import Path

from mosaicolabs import SessionLevelErrorPolicy

from mosaicopacks.manipulation.contracts import SequenceDescriptor, WriteMode
from mosaicopacks.manipulation.runner.reporters.sequence_progress import (
    SequenceProgress,
)
from mosaicopacks.manipulation.runner.topic_ingester import TopicIngester

LOGGER = logging.getLogger(__name__)


class FileSequenceExecutor:
    """Execute ingestion plans that read topic data directly from local files.

    The executor owns the high-level flow for a single file-backed sequence: skip
    detection, progress initialization, writer creation, and delegation to
    `TopicIngester` for the actual topic iteration.
    """

    def __init__(self, console, write_mode: WriteMode = "sync") -> None:
        """Initialize the executor with the console and topic write mode."""
        self.console = console
        self._write_mode = write_mode
        self._ingester = TopicIngester(write_mode=write_mode)

    def ingest_sequence(
        self,
        sequence_path: Path,
        plan: SequenceDescriptor,
        client,
        existing_sequences: set[str] | None = None,
    ) -> bool:
        """Upload one file-backed sequence described by `plan`.

        Args:
            sequence_path: Local path for the sequence being ingested.
            plan: Declarative ingestion plan built by the dataset plugin.
            client: Mosaico client used to create the destination sequence.
            existing_sequences: Optional cache of remote sequence names used to skip
                already-uploaded sequences without an extra backend round trip.

        Returns:
            `True` when the sequence was created and uploaded, `False` when it was
            skipped before ingestion started.
        """
        if existing_sequences is not None and plan.sequence_name in existing_sequences:
            LOGGER.warning(
                "Sequence '%s' already exists, skipping.", plan.sequence_name
            )
            return False

        LOGGER.info(
            "Creating file sequence '%s' from %s with %d topic(s) using %s topic ingestion",
            plan.sequence_name,
            sequence_path.name,
            len(plan.topics),
            (
                "sync (default)"
                if self._write_mode == "sync"
                else "async (shared-client topic threads)"
            ),
        )

        missing_topic_sources = self._find_missing_topic_sources(sequence_path, plan)
        topic_totals = {
            topic.topic_name: (
                0
                if topic.topic_name in missing_topic_sources
                else topic.message_count(sequence_path)
            )
            for topic in plan.topics
        }
        ui = SequenceProgress(self.console)
        ui.setup(topic_totals)

        with client.sequence_create(
            sequence_name=plan.sequence_name,
            metadata=plan.sequence_metadata,
            on_error=SessionLevelErrorPolicy.Delete,
        ) as swriter:
            with ui.live():
                topic_writers = self._ingester.prepare_topic_writers(swriter, plan, ui)
                total_messages = self._ingester.run_ingestion(
                    sequence_path,
                    topic_writers,
                    ui,
                    missing_topic_sources=missing_topic_sources,
                )

        LOGGER.info(
            "Completed file sequence '%s' — %d topic(s), %d message(s)",
            plan.sequence_name,
            len(plan.topics),
            total_messages,
        )

        if existing_sequences is not None:
            existing_sequences.add(plan.sequence_name)

        return True

    def _find_missing_topic_sources(
        self,
        sequence_path: Path,
        plan: SequenceDescriptor,
    ) -> dict[str, tuple[str, ...]]:
        """Collect missing required paths for topics that support sparse datasets.

        Topics with missing source files are still created, but they are marked as
        empty so the resulting sequence shape stays predictable for downstream users.
        """
        missing_topic_sources: dict[str, tuple[str, ...]] = {}

        if not plan.find_missing_paths:
            return missing_topic_sources

        for topic in plan.topics:
            if not topic.required_paths:
                continue

            missing_paths = plan.find_missing_paths(sequence_path, topic.required_paths)
            if not missing_paths:
                continue

            missing_topic_sources[topic.topic_name] = tuple(missing_paths)
            missing_list = ", ".join(missing_paths)
            LOGGER.warning(
                "Topic '%s' is missing source path(s) [%s] in '%s'; creating it empty.",
                topic.topic_name,
                missing_list,
                sequence_path.name,
            )

        return missing_topic_sources
