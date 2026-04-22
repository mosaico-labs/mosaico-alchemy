"""
Iterator factories and episode helpers for Fractal RT-1 TFDS datasets.

Fractal RT-1 episodes are stored inside TFDS shards, so this module provides the
translation layer between TFDS access patterns and the callable interface expected
by `TopicDescriptor`. It also defines the virtual sequence identifiers used by the
runner to treat each episode like a standalone sequence.
"""

import functools
from pathlib import Path
from typing import Callable, Iterable

from mosaicopacks.manipulation.readers.tfds_reader import TFDSReader

VIRTUAL_SEPARATOR = "@@"
VIRTUAL_SUFFIX = ".episode"
STEP_RATE_HZ = 3.0
STEP_PERIOD_NS = 1_000_000_000 / STEP_RATE_HZ


def num_examples(root: Path) -> int:
    """Returns the total number of examples exposed by the TFDS train split."""
    with TFDSReader(root) as reader:
        return reader.num_examples


def available_episodes(root: Path) -> list[int]:
    """Returns the episode indices that are actually available on disk."""
    with TFDSReader(root) as reader:
        return reader.available_episodes


@functools.lru_cache(maxsize=8)
def _dataset_feature_paths(root_str: str) -> frozenset[str]:
    """Caches the flattened TFDS feature paths available under one dataset root."""
    with TFDSReader(root_str) as reader:
        return reader.dataset_feature_paths


@functools.lru_cache(maxsize=8)
def average_episode_size_bytes(root_str: str) -> int:
    """
    Estimates the average on-disk size of one Fractal RT-1 episode.

    The dataset is stored in shared TFRecord shards, so the estimate is derived by
    dividing the total shard size by the number of available episodes. The result is
    approximate, but good enough for reporting and progress metadata.
    """
    root = Path(root_str)
    total_size_bytes = sum(p.stat().st_size for p in root.glob("*.tfrecord-*"))
    return total_size_bytes // max(1, len(available_episodes(root)))


def make_virtual_sequence_path(root: Path, episode_index: int) -> Path:
    """
    Builds the synthetic path used to identify one TFDS episode as a sequence.

    The returned path is not expected to exist on disk. It is a stable identifier
    that keeps the runner, reporters, and descriptor APIs file-oriented even though
    Fractal RT-1 episodes live inside shared TFDS shards.
    """
    return root / f"train{VIRTUAL_SEPARATOR}{episode_index:06d}{VIRTUAL_SUFFIX}"


def parse_virtual_sequence_path(sequence_path: Path) -> tuple[Path, int]:
    """
    Parses a synthetic Fractal RT-1 sequence path back into root and episode index.

    Args:
        sequence_path: Virtual sequence path produced by `make_virtual_sequence_path`.

    Returns:
        The dataset root and the referenced episode index.

    Raises:
        ValueError: If the path does not follow the Fractal RT-1 virtual naming scheme.
    """
    if VIRTUAL_SEPARATOR not in sequence_path.name:
        raise ValueError(f"Invalid fractal_rt1 sequence path '{sequence_path}'")
    stem, suffix = sequence_path.name.split(VIRTUAL_SEPARATOR, 1)
    if stem != "train":
        raise ValueError(f"Unsupported split in sequence path '{sequence_path}'")
    return sequence_path.parent, int(suffix.removesuffix(VIRTUAL_SUFFIX))


@functools.lru_cache(maxsize=16)
def _load_episode(sequence_path_str: str) -> dict:
    """Caches one decoded TFDS episode keyed by its virtual sequence path."""
    root, episode_index = parse_virtual_sequence_path(Path(sequence_path_str))
    with TFDSReader(root) as reader:
        return reader.load_episode(episode_index)


def _steps(sequence_path: Path) -> list[dict]:
    """Normalizes an episode into a step-by-step list of payload dictionaries."""
    episode = _load_episode(str(sequence_path))
    steps = episode.get("steps", [])
    if isinstance(steps, dict):
        return [
            TFDSReader.index_tree(steps, idx)
            for idx in range(TFDSReader.sequence_length(steps))
        ]
    return list(steps)


def count_steps() -> Callable[[Path], int]:
    """Builds a counter factory returning the number of steps in one episode."""
    return lambda seq_path: len(_steps(seq_path))


def _timestamp_ns(step_index: int) -> int:
    return int(round(step_index * STEP_PERIOD_NS))


def iter_episode_value(
    field_path: str,
    *,
    payload_key: str = "value",
    transform: Callable[[object], object] | None = None,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds an iterator factory for one episode-level TFDS field.

    Episode-level values are emitted once with a synthetic timestamp because they
    describe the episode as a whole rather than one individual step.

    Args:
        field_path: Dotted path to the episode-level TFDS feature.
        payload_key: Key used in the yielded payload dictionary.
        transform: Optional value conversion applied before yielding the payload.

    Returns:
        A callable that accepts a virtual sequence path and yields one payload.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        episode = _load_episode(str(sequence_path))
        value = TFDSReader.get_nested(episode, field_path)
        if transform is not None:
            value = transform(value)
        yield {"timestamp": 0.0, payload_key: value}

    return _fn


def iter_step_value(
    field_path: str,
    *,
    payload_key: str = "value",
    transform: Callable[[object], object] | None = None,
) -> Callable[[Path], Iterable[dict]]:
    """
    Builds an iterator factory for one step-level TFDS field.

    Step timestamps are synthesized from a fixed rate because Fractal RT-1 episodes
    are consumed as ordered control steps rather than as measurements carrying a
    native timestamp per field.

    Args:
        field_path: Dotted path to the step-level TFDS feature.
        payload_key: Key used in the yielded payload dictionary.
        transform: Optional value conversion applied before yielding the payload.

    Returns:
        A callable that accepts a virtual sequence path and yields step payloads.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        for step_index, step in enumerate(_steps(sequence_path)):
            value = TFDSReader.get_nested(step, field_path)
            if transform is not None:
                value = transform(value)
            yield {"timestamp_ns": _timestamp_ns(step_index), payload_key: value}

    return _fn


def iter_step_image(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """Builds an image payload iterator factory for one step-level feature."""
    return iter_step_value(field_path, payload_key="image")


def iter_step_pose(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """Builds a pose payload iterator factory for one step-level feature."""
    return iter_step_value(field_path, payload_key="pose", transform=TFDSReader.as_list)


def iter_step_vector(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """Builds a vector payload iterator factory for one step-level feature."""
    return iter_step_value(
        field_path, payload_key="vector", transform=TFDSReader.as_list
    )


def iter_step_values(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """Builds a multi-value payload iterator factory for one step-level feature."""
    return iter_step_value(
        field_path, payload_key="values", transform=TFDSReader.as_list
    )


def iter_step_scalar(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """Builds a scalar payload iterator factory for one step-level feature."""
    return iter_step_value(
        field_path, payload_key="value", transform=TFDSReader.as_scalar
    )


def iter_step_terminate_episode(field_path: str) -> Callable[[Path], Iterable[dict]]:
    """
    Builds the iterator factory for terminate-episode action payloads.

    The TFDS field is normalized to a list of integers because the downstream
    ontology expects the termination signal as an explicit numeric vector.
    """

    def _fn(sequence_path: Path) -> Iterable[dict]:
        for step_index, step in enumerate(_steps(sequence_path)):
            value = [
                int(v)
                for v in TFDSReader.as_list(TFDSReader.get_nested(step, field_path))
            ]
            yield {"timestamp_ns": _timestamp_ns(step_index), "value": value}

    return _fn
