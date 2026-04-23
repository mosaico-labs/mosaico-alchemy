"""
High-level orchestration for manipulation dataset ingestion.

This module coordinates dataset discovery, plan creation, executor selection, and
report aggregation. It is the layer that turns plugin-specific descriptors into one
consistent ingestion workflow, regardless of whether the underlying backend is file-
based or rosbag-based.
"""

import logging
import time
from collections.abc import Callable
from pathlib import Path

from mosaicolabs import MosaicoClient
from mosaicolabs.handlers.sequence_handler import SequenceHandler
from mosaicolabs.platform.helpers import _decode_app_metadata
from rich.console import Console
from rich.panel import Panel

from mosaico_alchemy.manipulation.contracts import (
    DatasetPlugin,
    RosbagSequenceDescriptor,
    SequenceDescriptor,
    WriteMode,
)
from mosaico_alchemy.manipulation.datasets import (
    DatasetRegistry,
    build_default_dataset_registry,
)
from mosaico_alchemy.manipulation.runner.executors.file_executor import (
    FileSequenceExecutor,
)
from mosaico_alchemy.manipulation.runner.executors.rosbag_executor import (
    RosbagSequenceExecutor,
)
from mosaico_alchemy.manipulation.runner.reporters.reports import (
    DatasetIngestionReport,
    SequenceIngestionResult,
)

LOGGER = logging.getLogger(__name__)


class ManipulationRunner:
    """
    Orchestrates ingestion for one or more manipulation dataset roots.

    The runner owns the boundary between plugin discovery and execution. Plugins only
    describe sequences; executors only know how to ingest a prepared plan. This class
    connects the two and turns their outcomes into structured reports.
    """

    def __init__(
        self,
        console: Console | None = None,
        host: str = "localhost",
        port: int = 6276,
        tls_cert_path: str | None = None,
        log_level: str = "INFO",
        write_mode: WriteMode = "sync",
        stop_requested: Callable[[], bool] | None = None,
        dataset_registry: DatasetRegistry | None = None,
    ) -> None:
        """Initializes the runner with shared executors and plugin registry state."""
        self.console = console or Console(stderr=True)
        self.dataset_registry = dataset_registry or build_default_dataset_registry()
        self._stop_requested = stop_requested or (lambda: False)
        self._file_executor = FileSequenceExecutor(
            self.console,
            write_mode=write_mode,
        )
        self._rosbag_executor = RosbagSequenceExecutor(
            console=self.console,
            host=host,
            port=port,
            log_level=log_level,
            tls_cert_path=tls_cert_path,
            stop_requested=self._stop_requested,
        )

    def ingest_root(
        self,
        root: Path,
        client: MosaicoClient,
        dataset_index: int | None = None,
        dataset_total: int | None = None,
        selected_plugin_id: str | None = None,
    ) -> DatasetIngestionReport:
        """
        Ingests one dataset root and returns the aggregated dataset-level report.

        The method resolves the dataset plugin, discovers sequences, delegates each
        sequence to the appropriate executor, and then enriches the final report with
        timing and remote-size information.

        Args:
            root: Dataset root requested by the caller.
            client: Connected Mosaico client used for discovery and ingestion.
            dataset_index: Optional one-based dataset position for logging.
            dataset_total: Optional total number of dataset roots in the run.
            selected_plugin_id: Optional plugin id chosen explicitly by the caller.

        Returns:
            The report summarizing ingestion for the dataset root.
        """
        dataset_start = time.monotonic()
        dataset_label = (
            f"[{dataset_index}/{dataset_total}] "
            if dataset_index and dataset_total
            else ""
        )

        if self._stop_requested():
            return self._build_interrupted_report(root, dataset_start)

        if not root.exists():
            return self._handle_missing_root(root, dataset_label, dataset_start)

        discovery = self._discover_sequences(
            root, dataset_start, selected_plugin_id=selected_plugin_id
        )
        if isinstance(discovery, DatasetIngestionReport):
            return discovery
        plugin, plugin_id, sequence_paths = discovery

        report = DatasetIngestionReport(
            root=root,
            plugin_id=plugin_id,
            discovered=len(sequence_paths),
        )

        existing_sequences = self._get_existing_sequences(client, report)

        LOGGER.info(
            "%sDataset '%s' from %s with %d sequence(s)",
            dataset_label,
            plugin_id,
            root,
            len(sequence_paths),
        )
        LOGGER.info("Found %d existing sequence(s) on server", len(existing_sequences))

        if not sequence_paths:
            return self._finalize_empty_report(report, dataset_label, dataset_start)

        self._process_sequences(
            sequence_paths,
            plugin,
            client,
            existing_sequences,
            report,
        )

        report.duration_s = time.monotonic() - dataset_start
        report.finalize(
            interrupted=report.status == "interrupted" or self._stop_requested()
        )
        report.remote_size_bytes = self._resolve_remote_size(client, report)

        LOGGER.info(
            "%sCompleted dataset '%s' — discovered=%d ingested=%d skipped=%d failed=%d duration=%.2fs",
            dataset_label,
            plugin_id,
            report.discovered,
            report.ingested,
            report.skipped,
            report.failed,
            report.duration_s,
        )

        return report

    def _build_interrupted_report(
        self, root: Path, start_time: float
    ) -> DatasetIngestionReport:
        """Builds the dataset report used when ingestion is interrupted early."""
        report = DatasetIngestionReport.interrupted_report(root=root)
        report.duration_s = time.monotonic() - start_time
        return report

    def _handle_missing_root(
        self, root: Path, label: str, start_time: float
    ) -> DatasetIngestionReport:
        """Builds the failure report used when the requested dataset root is missing."""
        report = DatasetIngestionReport.failed_report(
            root=root,
            error=f"Dataset root does not exist: {root}",
        )
        report.duration_s = time.monotonic() - start_time
        LOGGER.error("%sDataset root does not exist: %s", label, root)
        return report

    def _discover_sequences(
        self,
        root: Path,
        start_time: float,
        selected_plugin_id: str | None = None,
    ) -> tuple | DatasetIngestionReport:
        """
        Resolves the dataset plugin and discovers the sequence paths under one root.

        Returns either the successful discovery tuple or an already-populated failure
        report so callers can keep the control flow simple.
        """
        try:
            if selected_plugin_id is None:
                plugin = self.dataset_registry.resolve(root)
            else:
                plugin = self.dataset_registry.get(selected_plugin_id)
            plugin_id = getattr(plugin, "dataset_id", type(plugin).__name__)
            sequence_paths = list(plugin.discover_sequences(root))
            return plugin, plugin_id, sequence_paths
        except KeyError:
            return DatasetIngestionReport.failed_report(
                root=root,
                plugin_id=selected_plugin_id or "unresolved",
                error=f"Unknown dataset plugin '{selected_plugin_id}'.",
                duration_s=time.monotonic() - start_time,
            )
        except Exception:
            LOGGER.exception("Failed to resolve dataset root %s", root)
            return DatasetIngestionReport.failed_report(
                root=root,
                plugin_id="unresolved",
                error=f"Failed to resolve dataset root '{root}'.",
                duration_s=time.monotonic() - start_time,
            )

    def _get_existing_sequences(
        self, client: MosaicoClient, report: DatasetIngestionReport
    ) -> set[str]:
        """
        Retrieves the remote sequence names used for skip detection.

        Failures are downgraded to warnings so ingestion can continue even when the
        optimization is unavailable.
        """
        try:
            return set(client.list_sequences())
        except Exception:
            LOGGER.exception(
                "Failed to list existing sequences; continuing without skip detection."
            )
            report.warnings.append(
                "Failed to list existing sequences; skip detection was disabled."
            )
            return set()

    def _finalize_empty_report(
        self, report: DatasetIngestionReport, label: str, start_time: float
    ) -> DatasetIngestionReport:
        """Finalizes the report for a dataset root that yielded no sequences."""
        LOGGER.warning("No sequences discovered under %s", report.root)
        report.duration_s = time.monotonic() - start_time
        report.remote_size_bytes = 0
        LOGGER.info(
            "%sCompleted dataset '%s' — discovered=0 ingested=0 skipped=0 failed=0 duration=%.2fs",
            label,
            report.plugin_id,
            report.duration_s,
        )
        return report

    def _process_sequences(
        self,
        sequence_paths: list[Path],
        plugin: DatasetPlugin,
        client: MosaicoClient,
        existing_sequences: set[str],
        report: DatasetIngestionReport,
    ) -> None:
        """Processes each discovered sequence in order and records its result."""
        for index, sequence_path in enumerate(sequence_paths, start=1):
            if self._stop_requested():
                self._mark_report_interrupted(report)
                break

            LOGGER.info(
                "Ingesting sequence %d/%d from %s",
                index,
                len(sequence_paths),
                sequence_path,
            )
            try:
                sequence_result = self.ingest_sequence(
                    sequence_path,
                    plugin,
                    client,
                    existing_sequences=existing_sequences,
                )
            except KeyboardInterrupt:
                self._mark_report_interrupted(report)
                break
            except Exception:
                LOGGER.exception(
                    "Sequence '%s' failed; continuing with the next sequence.",
                    sequence_path.name,
                )
                sequence_result = SequenceIngestionResult(
                    sequence_name=sequence_path.name,
                    status="failed",
                    local_size_bytes=self._get_local_sequence_size(sequence_path),
                    error=f"Sequence '{sequence_path.name}' failed unexpectedly.",
                )

            report.record_sequence(sequence_result)
            if sequence_result.status == "interrupted":
                self._mark_report_interrupted(report)
                break

    def _mark_report_interrupted(self, report: DatasetIngestionReport) -> None:
        """Marks the dataset report as interrupted and records a standard error message."""
        report.status = "interrupted"
        report.errors.append("Interrupted by user.")

    def ingest_sequence(
        self,
        sequence_path: Path,
        plugin: DatasetPlugin,
        client: MosaicoClient,
        existing_sequences: set[str] | None = None,
    ) -> SequenceIngestionResult:
        """
        Ingests one logical sequence produced by a dataset plugin.

        The runner first asks the plugin for an ingestion plan, then dispatches that
        plan to the matching executor based on its backend. Any unexpected failure is
        converted into a structured result so the dataset-level loop can keep going.

        Args:
            sequence_path: Sequence or virtual sequence identifier discovered by the plugin.
            plugin: Dataset plugin responsible for building the ingestion plan.
            client: Connected Mosaico client used by the executor.
            existing_sequences: Optional cache of already-existing remote sequences.

        Returns:
            The structured result of ingesting, skipping, failing, or interrupting the sequence.
        """
        try:
            plan = plugin.create_ingestion_plan(sequence_path)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            LOGGER.exception(
                "Failed to create ingestion plan for sequence '%s'.",
                sequence_path.name,
            )
            return self._build_sequence_error_result(
                sequence_name=sequence_path.name,
                local_size=self._get_local_sequence_size(sequence_path),
                error=f"Failed to create ingestion plan for '{sequence_path.name}': {exc}",
            )

        local_size = self._get_local_sequence_size(sequence_path, plan)
        backend = getattr(plan, "backend", "file")

        if self._stop_requested():
            return self._build_sequence_interrupted_result(plan, local_size, backend)

        try:
            if isinstance(plan, RosbagSequenceDescriptor):
                ingested = self._rosbag_executor.ingest_sequence(
                    plan,
                    client=client,
                    existing_sequences=existing_sequences,
                )
            else:
                ingested = self._file_executor.ingest_sequence(
                    sequence_path,
                    plan,
                    client=client,
                    existing_sequences=existing_sequences,
                )
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            LOGGER.exception(
                "Sequence '%s' failed; continuing with the next sequence.",
                sequence_path.name,
            )
            return self._build_sequence_error_result(
                sequence_name=plan.sequence_name,
                local_size=local_size,
                error=f"Sequence '{plan.sequence_name}' failed: {exc}",
                backend=backend,
                plan=plan,
            )

        if self._stop_requested():
            return self._build_sequence_interrupted_result(plan, local_size, backend)

        if ingested:
            try:
                remote_size = self._get_remote_sequence_size(client, plan.sequence_name)
                self._print_injection_summary(
                    plan.sequence_name, local_size, remote_size
                )
            except Exception:
                LOGGER.debug(
                    "Could not retrieve remote size for injection summary of '%s'.",
                    plan.sequence_name,
                )

        return SequenceIngestionResult(
            sequence_name=plan.sequence_name,
            status="ingested" if ingested else "skipped",
            local_size_bytes=local_size,
            backend=backend,
            plan=plan,
        )

    def _build_sequence_error_result(
        self,
        sequence_name: str,
        local_size: int,
        error: str,
        backend: str | None = None,
        plan=None,
    ) -> SequenceIngestionResult:
        """Builds a standardized failed sequence result."""
        return SequenceIngestionResult(
            sequence_name=sequence_name,
            status="failed",
            local_size_bytes=local_size,
            backend=backend,
            plan=plan,
            error=error,
        )

    def _build_sequence_interrupted_result(
        self, plan, local_size: int, backend: str
    ) -> SequenceIngestionResult:
        """Builds a standardized interrupted sequence result."""
        return SequenceIngestionResult(
            sequence_name=plan.sequence_name,
            status="interrupted",
            local_size_bytes=local_size,
            backend=backend,
            plan=plan,
            error="Interrupted by user.",
        )

    def _print_injection_summary(
        self, sequence_name: str, local_size: int, remote_size: int
    ) -> None:
        if local_size == 0 or remote_size == 0:
            LOGGER.warning(
                "Skipping injection summary for '%s' due to zero local or remote size (local_size=%d, remote_size=%d).",
                sequence_name,
                local_size,
                remote_size,
            )
            return

        ratio = local_size / remote_size
        savings = max(0.0, (1 - (remote_size / local_size)) * 100)
        mb = 1024 * 1024
        summary_text = (
            f"Sequence:      [bold]{sequence_name}[/bold]\n"
            f"Original Size: [bold]{local_size / mb:.2f} MB[/bold]\n"
            f"Remote Size:   [bold]{remote_size / mb:.2f} MB[/bold]\n"
            f"Ratio:         [bold cyan]{ratio:.2f}x[/bold cyan]\n"
            f"Space Saved:   [bold green]{savings:.1f}%[/bold green]"
        )
        self.console.print(
            Panel(
                summary_text,
                title="[bold]Injection Summary[/bold]",
                expand=False,
                border_style="green",
                padding=1,
                highlight=True,
            )
        )

    def _get_local_sequence_size(
        self,
        sequence_path: Path,
        plan: SequenceDescriptor | RosbagSequenceDescriptor | None = None,
    ) -> int:
        """
        Estimates the local size attributable to one logical sequence.

        For virtual per-episode paths, the method tries to divide the shared backing
        file size by the number of episodes so reporting remains closer to the logical
        ingestion unit than to the container file.
        """
        if plan is not None:
            estimated_size = plan.sequence_metadata.get("estimated_local_size_bytes")
            if estimated_size is not None:
                return int(estimated_size)

        real_path = sequence_path
        episode_count = 1

        if "@@" in sequence_path.stem:
            real_stem = sequence_path.stem.split("@@")[0]
            real_path = sequence_path.with_name(f"{real_stem}{sequence_path.suffix}")

            cache = getattr(self, "_episode_count_cache", None)
            if cache is None:
                self._episode_count_cache: dict[Path, int] = {}
                cache = self._episode_count_cache

            if real_path in cache:
                episode_count = cache[real_path]
            else:
                try:
                    import pyarrow.parquet as pq

                    table = pq.read_table(real_path, columns=["episode_index"])
                    episode_count = max(1, table.column("episode_index").n_unique())
                except Exception:
                    LOGGER.warning(
                        "Could not count episodes in '%s'; using full file size.",
                        real_path.name,
                    )
                    episode_count = 1
                cache[real_path] = episode_count

        try:
            return real_path.stat().st_size // episode_count
        except OSError:
            LOGGER.exception(
                "Failed to read local size for sequence '%s'; using 0 bytes.",
                sequence_path.name,
            )
            return 0

    def _resolve_remote_size(
        self,
        client: MosaicoClient,
        report: DatasetIngestionReport,
    ) -> int | None:
        """
        Sums the remote size of the ingested sequences contained in one dataset report.

        Returns `None` when at least one remote size lookup fails, so callers can
        distinguish partial reporting failure from a real zero-byte result.
        """
        if report.ingested == 0:
            return 0

        total_remote_size = 0
        for plan in report.ingested_plans:
            try:
                total_remote_size += self._get_remote_sequence_size(
                    client,
                    plan.sequence_name,
                )
            except Exception:
                LOGGER.exception(
                    "Failed to retrieve remote size for sequence '%s'; continuing.",
                    plan.sequence_name,
                )
                report.errors.append(
                    f"Failed to retrieve remote size for '{plan.sequence_name}'."
                )
                return None

        return total_remote_size

    def _get_remote_sequence_size(
        self,
        client: MosaicoClient,
        sequence_name: str,
    ) -> int:
        """
        Computes the remote byte size of one ingested sequence from Flight metadata.

        Args:
            client: Connected Mosaico client used to query Flight metadata.
            sequence_name: Remote sequence name whose topics should be inspected.

        Returns:
            The sum of `total_bytes` across all endpoints in the sequence FlightInfo.

        Raises:
            ValueError: If the endpoint metadata is missing or malformed.
        """
        flight_info, _ = SequenceHandler._get_flight_info(
            client=client._control_client,
            sequence_name=sequence_name,
        )

        total_size_bytes = 0
        for endpoint in flight_info.endpoints:
            endpoint_metadata = _decode_app_metadata(endpoint.app_metadata)
            info_metadata = endpoint_metadata.get("info", {})
            if not isinstance(info_metadata, dict):
                raise ValueError(
                    f"Unexpected endpoint metadata format for '{sequence_name}'."
                )

            endpoint_size = info_metadata.get("total_bytes")
            if endpoint_size is None:
                raise ValueError(
                    f"Missing 'total_bytes' in endpoint metadata for '{sequence_name}'."
                )

            total_size_bytes += int(endpoint_size)

        return total_size_bytes
