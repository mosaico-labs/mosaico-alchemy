"""
Topic-level ingestion helpers for file-backed sequences.

This module owns the last mile of file-based ingestion: creating topic writers,
binding adapters, and pushing translated payloads either sequentially or in parallel.
It isolates topic execution policy from the higher-level dataset runner.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Event

from mosaicolabs import TopicLevelErrorPolicy

from mosaico_alchemy.manipulation.adapters import build_default_adapter_registry
from mosaico_alchemy.manipulation.contracts import (
    SequenceDescriptor,
    TopicDescriptor,
    WriteMode,
)
from mosaico_alchemy.manipulation.runner.reporters.sequence_progress import (
    SequenceProgress,
)

LOGGER = logging.getLogger(__name__)


class TopicIngester:
    """
    Writes the topics declared in a `SequenceDescriptor`.

    The ingester is deliberately narrower than the dataset runner: it assumes a file-
    backed plan already exists and focuses only on adapter resolution, topic writer
    preparation, and per-topic payload streaming.
    """

    def __init__(self, write_mode: WriteMode = "sync") -> None:
        """Initializes the ingester with the built-in adapter registry and write mode."""
        self.adapter_registry = build_default_adapter_registry()
        self._write_mode = write_mode

    def prepare_topic_writers(
        self,
        swriter,
        plan: SequenceDescriptor,
        ui: SequenceProgress,
    ) -> list:
        """
        Resolves adapters and ensures each topic in the plan has a writer.

        Args:
            swriter: Open sequence writer returned by the SDK.
            plan: File-backed sequence descriptor to ingest.
            ui: Progress reporter used to reflect topic state.

        Returns:
            Tuples of topic descriptor, topic writer, and resolved adapter class.

        Raises:
            RuntimeError: If a topic cannot be created in the target sequence.
            KeyError: If a topic references an unknown adapter id.
        """
        topic_writers = []
        for topic in plan.topics:
            writer = swriter.get_topic_writer(topic_name=topic.topic_name)

            if writer is None:
                LOGGER.debug(
                    "Creating topic '%s' with ontology '%s'",
                    topic.topic_name,
                    topic.ontology_type.__name__,
                )
                writer = swriter.topic_create(
                    topic_name=topic.topic_name,
                    metadata=topic.metadata,
                    ontology_type=topic.ontology_type,
                    on_error=TopicLevelErrorPolicy.Raise,
                )
                if writer is None:
                    ui.update_status(topic.topic_name, "Write Error", "red")
                    raise RuntimeError(
                        f"Unable to create topic '{topic.topic_name}' "
                        f"in sequence '{plan.sequence_name}'"
                    )

            try:
                adapter_cls = self.adapter_registry.get(topic.adapter_id)
            except KeyError:
                ui.update_status(topic.topic_name, "No Adapter", "yellow")
                raise

            topic_writers.append((topic, writer, adapter_cls))

        return topic_writers

    def run_ingestion(
        self,
        sequence_path: Path,
        topic_writers: list,
        ui: SequenceProgress,
        missing_topic_sources: dict[str, tuple[str, ...]] | None = None,
    ) -> int:
        """
        Runs topic ingestion using the configured write mode.

        Args:
            sequence_path: Source sequence path used by the topic payload iterators.
            topic_writers: Prepared topic writer tuples returned by `prepare_topic_writers`.
            ui: Progress reporter used for live status updates.
            missing_topic_sources: Optional precomputed missing source paths per topic.

        Returns:
            The total number of messages pushed across all topics.
        """
        if self._write_mode == "sync":
            return self.run_sequential_ingestion(
                sequence_path,
                topic_writers,
                ui,
                missing_topic_sources=missing_topic_sources,
            )

        return self.run_parallel_ingestion(
            sequence_path,
            topic_writers,
            ui,
            missing_topic_sources=missing_topic_sources,
        )

    def run_parallel_ingestion(
        self,
        sequence_path: Path,
        topic_writers: list,
        ui: SequenceProgress,
        missing_topic_sources: dict[str, tuple[str, ...]] | None = None,
    ) -> int:
        """
        Ingests topics concurrently using one worker per topic.

        This mode trades simpler execution for throughput when topic iterators and
        writers can make progress independently over a shared SDK client.
        """
        missing_topic_sources = missing_topic_sources or {}
        stop_event = Event()
        total_messages = 0

        with ThreadPoolExecutor(
            max_workers=max(1, len(topic_writers)),
            thread_name_prefix="manipulation-topic",
        ) as executor:
            futures = {
                executor.submit(
                    self._ingest_topic,
                    sequence_path,
                    topic,
                    writer,
                    adapter_cls,
                    ui,
                    stop_event,
                    missing_paths=missing_topic_sources.get(topic.topic_name, ()),
                ): topic
                for topic, writer, adapter_cls in topic_writers
            }

            for future in as_completed(futures):
                topic = futures[future]
                try:
                    total_messages += future.result()
                except Exception as exc:
                    LOGGER.error(
                        "Topic '%s' failed during ingestion: %s",
                        topic.topic_name,
                        exc,
                        exc_info=True,
                    )
                    ui.update_status(topic.topic_name, "Write Error", "red")

        ui.complete_all()
        return total_messages

    def run_sequential_ingestion(
        self,
        sequence_path: Path,
        topic_writers: list,
        ui: SequenceProgress,
        missing_topic_sources: dict[str, tuple[str, ...]] | None = None,
    ) -> int:
        """Ingests topics one after another in the current thread."""
        missing_topic_sources = missing_topic_sources or {}
        stop_event = Event()
        total_messages = 0

        for topic, writer, adapter_cls in topic_writers:
            try:
                total_messages += self._ingest_topic(
                    sequence_path,
                    topic,
                    writer,
                    adapter_cls,
                    ui,
                    stop_event,
                    missing_paths=missing_topic_sources.get(topic.topic_name, ()),
                )
            except Exception as exc:
                LOGGER.error(
                    "Topic '%s' failed during ingestion: %s",
                    topic.topic_name,
                    exc,
                    exc_info=True,
                )
                ui.update_status(topic.topic_name, "Write Error", "red")

        ui.complete_all()
        return total_messages

    def _ingest_topic(
        self,
        sequence_path: Path,
        topic: TopicDescriptor,
        writer,
        adapter_cls,
        ui: SequenceProgress,
        stop_event: Event,
        missing_paths: tuple[str, ...] = (),
    ) -> int:
        """
        Pushes all payloads for one topic through the resolved adapter and writer.

        Missing source paths are treated as an empty topic rather than as a hard
        failure, which lets sequence creation proceed even when some sources are absent.
        """
        if missing_paths:
            ui.update_status(topic.topic_name, "Missing Source", "yellow")
            ui.complete_topic(topic.topic_name)
            return 0

        message_count = 0
        for payload in topic.payload_iter(sequence_path):
            if stop_event.is_set():
                ui.update_status(topic.topic_name, "Cancelled", "yellow")
                return message_count

            writer.push(adapter_cls.translate(payload))
            message_count += 1
            ui.advance(topic.topic_name)

        ui.complete_topic(topic.topic_name)

        if message_count == 0:
            ui.update_status(topic.topic_name, "Empty", "yellow")
        elif not ui.enabled:
            LOGGER.info(
                "Completed topic '%s' with %d message(s)",
                topic.topic_name,
                message_count,
            )

        return message_count
