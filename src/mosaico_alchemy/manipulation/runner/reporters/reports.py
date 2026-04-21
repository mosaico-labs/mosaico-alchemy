"""
Reporting models for dataset and run ingestion.

These dataclasses capture the stable summary produced by the runner. They keep the
execution path decoupled from presentation so console output and future integrations
can reason about the same normalized ingestion outcome.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from mosaicopacks.manipulation.contracts import IngestionDescriptor

SequenceResultStatus = Literal["ingested", "skipped", "failed", "interrupted"]
DatasetReportStatus = Literal[
    "success",
    "partial_failure",
    "failed",
    "skipped",
    "interrupted",
]
RunReportStatus = Literal["success", "partial_failure", "interrupted"]


@dataclass
class SequenceIngestionResult:
    """Outcome of ingesting a single sequence.

    Attributes:
        sequence_name: Backend-visible sequence name.
        status: Final state for the sequence within the current run.
        local_size_bytes: Size of the source data that contributed to the sequence.
        backend: Backend path used to ingest the sequence, such as `files` or `rosbag`.
        plan: Ingestion plan that produced the sequence when ingestion succeeded.
        error: Human-readable failure or skip reason, when available.
    """

    sequence_name: str
    status: SequenceResultStatus
    local_size_bytes: int = 0
    backend: str | None = None
    plan: IngestionDescriptor | None = None
    error: str | None = None


@dataclass
class DatasetIngestionReport:
    """Aggregated result for one dataset root handled by a plugin.

    The report accumulates sequence-level outcomes and is finalized only after the
    runner has finished discovery, upload, and remote size inspection for the root.

    Attributes:
        root: Dataset root that was processed.
        plugin_id: Plugin responsible for the root.
        status: Final dataset status after aggregation.
        discovered: Number of sequences discovered before filtering.
        ingested: Number of sequences uploaded successfully.
        skipped: Number of sequences skipped intentionally.
        failed: Number of sequences that failed during processing.
        local_size_bytes: Sum of local source sizes for processed sequences.
        remote_size_bytes: Aggregate remote size when available from the backend.
        duration_s: Total processing time for the dataset root.
        errors: Collected dataset and sequence errors.
        warnings: Collected non-fatal warnings.
        ingested_plans: Plans that completed successfully and can be inspected later.
    """

    root: Path
    plugin_id: str
    status: DatasetReportStatus = "success"
    discovered: int = 0
    ingested: int = 0
    skipped: int = 0
    failed: int = 0
    local_size_bytes: int = 0
    remote_size_bytes: int | None = None
    duration_s: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ingested_plans: list[IngestionDescriptor] = field(default_factory=list)

    @classmethod
    def failed_report(
        cls,
        root: Path,
        error: str,
        plugin_id: str = "unresolved",
        duration_s: float = 0.0,
    ) -> "DatasetIngestionReport":
        """Build a report for a dataset root that failed before sequence ingestion."""
        report = cls(
            root=root,
            plugin_id=plugin_id,
            status="failed",
            duration_s=duration_s,
        )
        report.errors.append(error)
        return report

    @classmethod
    def skipped_report(
        cls,
        root: Path,
        warning: str,
        plugin_id: str = "none",
        duration_s: float = 0.0,
    ) -> "DatasetIngestionReport":
        """Build a report for a dataset root that was intentionally skipped."""
        report = cls(
            root=root,
            plugin_id=plugin_id,
            status="skipped",
            duration_s=duration_s,
        )
        report.warnings.append(warning)
        return report

    @classmethod
    def interrupted_report(
        cls,
        root: Path,
        error: str = "Interrupted by user.",
        plugin_id: str = "unresolved",
        duration_s: float = 0.0,
    ) -> "DatasetIngestionReport":
        """Build a report for a dataset root interrupted before completion."""
        report = cls(
            root=root,
            plugin_id=plugin_id,
            status="interrupted",
            duration_s=duration_s,
        )
        report.errors.append(error)
        return report

    def record_sequence(self, result: SequenceIngestionResult) -> None:
        """Fold a sequence-level outcome into the dataset totals."""
        self.local_size_bytes += result.local_size_bytes

        if result.status == "ingested":
            self.ingested += 1
            if result.plan is not None:
                self.ingested_plans.append(result.plan)
        elif result.status == "skipped":
            self.skipped += 1
        elif result.status == "failed":
            self.failed += 1

        if result.error:
            self.errors.append(result.error)

    def finalize(self, interrupted: bool = False) -> None:
        """Derive the final dataset status from the accumulated counters."""
        if interrupted or self.status == "interrupted":
            self.status = "interrupted"
            return

        if self.status == "skipped":
            return

        if self.status == "failed" and self.failed == 0:
            return

        if self.failed > 0:
            self.status = (
                "partial_failure"
                if (self.ingested > 0 or self.skipped > 0)
                else "failed"
            )
            return

        self.status = "success"


@dataclass
class RunIngestionReport:
    """Top-level summary for an entire manipulation run.

    Attributes:
        datasets: Dataset reports produced during the run.
        duration_s: Total wall-clock duration for the run.
        status: Final run status derived from dataset outcomes.
    """

    datasets: list[DatasetIngestionReport] = field(default_factory=list)
    duration_s: float = 0.0
    status: RunReportStatus = "success"

    @classmethod
    def from_dataset_reports(
        cls,
        dataset_reports: list[DatasetIngestionReport],
        duration_s: float,
        interrupted: bool = False,
    ) -> "RunIngestionReport":
        """Build the run summary by collapsing the statuses of all dataset reports."""
        if interrupted or any(
            report.status == "interrupted" for report in dataset_reports
        ):
            status: RunReportStatus = "interrupted"
        elif any(
            report.status in {"failed", "partial_failure"} for report in dataset_reports
        ):
            status = "partial_failure"
        else:
            status = "success"

        return cls(datasets=dataset_reports, duration_s=duration_s, status=status)

    @property
    def discovered(self) -> int:
        """Return the total number of discovered sequences across all datasets."""
        return sum(report.discovered for report in self.datasets)

    @property
    def ingested(self) -> int:
        """Return the total number of successfully ingested sequences."""
        return sum(report.ingested for report in self.datasets)

    @property
    def skipped(self) -> int:
        """Return the total number of skipped sequences across the run."""
        return sum(report.skipped for report in self.datasets)

    @property
    def failed(self) -> int:
        """Return the total number of failed sequences across the run."""
        return sum(report.failed for report in self.datasets)

    @property
    def local_size_bytes(self) -> int:
        """Return the aggregate source size contributed by all dataset reports."""
        return sum(report.local_size_bytes for report in self.datasets)

    @property
    def remote_size_bytes(self) -> int | None:
        """Return the aggregate remote size when every dataset exposes it."""
        remote_sizes = [report.remote_size_bytes for report in self.datasets]
        if any(size is None for size in remote_sizes):
            return None
        return sum(size or 0 for size in remote_sizes)
