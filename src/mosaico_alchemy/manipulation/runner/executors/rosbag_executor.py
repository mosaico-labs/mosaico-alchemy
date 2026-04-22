"""
Rosbag-backed sequence execution.

This module adapts `RosbagSequenceDescriptor` plans into `mosaicolabs.ros_bridge`
configuration objects. It keeps topic resolution and adapter override selection in a
single place so rosbag ingestion follows the same plugin-driven planning model as
file-backed datasets.
"""

import logging
from collections.abc import Callable

from mosaicolabs import SessionLevelErrorPolicy

from mosaicopacks.manipulation.contracts import (
    RosbagSequenceDescriptor,
    normalize_topic_name,
)

LOGGER = logging.getLogger(__name__)


class RosbagSequenceExecutor:
    """Execute ingestion plans that delegate message replay to the ROS bridge."""

    def __init__(
        self,
        console,
        host: str,
        port: int,
        log_level: str = "INFO",
        tls_cert_path: str | None = None,
        stop_requested: Callable[[], bool] | None = None,
    ) -> None:
        """Store connection settings used for rosbag uploads."""
        self.console = console
        self.host = host
        self.port = port
        self.log_level = log_level
        self.tls_cert_path = tls_cert_path
        self._stop_requested = stop_requested or (lambda: False)

    def build_config(
        self,
        plan: RosbagSequenceDescriptor,
    ) -> tuple:
        """Resolve requested topics and build the bridge configuration.

        The plugin expresses the desired topics using normalized names. This method
        maps them back to the concrete names present in the bag, filters out missing
        topics, applies adapter overrides only to surviving topics, and returns the
        total message count for reporting.
        """
        from mosaicolabs.ros_bridge import ROSInjectionConfig
        from mosaicolabs.ros_bridge.loader import LoaderErrorPolicy, ROSLoader

        requested_topics = plan.default_topics
        if not requested_topics:
            raise ValueError(
                f"No plugin-default topics matched the requested filters for '{plan.sequence_name}'"
            )

        with ROSLoader(
            file_path=plan.bag_path,
            error_policy=LoaderErrorPolicy.IGNORE,
        ) as loader:
            available_topics = {
                normalize_topic_name(topic_name): topic_name
                for topic_name in loader.topics
            }

            resolved_topics: list[str] = []
            for topic_name in requested_topics:
                normalized_topic = normalize_topic_name(topic_name)
                actual_topic = available_topics.get(normalized_topic)
                if actual_topic is None:
                    LOGGER.warning(
                        "Topic '%s' is missing in '%s'; skipping it.",
                        topic_name,
                        plan.bag_path.name,
                    )
                    continue
                resolved_topics.append(actual_topic)

            if not resolved_topics:
                raise ValueError(
                    f"None of the requested topics were found in '{plan.bag_path.name}'"
                )

            resolved_overrides = {}
            for topic_name, adapter_cls in plan.adapter_overrides.items():
                actual_topic = available_topics.get(normalize_topic_name(topic_name))
                if actual_topic is not None and actual_topic in resolved_topics:
                    resolved_overrides[actual_topic] = adapter_cls

            total_messages = sum(
                loader.msg_count(topic_name) for topic_name in resolved_topics
            )

        config = ROSInjectionConfig(
            file_path=plan.bag_path,
            sequence_name=plan.sequence_name,
            metadata=plan.sequence_metadata,
            host=self.host,
            port=self.port,
            on_error=SessionLevelErrorPolicy.Delete,
            topics=resolved_topics,
            adapter_overrides=resolved_overrides,
            log_level=self.log_level,
            tls_cert_path=self.tls_cert_path,
        )
        return config, total_messages

    def ingest_sequence(
        self,
        plan: RosbagSequenceDescriptor,
        client,
        existing_sequences: set[str] | None = None,
    ) -> bool:
        """Upload one rosbag sequence described by `plan`.

        Returns:
            `True` when the bridge run completed and the sequence is visible in the
            backend, `False` when the sequence was skipped or rejected before upload.
        """
        if existing_sequences is not None and plan.sequence_name in existing_sequences:
            LOGGER.warning(
                "Sequence '%s' already exists, skipping.", plan.sequence_name
            )
            return False

        try:
            config, total_messages = self.build_config(plan)
        except ValueError as exc:
            LOGGER.warning("Skipping sequence '%s': %s", plan.sequence_name, exc)
            return False

        LOGGER.info(
            "Creating rosbag sequence '%s' from %s with %d topic(s), %d message(s)",
            plan.sequence_name,
            plan.bag_path.name,
            len(config.topics or []),
            total_messages,
        )

        from mosaicolabs.ros_bridge import RosbagInjector

        injector = RosbagInjector(config)
        injector.run()

        if self._stop_requested():
            raise KeyboardInterrupt

        remote_sequences = set(client.list_sequences())
        if plan.sequence_name not in remote_sequences:
            LOGGER.error(
                "Rosbag ingestion for '%s' completed but the sequence is not visible via list_sequences().",
                plan.sequence_name,
            )
            return False

        LOGGER.info(
            "Completed rosbag sequence '%s' — %d topic(s), %d message(s)",
            plan.sequence_name,
            len(config.topics or []),
            total_messages,
        )

        if existing_sequences is not None:
            existing_sequences.update(remote_sequences)

        return True
