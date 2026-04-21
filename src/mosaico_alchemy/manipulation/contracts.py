"""
Core contracts shared by dataset plugins and the ingestion runner.

These types describe the hand-off between dataset-specific discovery logic and the
generic upload pipeline. Plugin implementations build descriptors declared here,
while the runner consumes them without needing to know dataset-specific details.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Literal, Protocol, TypeAlias

from mosaicolabs.models import Serializable

if TYPE_CHECKING:
    from mosaicolabs.ros_bridge import ROSAdapterBase


def normalize_topic_name(topic_name: str) -> str:
    """
    Normalizes a user-defined topic name to the canonical absolute form.

    Topic names are exposed remotely and used across adapters, ingestion plans, and
    sequence writers. Centralizing normalization keeps plugin code simple and avoids
    subtle mismatches where one component expects a leading slash and another does not.

    Args:
        topic_name: Topic identifier supplied by a plugin or helper.

    Returns:
        The normalized topic name, always starting with `/`.

    Raises:
        ValueError: If `topic_name` is empty after trimming whitespace.
    """
    topic_name = topic_name.strip()
    if not topic_name:
        raise ValueError("topic_name cannot be empty")
    return topic_name if topic_name.startswith("/") else f"/{topic_name}"


@dataclass
class TopicDescriptor:
    """
    Declares how a single logical topic should be ingested from a dataset sequence.

    A dataset plugin uses this descriptor to tell the runner which ontology message
    to produce, which adapter should perform the translation, and how raw payloads
    are streamed from the source dataset. The descriptor deliberately contains
    callables instead of open file handles so the runner can control execution timing.

    Attributes:
        topic_name: Public topic name that will be created in Mosaico.
        ontology_type: Serializable ontology model expected after adapter translation.
        adapter_id: Registry identifier of the adapter that understands the payloads.
        payload_iter: Factory returning the raw payload stream for a sequence path.
        message_count: Callable used for progress reporting before ingestion starts.
        metadata: Optional schema metadata to attach when creating the topic.
        required_paths: Dataset-relative paths that must exist for the topic to be ingestible.
    """

    topic_name: str
    ontology_type: type[Serializable]
    adapter_id: str
    payload_iter: Callable[[Path], Iterable[dict]]
    message_count: Callable[[Path], int]
    metadata: dict[str, Any] = field(default_factory=dict)
    required_paths: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class SequenceDescriptor:
    """
    Describes a file-backed sequence that can be ingested by the generic runner.

    Dataset plugins return this descriptor when the underlying source data is read
    directly from files. It groups sequence-level metadata with the list of topics to
    ingest so the runner can orchestrate validation, creation, and upload uniformly
    across very different dataset formats.

    Attributes:
        sequence_name: Stable name that will be created remotely for the sequence.
        sequence_metadata: Optional metadata attached to the created sequence.
        topics: Topic declarations that make up the sequence ingestion plan.
        find_missing_paths: Optional validator used to explain which dataset paths are missing.
        backend: Internal discriminator consumed by the runner to select the file executor.
    """

    sequence_name: str
    sequence_metadata: dict[str, Any] = field(default_factory=dict)
    topics: list[TopicDescriptor] = field(default_factory=list)
    find_missing_paths: Callable[[Path, tuple[str, ...]], tuple[str, ...]] | None = None
    backend: str = field(init=False, default="file")


@dataclass
class RosbagSequenceDescriptor:
    """
    Describes a ROS bag sequence that must be ingested through the rosbag executor.

    This variant exists because rosbag-backed datasets are discovered like file-based
    datasets, but ingestion relies on the ROS bridge instead of per-topic payload
    iterators. Keeping a dedicated descriptor makes that backend choice explicit while
    preserving the same plugin-facing workflow.

    Attributes:
        bag_path: Path to the bag file or directory that should be replayed.
        sequence_name: Stable name that will be created remotely for the sequence.
        sequence_metadata: Optional metadata attached to the created sequence.
        default_topics: Topics to ingest when no explicit override is provided elsewhere.
        adapter_overrides: Per-topic adapter overrides for ROS message translation.
        backend: Internal discriminator consumed by the runner to select the rosbag executor.
    """

    bag_path: Path
    sequence_name: str
    sequence_metadata: dict[str, Any] = field(default_factory=dict)
    default_topics: tuple[str, ...] = field(default_factory=tuple)
    adapter_overrides: dict[str, type["ROSAdapterBase"]] = field(default_factory=dict)
    backend: str = field(init=False, default="rosbag")


# Public descriptor union returned by dataset plugins for runner execution.
IngestionDescriptor: TypeAlias = SequenceDescriptor | RosbagSequenceDescriptor
# Supported write modes for file-backed topic ingestion.
WriteMode: TypeAlias = Literal["sync", "async"]


class DatasetPlugin(Protocol):
    """
    Public extension protocol for adding support for a new dataset family.

    A plugin is responsible for three decisions only: whether it recognizes a dataset
    root, which ingestible sequences exist under that root, and how each sequence maps
    to one of the supported ingestion descriptors. Everything after that is handled by
    the shared runner.

    Attributes:
        dataset_id: Stable identifier used in CLI output, reporting, and plugin lookup.
    """

    dataset_id: str

    def supports(self, root: Path) -> bool:
        """
        Returns whether this plugin can interpret the given dataset root.

        The method should be cheap and deterministic because the registry may call it
        repeatedly during auto-detection. It should only answer compatibility, not
        perform expensive discovery or partial ingestion planning.

        Args:
            root: Candidate dataset root passed by the user.

        Returns:
            `True` when the plugin recognizes the dataset layout, else `False`.
        """
        ...

    def discover_sequences(self, root: Path) -> Iterable[Path]:
        """
        Enumerates the ingestible sequences available under a compatible root.

        The returned paths become the unit of work for the runner. Plugins should keep
        this method focused on discovery so failures are easier to report before any
        remote resources are created.

        Args:
            root: Dataset root previously accepted by :meth:`supports`.

        Returns:
            An iterable of paths, each representing one sequence to ingest.
        """
        ...

    def create_ingestion_plan(self, sequence_path: Path) -> IngestionDescriptor:
        """
        Builds the ingestion descriptor consumed by the shared runner.

        This is the main hand-off point between plugin code and the orchestration layer.
        The returned descriptor must be self-contained: the runner should not need any
        plugin-specific branching after receiving it.

        Args:
            sequence_path: Sequence selected during discovery.

        Returns:
            A descriptor describing how the sequence should be ingested.
        """
        ...
