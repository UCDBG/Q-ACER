# app/api/v1/endpoints/results.py
from __future__ import annotations
import os
import re

from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from typing import List, Optional, Tuple
import pandas as pd

from app.models.schemas import ParsedResults, RunInfo, SatisfiedRow
from concurrent.futures import ThreadPoolExecutor


router = APIRouter()

# ---------- helpers ----------
def _read_original_check(files: List[Path], dataset: str) -> Tuple[Optional[str], Optional[bool]]:
    # tolerate underscores / hyphens and both orders
    pattern = rf"original[_-]?query.*{_escape_dataset(dataset)}|{_escape_dataset(dataset)}.*original[_-]?query"
    p = _match(files, pattern)
    if not p:
        return (None, None)

    df = _read_csv(p)
    if df.empty:
        return (None, None)

    df = _clean_df(df)

    # case-insensitive column lookup
    cols = {str(c).strip().lower(): c for c in df.columns}
    metric_col = cols.get("original metric")
    pass_col   = cols.get("original pass")
    if not metric_col or not pass_col:
        return (None, None)

    last = df.tail(1).iloc[0]
    metric_val = last.get(metric_col)
    pass_val = last.get(pass_col)

    # stringify metric exactly as stored
    metric_str = None if metric_val is None else str(metric_val)
    return (metric_str, (pass_val))

def _first(paths: List[Path]) -> Optional[Path]:
    return sorted(paths)[0] if paths else None

def _read_csv(p: Optional[Path]) -> pd.DataFrame:
    if p and p.exists():
        try:
            # let pandas parse NA normally; we'll normalize blanks below
            # return pd.read_csv(p, engine="python")
            return pd.read_csv(p)
        except Exception:
            pass
    return pd.DataFrame()

def _read_all_csvs(paths: dict) -> dict:
    """Read multiple CSVs concurrently."""
    def read(item):
        key, path = item
        return key, _read_csv(path)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        return dict(executor.map(read, paths.items()))

def _normalize_cell(v):
    """Convert whitespacey/placeholder strings to None; otherwise return trimmed strings or original value."""
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if s in ("", "None", "nan", "NaN", "N/A", "-"):
            return None
        return s  # keep as string; Pydantic will coerce where needed
    return v

def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.rename(columns=lambda c: str(c).strip())
    # normalize every cell
    return df.applymap(_normalize_cell)

def _clean_df_faster(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.rename(columns=lambda c: str(c).strip())
    
    # Vectorized replacement — much faster than applymap per cell
    # Step 1: strip whitespace from all string columns at once
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda col: col.str.strip())
    
    # Step 2: replace placeholder strings with None vectorized
    placeholders = {"", "None", "nan", "NaN", "N/A", "-"}
    df[str_cols] = df[str_cols].apply(
        lambda col: col.where(~col.isin(placeholders), other=None)
    )
    
    return df

def _escape_dataset(ds: str) -> str:
    return re.escape(ds.strip())

def _match(files: List[Path], pattern: str) -> Optional[Path]:
    regex = re.compile(pattern, flags=re.IGNORECASE)
    for p in sorted(files):
        if p.suffix.lower() == ".csv" and regex.search(p.stem):
            return p
    return None

def _match_all(files: List[Path], patterns: dict) -> dict:
    """Scan files once and match all patterns in a single pass."""
    compiled = {key: re.compile(pat, flags=re.IGNORECASE) for key, pat in patterns.items()}
    results = {key: None for key in patterns}
    remaining = set(patterns.keys())

    for p in files:
        if p.suffix.lower() != ".csv":
            continue
        for key in list(remaining):
            if compiled[key].search(p.stem):
                results[key] = p
                remaining.discard(key)
        if not remaining:
            break  # all patterns matched, stop scanning

    return results

def _extract_constraint_bounds(expr: Optional[str]) -> Optional[Tuple[float, float]]:
    if not expr:
        return None
    nums = re.findall(r'-?\d+(?:\.\d+)?', expr)
    if len(nums) < 2:
        return None
    return float(nums[0]), float(nums[-1])

def _constraint_regex_part(expr: Optional[str]) -> Optional[str]:
    bounds = _extract_constraint_bounds(expr)
    if not bounds:
        return None
    lb, ub = bounds
    # filenames look like constraint[1.0, 5.0]
    return rf"\[{lb:.1f},\s*{ub:.1f}\]"

# ---------- endpoint ----------
@router.get("", response_model=ParsedResults)
def get_results(
    dataset: str = Query(..., description="Dataset name to fetch results for"),
    const_num: Optional[int] = Query(None, description="Constraint number to filter results"),
    constraint: Optional[str] = Query(None, description="Constraint expression to filter results")
) -> ParsedResults:
    """
    Read artifacts from an output dir and return structured JSON for the Results page.
    """
    DEFAULT_OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output")).resolve()
    odir = DEFAULT_OUTPUT_DIR
    if not odir.exists():
        raise HTTPException(status_code=404, detail=f"Output dir not found: {odir}")

    # # search recursively (in case future runs write subfolders)
    # files = [p for p in odir.rglob("*") if p.is_file()]
    # no recursive search needed
    files = [p for p in odir.glob("*") if p.is_file()]
    if not files:
        raise HTTPException(status_code=404, detail=f"No files found in: {odir}")

    ds = _escape_dataset(dataset)

    # Extract constraint bounds
    constraint_part = _constraint_regex_part(constraint)
    print(f"Extracted bounds: {constraint_part}")

    ff_pattern = rf"satisfied[_-]?conditions[_-]?fully.*{ds}.*constraint{constraint_part}.*_{const_num}|{ds}.*satisfied[_-]?conditions[_-]?fully.*constraint{constraint_part}.*_{const_num}"
    rp_pattern = rf"satisfied[_-]?conditions[_-]?ranges.*{ds}.*constraint{constraint_part}.*_{const_num}|{ds}.*satisfied[_-]?conditions[_-]?ranges.*constraint{constraint_part}.*_{const_num}"
    run_info_pattern = rf"run[_-]?info.*{ds}.*constraint{constraint_part}.*_{const_num}|{ds}.*run[_-]?info.*constraint{constraint_part}.*_{const_num}"

    csv_files = sorted([p for p in files if p.suffix.lower() == ".csv"])
    # print(f"Files in output dir: {csv_files}")

    run_info_path = _match(files, run_info_pattern)
    ff_path       = _match(files, ff_pattern)
    rp_path       = _match(files, rp_pattern)

    run_info_df = _read_csv(run_info_path)
    ff_df       = _read_csv(ff_path)
    rp_df       = _read_csv(rp_path)

    # # Single pass scan for all patterns at once
    # matched = _match_all(files, {
    #     "run_info": rf"run[_-]?info.*{ds}.*constraint{constraint_part}.*_{const_num}|{ds}.*run[_-]?info.*constraint{constraint_part}.*_{const_num}",
    #     "ff":       rf"satisfied[_-]?conditions[_-]?fully.*{ds}.*constraint{constraint_part}.*_{const_num}",
    #     "rp":       rf"satisfied[_-]?conditions[_-]?ranges.*{ds}.*constraint{constraint_part}.*_{const_num}",
    #     "original": rf"original[_-]?query.*{_escape_dataset(dataset)}|{_escape_dataset(dataset)}.*original[_-]?query",
    # })

    # # Read all CSVs concurrently
    # dfs = _read_all_csvs({
    #     "run_info": matched["run_info"],
    #     "ff":       matched["ff"],
    #     "rp":       matched["rp"],
    #     "original": matched["original"],
    # })

    # run_info_df = dfs["run_info"]
    # ff_df       = dfs["ff"]
    # rp_df       = dfs["rp"]
    # original_df = dfs["original"]

    # --- Clean and coerce run_info into typed models ---
    if not run_info_df.empty:
        run_info_df = _clean_df_faster(run_info_df)
        # Normalize CSV headers to the names expected by RunInfo
        run_info_df = run_info_df.rename(columns={
            "Query No.": "Query Num",
            "Combinations No.": "Combinations Num",
            "Access No.": "Access Num",
            "Checked No.": "Checked Num",
            "Refinement No.": "Refinement Num",
        })
        run_info_records = run_info_df.to_dict(orient="records")
        run_info_rows: List[RunInfo] = [RunInfo(**rec) for rec in run_info_records]
        # print("--- DEBUG: RUN INFO CONTENT START ---")
        # for i, row in enumerate(run_info_rows):
        #     # .model_dump() is the Pydantic v2 way to show data
        #     print(f"Row {i}: {row.model_dump()}") 
        # print("--- DEBUG: RUN INFO CONTENT END ---")
    else:
        run_info_rows = []

    # # Process original query check inline — no separate file read
    # orig_metric, orig_pass = (None, None)
    # if not original_df.empty:
    #     original_df = _clean_df(original_df)
    #     cols = {str(c).strip().lower(): c for c in original_df.columns}
    #     metric_col = cols.get("original metric")
    #     pass_col = cols.get("original pass")
    #     if metric_col and pass_col:
    #         last = original_df.tail(1).iloc[0]
    #         orig_metric = None if last.get(metric_col) is None else str(last.get(metric_col))
    #         orig_pass = last.get(pass_col)

    # satisfied_* tables are passed through as-is (free-form rows)
    ff_rows = ff_df.to_dict(orient="records") if not ff_df.empty else []
    rp_rows = rp_df.to_dict(orient="records") if not rp_df.empty else []

    orig_metric, orig_pass = _read_original_check(files, dataset)

    return ParsedResults(
        output_dir=str(odir),
        run_info=run_info_rows,
        satisfied_conditions_ff=[SatisfiedRow(row=r) for r in ff_rows],
        satisfied_conditions_rp=[SatisfiedRow(row=r) for r in rp_rows],
        raw_files=[str(p) for p in files],
        original_metric=orig_metric,
        original_pass=orig_pass,
    )

