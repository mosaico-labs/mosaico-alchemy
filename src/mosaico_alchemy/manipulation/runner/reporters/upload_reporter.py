"""
Console reporting for manipulation runs.

This module turns normalized run reports into human-readable Rich panels and tables.
It keeps presentation concerns separate from the runner so status aggregation remains
testable and reusable outside the terminal UI.
"""

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mosaicopacks.manipulation.runner.reporters.reports import (
    DatasetIngestionReport,
    RunIngestionReport,
)


def _describe_write_mode(write_mode: str) -> str:
    if write_mode == "sync":
        return "sync (default)"
    return "async (shared-client topic threads)"


class UploadReporter:
    """Render high-level run and dataset summaries to the console."""

    def __init__(self, console: Console) -> None:
        """Store the console used for Rich output."""
        self.console = console

    def print_run_header(
        self,
        dataset_roots: list[Path],
        host: str,
        port: int,
        write_mode: str,
    ) -> None:
        """Print the static header that describes the run configuration."""
        body = (
            f"Datasets:     [bold]{len(dataset_roots)}[/bold]\n"
            f"Destination:  [bold]{host}:{port}[/bold]\n"
            f"Write Mode:   [bold]{_describe_write_mode(write_mode)}[/bold]"
        )
        self.console.print(
            Panel(
                body,
                title="[bold]Manipulation Run[/bold]",
                expand=False,
                border_style="blue",
                padding=1,
                highlight=True,
            )
        )

    def print_dataset_summary(self, report: DatasetIngestionReport) -> None:
        """Print the summary panel for one dataset root."""
        size_summary = self._build_size_summary(
            original_size=report.local_size_bytes,
            remote_size=report.remote_size_bytes,
        )
        summary_text = (
            f"Plugin:       [bold]{report.plugin_id}[/bold]\n"
            f"Status:       {self._status_text(report.status)}\n"
            f"Sequences:    [bold]{report.discovered}[/bold] discovered, "
            f"[bold]{report.ingested}[/bold] ingested, "
            f"[bold]{report.skipped}[/bold] skipped, "
            f"[bold]{report.failed}[/bold] failed\n"
            f"{size_summary}\n"
            f"Duration:     [bold]{self._format_duration(report.duration_s)}[/bold]"
        )

        if report.warnings:
            summary_text += (
                f"\nWarnings:     [bold]{len(report.warnings)}[/bold]"
                f" ([dim]{self._truncate_error(report.warnings[-1])}[/dim])"
            )

        if report.errors:
            summary_text += (
                f"\nErrors:       [bold]{len(report.errors)}[/bold]"
                f" ([dim]{self._truncate_error(report.errors[-1])}[/dim])"
            )

        self.console.print(
            Panel(
                summary_text,
                title=(f"[bold]Dataset Summary[/bold] [dim]({report.root})[/dim]"),
                expand=False,
                border_style=self._status_style(report.status),
                padding=1,
                highlight=True,
            )
        )

    def print_run_summary(self, report: RunIngestionReport) -> None:
        """Print the final run summary and a per-dataset breakdown table."""
        size_summary = self._build_size_summary(
            original_size=report.local_size_bytes,
            remote_size=report.remote_size_bytes,
        )
        summary = (
            f"Status:       {self._status_text(report.status)}\n"
            f"Datasets:     [bold]{len(report.datasets)}[/bold]\n"
            f"Sequences:    [bold]{report.discovered}[/bold] discovered, "
            f"[bold]{report.ingested}[/bold] ingested, "
            f"[bold]{report.skipped}[/bold] skipped, "
            f"[bold]{report.failed}[/bold] failed\n"
            f"{size_summary}\n"
            f"Duration:     [bold]{self._format_duration(report.duration_s)}[/bold]"
        )
        self.console.print(
            Panel(
                summary,
                title="[bold]Run Summary[/bold]",
                expand=False,
                border_style=self._status_style(report.status),
                padding=1,
                highlight=True,
            )
        )

        table = Table(show_header=True, header_style="bold")
        table.add_column("#", justify="right")
        table.add_column("Dataset")
        table.add_column("Plugin")
        table.add_column("Status")
        table.add_column("Discovered", justify="right")
        table.add_column("Ingested", justify="right")
        table.add_column("Skipped", justify="right")
        table.add_column("Failed", justify="right")
        table.add_column("Local MB", justify="right")
        table.add_column("Remote MB", justify="right")
        table.add_column("Duration", justify="right")

        for index, dataset_report in enumerate(report.datasets, start=1):
            table.add_row(
                str(index),
                dataset_report.root.name or str(dataset_report.root),
                dataset_report.plugin_id,
                self._plain_status_text(dataset_report.status),
                str(dataset_report.discovered),
                str(dataset_report.ingested),
                str(dataset_report.skipped),
                str(dataset_report.failed),
                f"{self._format_size_mb(dataset_report.local_size_bytes):.2f}",
                self._plain_remote_size(dataset_report.remote_size_bytes),
                self._format_duration(dataset_report.duration_s),
            )

        table.add_section()
        table.add_row(
            "Σ",
            "Totals",
            "-",
            self._plain_status_text(report.status),
            str(report.discovered),
            str(report.ingested),
            str(report.skipped),
            str(report.failed),
            f"{self._format_size_mb(report.local_size_bytes):.2f}",
            self._plain_remote_size(report.remote_size_bytes),
            self._format_duration(report.duration_s),
        )
        self.console.print(table)

    @staticmethod
    def _format_size_mb(size_bytes: int) -> float:
        return size_bytes / (1024 * 1024)

    @staticmethod
    def _format_duration(duration_s: float) -> str:
        total_seconds = max(0, int(duration_s))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def _format_remote_size(self, remote_size: int | None) -> str:
        if remote_size is None:
            return "[dim]unavailable[/dim]"
        return f"[bold]{self._format_size_mb(remote_size):.2f} MB[/bold]"

    def _plain_remote_size(self, remote_size: int | None) -> str:
        if remote_size is None:
            return "-"
        return f"{self._format_size_mb(remote_size):.2f}"

    @staticmethod
    def _truncate_error(error: str, max_length: int = 100) -> str:
        if len(error) <= max_length:
            return error
        return f"{error[: max_length - 3]}..."

    def _build_size_summary(self, original_size: int, remote_size: int | None) -> str:
        if remote_size is None or original_size <= 0 or remote_size <= 0:
            return (
                f"Original Size: [bold]{self._format_size_mb(original_size):.2f} MB[/bold]\n"
                f"Remote Size:   {self._format_remote_size(remote_size)}\n"
                "Ratio:         [dim]unavailable[/dim]\n"
                "Space Saved:   [dim]unavailable[/dim]"
            )

        ratio = original_size / remote_size
        savings = max(0.0, (1 - (remote_size / original_size)) * 100)
        return (
            f"Original Size: [bold]{self._format_size_mb(original_size):.2f} MB[/bold]\n"
            f"Remote Size:   {self._format_remote_size(remote_size)}\n"
            f"Ratio:         [bold cyan]{ratio:.2f}x[/bold cyan]\n"
            f"Space Saved:   [bold green]{savings:.1f}%[/bold green]"
        )

    def _status_text(self, status: str) -> str:
        status_map = {
            "success": "[bold green]success[/bold green]",
            "partial_failure": "[bold yellow]partial_failure[/bold yellow]",
            "failed": "[bold red]failed[/bold red]",
            "skipped": "[bold cyan]skipped[/bold cyan]",
            "interrupted": "[bold yellow]interrupted[/bold yellow]",
        }
        return status_map.get(status, f"[bold]{status}[/bold]")

    @staticmethod
    def _plain_status_text(status: str) -> str:
        return status.replace("_", " ")

    @staticmethod
    def _status_style(status: str) -> str:
        style_map = {
            "success": "green",
            "partial_failure": "yellow",
            "failed": "red",
            "skipped": "cyan",
            "interrupted": "yellow",
        }
        return style_map.get(status, "blue")
