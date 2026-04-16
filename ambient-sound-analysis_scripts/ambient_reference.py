"""
Compute rolling 7-day broadband reference levels (5th percentile)
for all Orcasound hydrophones and write results to S3.

Uses the most recent 604,800 data points (7 days at 1-second resolution)
ending at "now", looking back up to 14 calendar days to find enough data.
Stores the result under tomorrow's date so the PSD pipeline always has a
ref value available for any day it runs.

Produces per-hydrophone ref files matching the schema expected by
the pipeline: date, bb_ref, comm_bb_ref, ship_bb_ref.
"""

import datetime as dt
import io
import traceback
from dataclasses import asdict, dataclass
from zoneinfo import ZoneInfo

import boto3
import polars as pl

from orcasound_noise.analysis.partitioned_accessor import PartitionedAccessor
from orcasound_noise.utils import Hydrophone

WINDOW_DAYS = 7
TARGET_ROWS = WINDOW_DAYS * 24 * 60 * 60  # 604,800 seconds of data
MIN_ROWS = TARGET_ROWS  # require a full 7 days of data
MAX_LOOKBACK_DAYS = 14
TIMEZONE = ZoneInfo("US/Pacific")

# data_3.0 broadband columns
BB_COL = "bb_o"
COMM_BB_COL = "comm_bb_o"
SHIP_BB_COL = "ship_bb_o"
TIMESTAMP_COL = "ind"


@dataclass
class ReferenceRow:
    date: dt.date
    bb_ref: float
    comm_bb_ref: float
    ship_bb_ref: float


def s3_ref_key(hydrophone: Hydrophone) -> str:
    """S3 key matching the path the pipeline reads refs from."""
    name = hydrophone.value.name
    save_folder = hydrophone.value.save_folder
    return f"{save_folder}/ref/hydrophone={name}/{name}_ref.parquet"


def read_existing(s3_client, hydrophone: Hydrophone) -> pl.DataFrame | None:
    """Read existing reference parquet from S3, or return None."""
    bucket = hydrophone.value.save_bucket
    key = s3_ref_key(hydrophone)
    try:
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        data = obj["Body"].read()
        return pl.read_parquet(io.BytesIO(data))
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"  Warning: could not read existing data for {hydrophone.name}: {e}")
        return None


def write_to_s3(s3_client, hydrophone: Hydrophone, df: pl.DataFrame) -> None:
    """Write reference parquet to S3."""
    bucket = hydrophone.value.save_bucket
    key = s3_ref_key(hydrophone)
    buf = io.BytesIO()
    df.write_parquet(buf)
    s3_client.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())
    print(f"  Wrote {len(df)} rows to s3://{bucket}/{key}")



def load_broadband(hydrophone: Hydrophone, start: dt.datetime, end: dt.datetime) -> pl.DataFrame | None:
    """Load broadband data for a hydrophone over a date range using PartitionedAccessor."""
    try:
        accessor = PartitionedAccessor(hydrophone, start, end)
        _, lf_bb = accessor.get_dataframes(lazy=True)
        return lf_bb.collect()
    except Exception as e:
        print(f"  Warning: failed to load broadband data: {e}")
        return None


def compute_reference(
    hydrophone: Hydrophone, now: dt.datetime, ref_date: dt.date
) -> ReferenceRow | None:
    """Compute 5th percentile over the most recent TARGET_ROWS data points.

    Loads broadband data for the past MAX_LOOKBACK_DAYS, takes the most recent
    TARGET_ROWS rows, and computes the 5th percentile.
    """
    name = hydrophone.value.name

    # Strip timezone — parquet ind column is naive datetime[ns]
    now_naive = now.replace(tzinfo=None)
    start_time = now_naive - dt.timedelta(days=MAX_LOOKBACK_DAYS)

    bb_df = load_broadband(hydrophone, start_time, now_naive)
    if bb_df is None or bb_df.height == 0:
        return None

    # Take only the most recent TARGET_ROWS
    bb_df = bb_df.sort(TIMESTAMP_COL, descending=True).head(TARGET_ROWS)

    if bb_df.height < MIN_ROWS:
        print(
            f"  Skipping {name}: only {bb_df.height} rows found "
            f"(need at least {MIN_ROWS}) — not enough data for a reliable reference"
        )
        return None

    if bb_df.height < TARGET_ROWS:
        print(
            f"  WARNING: only {bb_df.height}/{TARGET_ROWS} rows found after "
            f"{MAX_LOOKBACK_DAYS}d lookback for {name} — using available data"
        )
    else:
        print(f"  Collected {bb_df.height} rows")

    quantiles = bb_df.select(
        pl.col(BB_COL).quantile(0.05).alias("bb_ref"),
        pl.col(COMM_BB_COL).quantile(0.05).alias("comm_bb_ref"),
        pl.col(SHIP_BB_COL).quantile(0.05).alias("ship_bb_ref"),
    ).row(0)
    return ReferenceRow(
        date=ref_date,
        bb_ref=float(quantiles[0]),
        comm_bb_ref=float(quantiles[1]),
        ship_bb_ref=float(quantiles[2]),
    )


def process_hydrophone(
    s3_client, hydrophone: Hydrophone, now: dt.datetime, tomorrow: dt.date
) -> int:
    """Process a single hydrophone. Computes one ref row for tomorrow. Returns 1 on success, 0 otherwise."""
    name = hydrophone.name
    print(f"\nProcessing {name}...")

    existing_df = read_existing(s3_client, hydrophone)

    # Keep all rows except tomorrow (we'll recompute it)
    if existing_df is not None and len(existing_df) > 0:
        existing_df = existing_df.filter(pl.col("date") != tomorrow)
        print(f"  Existing ref has {len(existing_df)} rows (excluding tomorrow)")
    else:
        existing_df = None
        print("  No existing ref data found")

    row = compute_reference(hydrophone, now, tomorrow)
    if row is None:
        print(f"  No data found for {name}, skipping")
        return 0
    print(f"  {tomorrow}: bb={row.bb_ref:.1f} comm={row.comm_bb_ref:.1f} "
          f"ship={row.ship_bb_ref:.1f} dB")

    new_df = pl.DataFrame([asdict(row)]).with_columns(
        pl.col("date").cast(pl.Date),
    )

    if existing_df is not None and len(existing_df) > 0:
        combined = pl.concat([existing_df, new_df])
    else:
        combined = new_df

    write_to_s3(s3_client, hydrophone, combined)
    return 1


def main():
    print("=" * 60)
    print("Rolling Broadband Reference Level Computation")
    print("=" * 60)

    s3_client = boto3.client("s3")
    now = dt.datetime.now(TIMEZONE)
    tomorrow = (now + dt.timedelta(days=1)).date()
    print(f"Now: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Computing ref for: {tomorrow}")

    summary = {}
    for hydrophone in Hydrophone:
        if hydrophone.name == "HPhoneTup":
            continue
        try:
            count = process_hydrophone(s3_client, hydrophone, now, tomorrow)
            summary[hydrophone.name] = count
        except Exception:
            print(f"\nERROR processing {hydrophone.name}:")
            traceback.print_exc()
            summary[hydrophone.name] = None

    print("\n" + "=" * 60)
    print("Summary:")
    for name, result in summary.items():
        if result is None:
            print(f"  {name}: FAILED")
        else:
            print(f"  {name}: {result} new rows")
    print("=" * 60)


if __name__ == "__main__":
    main()
