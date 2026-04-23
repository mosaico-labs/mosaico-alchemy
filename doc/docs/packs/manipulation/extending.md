---
title: Integrating a Dataset
description: A discursive guide to adding a new dataset plugin to the Manipulation Pack.
---

This guide explains how to extend the Manipulation Pack to support your own custom dataset formats alongside the built-in ones. 

??? question "In Depth Explanation"
    * **[Documentation: Data Models & Ontology](https://docs.mosaico.dev/SDK/ontology)**
    * **[Example: Customizing the Data Ontology](https://docs.mosaico.dev/SDK/examples/ontology_customization)**
    * **[API Reference: Base Models and Mixins](https://docs.mosaico.dev/SDK/API_reference/models/base)**
    * **[Documentation: The ROS Bridge](https://docs.mosaico.dev/SDK/bridges/ros)**

By following this guide, you will:

* **Select an Execution Backend**: Decide whether to rely natively on ROS bag architectures or to construct a structured File descriptor pipeline.
* **Define Ontologies and Adapters**: Choose the Mosaico types that model your sensor streams and implement the adapters that translate raw dictionaries into them.
* **Implement the Dataset Plugin**: Assemble the ingestion plan that wires your iterators, ontologies, and adapters into a declarative sequence descriptor.
* **Register Your Components**: Expose your plugin and adapters to the CLI layer so they are discovered at runtime.

## Step 1: Choosing the Execution Backend

Your first architectural decision is deciding how the data should be accessed. If your dataset relies on standard file and database formats such as HDF5, Parquet, JSON, or custom binary files, you will utilize the file-backed executor by generating a `SequenceDescriptor`. 

Alternatively, if your dataset consists of native ROS bags and maps naturally to ROS topics, you should use a `RosbagSequenceDescriptor`. This allows the plugin to validate the required topics and immediately delegate the demanding ingestion effort directly to the ROS bridge.

## Step 2: Applying Ontologies and Implementing Adapters

For each data stream, you define how it maps to a Mosaico ontology type. If you cannot reuse an existing SDK ontology, you can define your own custom class. We highly recommend reviewing the **[Ontology Customization Guide](https://docs.mosaico.dev/SDK/examples/ontology_customization)** to see exactly how to write and register your own custom data models.

### The Custom Adapter

With your ontologies defining the target structure, you implement a custom adapter.

```python
from mosaicolabs import Message
from mosaicolabs.packs.manipulation.adapters.base import BaseAdapter

class MyDatasetCustomAdapter(BaseAdapter):
    adapter_id = "mydataset.custom_sensor" # (1)!
    ontology_type = CustomSensorModel # (2)!

    @classmethod
    def translate(cls, payload: dict) -> Message: # (3)!
        """
        Translates a raw custom dictionary into a Mosaico Message container.
        """
        return Message(
            timestamp_ns=int(payload["timestamp"] * 1e9), # (4)!
            data=CustomSensorModel(values=payload["sensor_readings"]),
        )
```

1. The global identifier that will be referenced by name in your `TopicDescriptor`.
2. The Mosaico ontology type (defined from the base `Serializable` structures) that this adapter handles.
3. This is the heart of the translator. An adapter receives the raw payload dictionary from your custom iterator and returns an instantiated Mosaico message.
4. Accurate conversion from arbitrary time structures into native Mosaico nanosecond formats.

## Step 3: Developing the Dataset Plugin

With adapters in place, you implement the dataset plugin class. This class satisfies a straightforward internal protocol to detect your dataset format, discover its logical sequences, and assemble the ingestion plan that wires everything together.

### The Plugin Protocol

```python
class DatasetPlugin(Protocol):
    dataset_id: str # (1)!

    def supports(self, root: Path) -> bool: ... # (2)!
    def discover_sequences(self, root: Path) -> Iterable[Path]: ... # (3)!
    def create_ingestion_plan(self, sequence_path: Path) -> IngestionDescriptor: ... # (4)!
```

1. A unique string identifier used in downstream logging and operator prompts.
2. A fast, deterministic method to verify if a given folder matches the dataset signature (e.g., checking for `*.h5` files) avoiding expensive full-dataset scans.
3. A method to discover the logical sequences contained in the root folder, such as individual robot episodes.
4. The core logic to create an ingestion plan for each sequence, returning an `IngestionDescriptor`.

### Extracting Raw Data

To keep your plugin code clean and maintainable, raw file I/O operations must be completely separated from the orchestration step. You should create dedicated iterator functions following the **factory pattern**: each function accepts static configuration parameters (file paths, field names) and returns a `Callable[[Path], Iterable[dict]]`. The runner calls that callable later with the actual sequence path to stream the raw payloads. Each payload dict must include a `"timestamp"` key expressed in seconds as a float.

```python
def iter_video_frames(video_path: str, timestamps_path: str) -> Callable[[Path], Iterable[dict]]:
    def _fn(sequence_path: Path) -> Iterable[dict]:
        # open sequence_path and read the data at video_path / timestamps_path
        yield {"timestamp": 1234.56, "image": b"..."}
    return _fn

def count_video_frames(timestamps_path: str) -> Callable[[Path], int]:
    def _fn(sequence_path: Path) -> int:
        # count the number of frames at timestamps_path
        return total_frames
    return _fn
```

### Structuring the Ingestion Plan

The plugin implements `create_ingestion_plan` to declare the sequence name, its metadata, and the full list of topics. Each topic references the iterators and adapters you built in the previous steps.

```python
return SequenceDescriptor(
    sequence_name=f"{self.dataset_id}_{sequence_path.stem}", # (1)!
    sequence_metadata={
        "dataset_id": self.dataset_id,
        "ingestion_backend": "file",
    },
    topics=[
        TopicDescriptor(
            topic_name="/camera/front",
            ontology_type=CompressedImage, # (2)!
            adapter_id=f"{self.dataset_id}.video_frame", # (3)!
            payload_iter=iter_video_frames("path/to/video", "path/to/timestamps"), # (4)!
            message_count=count_video_frames("path/to/timestamps"), # (5)!
        ),
    ],
)
```

1. The unique name of the target sequence being constructed.
2. The Mosaico ontology type that models this data stream.
3. The string identifier for the adapter responsible for translating this specific topic.
4. A factory call that returns a `Callable[[Path], Iterable[dict]]`. The runner calls this callable later with the sequence path to obtain the raw payload stream.
5. A factory call that returns a `Callable[[Path], int]`. The runner uses this to count the total messages ahead of time for progress reporting. It must match the number of items `payload_iter` will yield.

## Step 4: Registering Your Components

Once your dataset plugin, functional iterators, and adapters are implemented, they must be made discoverable to the CLI layer. There are two separate registries to update: one for the dataset plugin and one for the adapter.

### Registering the Dataset Plugin

```python
def build_default_dataset_registry() -> DatasetRegistry: # (1)!
    registry = DatasetRegistry()
    registry.register(MyDatasetPlugin()) # (2)!
    return registry
```

1. This hook initiates the CLI layer default options.
2. Registers the plugin so your custom dataset natively appears alongside the officially supported robotics datasets in the interactive CLI prompts.

### Registering the Adapter

The adapter must also be registered in the `AdapterRegistry`. Without this step, the file executor will not be able to resolve the `adapter_id` declared in your `TopicDescriptor` and the ingestion will fail.

```python
def build_default_adapter_registry() -> AdapterRegistry: # (1)!
    registry = AdapterRegistry()
    registry.register(MyDatasetCustomAdapter) # (2)!
    return registry
```

1. This hook initiates the adapter registry used by the file executor to resolve `adapter_id` strings at ingestion time.
2. Registers the adapter class so the executor can look it up by its `adapter_id` when processing each topic.

After registering both components, your dataset plugin is ready to be executed.