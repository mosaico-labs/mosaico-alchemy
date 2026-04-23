<p align="center">
  <img src="https://raw.githubusercontent.com/mosaico-labs/mosaico/main/logo/mono_white.svg" width="300" alt="Mosaico Logo">
</p>

# Mosaico Alchemy

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Documentation (Mosaico Alchemy)](https://img.shields.io/badge/docs-Mosaico%20Alchemy-blue?logo=readthedocs&logoColor=white)](https://your-project.readthedocs.io)
[![Documentation (Mosaico)](https://img.shields.io/badge/docs-Mosaico-blue?logo=readthedocs&logoColor=white&labelColor=gray)](https://docs.mosaico.dev)

A collection of ready-to-use ingestion pipelines showcasing the import of public datasets into the [Mosaico Data Platform](https://github.com/mosaico-labs/mosaico).

## Overview

The **Mosaico Alchemy** repository provides ready-to-use ingestion pipelines, showing how datatest can be ingested into the **Mosaico Data Platform**.

The project is organized in *Packs*, where each *Pack* is focused on a specific use-case (like **Robotic Manipulation**) and translates heterogeneous dataset formats into the same ontology used by the [**Mosaico SDK**](https://docs.mosaico.dev/SDK/), so you can ingest once and query robotics data through one consistent semantic model.

## Key Features

* **Pack-Oriented CLI**: A single `mosaico_alchemy` entrypoint dispatches execution to the selected *alchemy*.
* **Unified Ontology Mapping**: Normalizes different source formats (like HDF5, TFDS, Parquet/MP4, and ROS bag) into **Mosaico Sequences and Ontology Models**.
* **Multiple Execution Backends**: Supports both file-backed ingestion flows and rosbag-based replay flows.
* **Extensible Architecture**: New datasets can be added through registries for dataset plugins and adapters.
* **Rich Terminal Reporting**: Includes progress summaries, dataset/run reports, and optional log-file output.

## Available Packs

| Pack | Description | Status |
|:--------|:------------|:-------|
| [Manipulation](src/mosaico_alchemy/manipulation/) | Built-in Manipulation Support: Ships with ingestion plugins for public datatets like [`reassemble`](https://tuwien-asl.github.io/REASSEMBLE_page/), [`fractal_rt1`](https://research.google/blog/rt-1-robotics-transformer-for-real-world-control-at-scale/), [`droid`](https://huggingface.co/datasets/lerobot/droid_1.0.1), and [`mml`](https://zenodo.org/records/6372438). | ✅ Ready |

## Installation

### Mosaico

Before running any mosaico service via SDK (included the *alchemy-packs* in this project), ensure your **Mosaico Infrastructure** is active and running. 
The easiest way to start is using the provided **[Quick Start environment via Containers](https://docs.mosaico.dev/daemon/install/)**.

### Mosaico-Alchemy

Clone this repository, then install and run the project with **Poetry**:

```bash
cd mosaico-alchemy
poetry install
eval $(poetry env activate)
```

*Note: Requires Python 3.10 or higher.*

The top-level CLI exposes the *alchemies* bundled in the repository:

```bash
# Show the global dispatcher help
mosaico_alchemy -h

# E.g.: Show the manipulation alchemy usage
mosaico_alchemy manipulation -h
```

## Quick Start

As an example Run the manipulation alchemy against one or more dataset roots:

```bash
mosaico_alchemy manipulation \
  --datasets /path/to/reassemble /path/to/droid \
  --host localhost \
  --port 6726 \
  --write-mode sync
```

The CLI currently requires an **interactive terminal**. For each dataset root, it prompts you to choose one of the registered plugins or skip the dataset entirely.

## License

This project is licensed under the **Apache License v2.0 (Apache-2.0)**. See the `LICENSE` file for more details.
