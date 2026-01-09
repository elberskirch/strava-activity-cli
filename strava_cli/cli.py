"""Command-line interface for Strava Activity CLI."""

import json
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from strava_cli.client import StravaClient
from strava_cli.models import Activity

console = Console()


def get_client(token_file: str | None) -> StravaClient:
    """Get authenticated Strava client.

    Args:
        token_file: Optional path to token file

    Returns:
        StravaClient instance
    """
    token_path = Path(token_file) if token_file else None
    try:
        return StravaClient(token_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@click.group()
@click.version_option(version="0.1.0", prog_name="strava")
def main():
    """Strava Activity CLI - Manage your Strava activities from the command line."""
    pass


@main.command()
@click.option(
    "--limit",
    "-l",
    type=int,
    default=10,
    help="Number of activities to retrieve (default: 10)",
)
@click.option(
    "--after",
    "-a",
    type=str,
    help="Only activities after this date (YYYY-MM-DD)",
)
@click.option(
    "--before",
    "-b",
    type=str,
    help="Only activities before this date (YYYY-MM-DD)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--token-file",
    "-t",
    type=str,
    help="Path to token file (default: strava-token.json)",
)
def list(
    limit: int,
    after: str | None,
    before: str | None,
    output_json: bool,
    token_file: str | None,
):
    """List your Strava activities."""
    client = get_client(token_file)

    # Parse dates if provided
    after_date = None
    before_date = None

    if after:
        try:
            after_date = datetime.strptime(after, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format for --after. Use YYYY-MM-DD")
            raise click.Abort()

    if before:
        try:
            before_date = datetime.strptime(before, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Error:[/red] Invalid date format for --before. Use YYYY-MM-DD")
            raise click.Abort()

    # Fetch activities
    try:
        strava_activities = client.get_client().get_activities(
            after=after_date, before=before_date, limit=limit
        )
        activities = [Activity.from_strava_activity(a) for a in strava_activities]
    except Exception as e:
        console.print(f"[red]Error fetching activities:[/red] {e}")
        raise click.Abort()

    if not activities:
        console.print("[yellow]No activities found.[/yellow]")
        return

    if output_json:
        # JSON output
        output = {"activities": [a.to_dict() for a in activities], "count": len(activities)}
        click.echo(json.dumps(output, indent=2))
    else:
        # Table output
        table = Table(title=f"Your Strava Activities (showing {len(activities)})")
        table.add_column("ID", style="cyan")
        table.add_column("Date", style="green")
        table.add_column("Name", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("Distance", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Elevation", justify="right")

        for activity in activities:
            row = activity.format_table_row()
            table.add_row(
                row["ID"],
                row["Date"],
                row["Name"],
                row["Type"],
                row["Distance"],
                row["Time"],
                row["Elevation"],
            )

        console.print(table)


@main.command()
@click.argument("activity_id", type=int)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--token-file",
    "-t",
    type=str,
    help="Path to token file (default: strava-token.json)",
)
def get(activity_id: int, output_json: bool, token_file: str | None):
    """Get details of a specific activity by ID."""
    client = get_client(token_file)

    try:
        strava_activity = client.get_client().get_activity(activity_id)
        activity = Activity.from_strava_activity(strava_activity)
    except Exception as e:
        console.print(f"[red]Error fetching activity {activity_id}:[/red] {e}")
        raise click.Abort()

    if output_json:
        click.echo(json.dumps(activity.to_dict(), indent=2))
    else:
        # Rich formatted output
        console.print(f"\n[bold cyan]Activity: {activity.name}[/bold cyan]")
        console.print(f"[dim]ID: {activity.id}[/dim]\n")

        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="bold")
        info_table.add_column("Value")

        info_table.add_row("Type", activity.type)
        info_table.add_row("Date", activity.start_date_local.strftime("%Y-%m-%d %H:%M:%S"))
        info_table.add_row("Distance", f"{activity.distance / 1000:.2f} km")

        hours = activity.moving_time // 3600
        minutes = (activity.moving_time % 3600) // 60
        seconds = activity.moving_time % 60
        time_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        info_table.add_row("Moving Time", time_str)

        hours = activity.elapsed_time // 3600
        minutes = (activity.elapsed_time % 3600) // 60
        seconds = activity.elapsed_time % 60
        elapsed_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        info_table.add_row("Elapsed Time", elapsed_str)

        info_table.add_row("Elevation Gain", f"{activity.total_elevation_gain:.0f} m")

        if activity.average_speed:
            info_table.add_row("Average Speed", f"{activity.average_speed * 3.6:.2f} km/h")
        if activity.max_speed:
            info_table.add_row("Max Speed", f"{activity.max_speed * 3.6:.2f} km/h")
        if activity.average_heartrate:
            info_table.add_row("Average HR", f"{activity.average_heartrate:.0f} bpm")
        if activity.max_heartrate:
            info_table.add_row("Max HR", f"{activity.max_heartrate:.0f} bpm")
        if activity.calories:
            info_table.add_row("Calories", f"{activity.calories:.0f}")

        info_table.add_row("Trainer", "Yes" if activity.trainer else "No")
        info_table.add_row("Commute", "Yes" if activity.commute else "No")

        if activity.description:
            info_table.add_row("Description", activity.description)

        console.print(info_table)
        console.print()


@main.command()
@click.argument("activity_id", type=int)
@click.option("--name", "-n", type=str, help="Update activity name")
@click.option("--description", "-d", type=str, help="Update activity description")
@click.option("--type", type=str, help="Update activity type (e.g., Run, Ride, Swim)")
@click.option("--commute/--no-commute", default=None, help="Mark as commute or not a commute")
@click.option("--trainer/--no-trainer", default=None, help="Mark as trainer or not trainer")
@click.option("--gear-id", type=str, help="Set gear ID")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output updated activity as JSON",
)
@click.option(
    "--token-file",
    "-t",
    type=str,
    help="Path to token file (default: strava-token.json)",
)
def update(
    activity_id: int,
    name: str | None,
    description: str | None,
    type: str | None,
    commute: bool | None,
    trainer: bool | None,
    gear_id: str | None,
    output_json: bool,
    token_file: str | None,
):
    """Update a specific activity."""
    client = get_client(token_file)

    # Build update dictionary
    updates = {}
    if name:
        updates["name"] = name
    if description is not None:  # Allow empty string to clear description
        updates["description"] = description
    if type:
        updates["type"] = type
    if commute is not None:
        updates["commute"] = commute
    if trainer is not None:
        updates["trainer"] = trainer
    if gear_id:
        updates["gear_id"] = gear_id

    if not updates:
        console.print("[yellow]No updates specified. Use --help to see available options.[/yellow]")
        return

    try:
        # Update activity
        client.get_client().update_activity(activity_id, **updates)

        # Fetch updated activity
        strava_activity = client.get_client().get_activity(activity_id)
        activity = Activity.from_strava_activity(strava_activity)

        if output_json:
            click.echo(json.dumps(activity.to_dict(), indent=2))
        else:
            console.print(f"[green]✓[/green] Activity {activity_id} updated successfully!")
            console.print(f"\n[bold]{activity.name}[/bold]")
            if activity.description:
                console.print(f"[dim]{activity.description}[/dim]")
    except Exception as e:
        console.print(f"[red]Error updating activity {activity_id}:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
