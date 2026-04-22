<p align="center">
  <img src="https://raw.githubusercontent.com/mosaico-labs/mosaico/main/logo/mono_black.svg" width="300" alt="Mosaico Logo">
</p>

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)

# Mosaico Packs

The **Mosaico Packs** repository provides ready-to-use ingestion pipelines for the **Mosaico Data Platform**.

Each pack translates heterogeneous dataset formats into the same ontology used by the **Mosaico SDK**, so you can ingest once and query robotics data through one consistent semantic model. The current open-source release focuses on **robotic manipulation** workloads.

Documentation is available on [docs.mosaico.dev](https://docs.mosaico.dev/), including the [Packs overview](https://docs.mosaico.dev/SDK/packs/) and the [Manipulation Pack guide](https://docs.mosaico.dev/SDK/packs/manipulation/).

## Key Features

* **Pack-Oriented CLI**: A single `mosaicopacks` entrypoint dispatches execution to the selected pack.
* **Built-in Manipulation Support**: Ships with ingestion plugins for `reassemble`, `fractal_rt1`, `droid`, and `mml`.
* **Unified Ontology Mapping**: Normalizes HDF5, TFDS, Parquet/MP4, and ROS bag sources into Mosaico ontology types.
* **Multiple Execution Backends**: Supports both file-backed ingestion flows and rosbag-based replay flows.
* **Extensible Architecture**: New datasets can be added through registries for dataset plugins and adapters.
* **Rich Terminal Reporting**: Includes progress summaries, dataset/run reports, and optional log-file output.

## Installation

Clone the repository, then install and run the project with **Poetry**:

```bash
cd mosaico-packs
poetry install
eval $(poetry env activate)
```

*Note: Requires Python 3.11 or higher.*

## Available Packs

The top-level CLI exposes the packs bundled in the repository:

```bash
# Show the global dispatcher help
mosaicopacks -h

# Show the manipulation pack usage
mosaicopacks manipulation -h
```

At the moment, the bundled open-source pack is:

* `manipulation`: ingestion suite for robotic manipulation datasets and demonstrations.

## Infrastructure Prerequisite

Before running any pack, ensure your **Mosaico Infrastructure** is active and reachable.
Please refer to the **[daemon setup](https://docs.mosaico.dev/daemon/install/)** documentation.

```python
from mosaicolabs import MosaicoClient

# Connect to the Mosaico server
with MosaicoClient.connect(host="localhost", port=6726) as client:
    # Simple is-alive check
    print(client.version())
```

## Quick Start

Run the manipulation pack against one or more dataset roots:

```bash
mosaicopacks manipulation \
  --datasets /path/to/reassemble /path/to/droid \
  --host localhost \
  --port 6726 \
  --write-mode sync
```

The CLI currently requires an **interactive terminal**. For each dataset root, it prompts you to choose one of the registered plugins or skip the dataset entirely.

## Supported Manipulation Datasets

| Dataset ID | Expected Source Format | Execution Backend |
| :--- | :--- | :--- |
| `reassemble` | HDF5 sequences (`*.h5`) | `file` |
| `fractal_rt1` | TensorFlow Datasets export | `file` |
| `droid` | Parquet episodes with companion MP4 assets | `file` |
| `mml` | ROS bag recordings (`*.bag`) | `rosbag` |

These built-in plugins cover common manipulation modalities including RGB frames, event-camera data, robot joint state, cartesian pose and velocity, audio, tactile sensing, reward/step annotations, and language-conditioned episode metadata.

## CLI Options

The manipulation pack supports the following flags:

| Option | Default | Description |
| :--- | :--- | :--- |
| `--datasets` | Required | One or more dataset roots to ingest. |
| `--host` | `localhost` | Hostname of the target Mosaico server. |
| `--port` | `6726` | Port of the target Mosaico server. |
| `--log-level` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |
| `--log-file` | `None` | Optional file path for persisted SDK logs. |
| `--write-mode` | `sync` | Topic write mode for file-backed datasets (`sync` or `async`). |

## Extending the Pack

The manipulation pipeline is designed to be extended with custom dataset plugins, topic adapters, and ontology models.

See the [integration guide](https://docs.mosaico.dev/SDK/packs/manipulation/integrating/) for the plugin protocol, execution backends, adapter registration, and ingestion-plan structure used by the runner.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. See the `LICENSE` file for more details.
