"""Tests for Chart_Summaries.ipynb.

Runs the summary generation pipeline with real local Excel data from
colab/test_data/ and prints the resulting chart_summaries.txt.
Skips when Excel files are absent.
"""
import json
import os
import sys
import shutil

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Chart_Summaries.ipynb')
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')


def load_cell_source(notebook_path, cell_index):
    """Load and return the source code from a notebook cell."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    cell = nb['cells'][cell_index]
    return ''.join(cell['source'])


def get_summary_env():
    """Execute Cells 2-5 with SKIP_TRACXN_UPLOAD=True to load config and helpers."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import pandas as pd
    import numpy as np
    import re
    from datetime import datetime

    env = {
        'plt': plt, 'pd': pd, 'np': np, 'os': os, 'gc': __import__('gc'),
        'FuncFormatter': FuncFormatter, 'zipfile': __import__('zipfile'),
        're': re, 'datetime': datetime,
    }

    # Cell 2 (index 1): config
    exec(load_cell_source(NOTEBOOK_PATH, 2), env)
    # Cell 3 (index 2): data pipeline — skip upload
    env['SKIP_TRACXN_UPLOAD'] = True
    exec(load_cell_source(NOTEBOOK_PATH, 3), env)
    env['SKIP_TRACXN_UPLOAD'] = False
    # Cell 4 (index 3): summary helpers
    exec(load_cell_source(NOTEBOOK_PATH, 4), env)

    return env


def load_local_data(env):
    """Load real Excel files from test_data/ and replicate the Cell 4 pipeline.

    Returns (analysis_df, all_events_df, companies_df) or None if files not found.
    """
    pd = env['pd']
    clean_amount = env['clean_amount']
    extract_year = env['extract_year']
    clean_category = env['clean_category']
    clean_country = env['clean_country']

    # Find Excel files
    companies_path = None
    funding_path = None
    if not os.path.isdir(TEST_DATA_DIR):
        return None

    for fn in os.listdir(TEST_DATA_DIR):
        if not fn.endswith('.xlsx'):
            continue
        lower = fn.lower()
        if 'companies' in lower and 'combined' in lower:
            companies_path = os.path.join(TEST_DATA_DIR, fn)
        elif 'funding' in lower and 'combined' in lower:
            funding_path = os.path.join(TEST_DATA_DIR, fn)

    if companies_path is None or funding_path is None:
        return None

    # Load files
    companies_raw = pd.read_excel(companies_path, engine='openpyxl')
    funding_raw = pd.read_excel(funding_path, engine='openpyxl')

    # Auto-detect: companies file has 'Subcategory' column
    if 'Subcategory' not in companies_raw.columns:
        if 'Subcategory' in funding_raw.columns:
            companies_raw, funding_raw = funding_raw, companies_raw
        else:
            return None

    # Find round amount column
    round_amount_col = None
    for candidate in ['Round Amount (in USD)', 'Round Amount (USD)']:
        if candidate in funding_raw.columns:
            round_amount_col = candidate
            break
    if round_amount_col is None:
        return None

    # Inner join on Domain Name
    merged_df = pd.merge(companies_raw, funding_raw, on='Domain Name', how='inner',
                         suffixes=('_Companies', '_Funding'))

    # Determine column names (may have suffixes from merge)
    cat_col = 'Category_Companies' if 'Category_Companies' in merged_df.columns else 'Category'
    country_col = 'Country_Companies' if 'Country_Companies' in merged_df.columns else 'Country'

    # Apply cleaning
    merged_df['amount_usd'] = merged_df[round_amount_col].apply(clean_amount)
    merged_df['year'] = merged_df['Round Date'].apply(extract_year)
    merged_df['category_clean'] = merged_df[cat_col].apply(clean_category)
    merged_df['country_clean'] = merged_df[country_col].apply(clean_country)
    merged_df['investment_type'] = merged_df['Round Name'].fillna('Unspecified').replace('', 'Unspecified').str.strip()

    # analysis_df: disclosed amounts, valid years
    analysis_df = merged_df[(merged_df['amount_usd'] > 0) & (merged_df['year'].notna())].copy()
    analysis_df['year'] = analysis_df['year'].astype(int)

    # all_events_df: all events with valid years
    all_events_df = merged_df[merged_df['year'].notna()].copy()
    all_events_df['year'] = all_events_df['year'].astype(int)

    # companies_df: deduplicated company records
    companies_df = companies_raw.copy()
    companies_df['founded_year'] = companies_df['Founded Year'].apply(extract_year)
    companies_df = companies_df[companies_df['founded_year'].notna()].copy()
    companies_df['founded_year'] = companies_df['founded_year'].astype(int)
    companies_df = companies_df[(companies_df['founded_year'] >= 1800) & (companies_df['founded_year'] <= 2030)]
    companies_df['category_clean'] = companies_df['Category'].apply(clean_category)
    companies_df['country_clean'] = companies_df['Country'].apply(clean_country)

    return analysis_df, all_events_df, companies_df


def test_summaries_with_local_data():
    """Generate chart summaries using real Excel data and print the output."""
    env = get_summary_env()
    result = load_local_data(env)
    if result is None:
        print("SKIP: Local Excel test data not found in colab/test_data/")
        print("  Expected: *companies*combined*.xlsx and *funding*combined*.xlsx")
        return False

    analysis_df, all_events_df, companies_df = result
    print(f"Loaded real data: {len(analysis_df):,} analysis rows, "
          f"{len(all_events_df):,} events, {len(companies_df):,} companies")

    # Output to test_output/ to avoid clobbering production charts
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_output')
    os.makedirs(output_dir, exist_ok=True)
    env['CHART_OUTPUT_DIR'] = output_dir

    # Inject data
    env['analysis_df'] = analysis_df
    env['all_events_df'] = all_events_df
    env['companies_df'] = companies_df
    env['SKIP_TRACXN_UPLOAD'] = False
    env['SKIP_VC_UPLOAD'] = True

    # Mock files module (not needed but Cell 6 references it for VC upload)
    class MockFiles:
        def upload(self):
            return {}
        def download(self, path):
            pass
    env['files'] = MockFiles()

    # Execute Cell 5 (generation loop)
    cell6_source = load_cell_source(NOTEBOOK_PATH, 5)
    exec(cell6_source, env)

    # Check results
    summaries_generated = env.get('summaries_generated', [])
    summaries_failed = env.get('summaries_failed', [])

    print(f"\nGenerated: {len(summaries_generated)} summaries")
    print(f"Failed: {len(summaries_failed)} summaries")
    if summaries_failed:
        print("Failures:")
        for name, error in summaries_failed:
            print(f"  - {name}: {error}")

    # Print the output file
    output_path = os.path.join(output_dir, 'chart_summaries.txt')
    if os.path.exists(output_path):
        size_kb = os.path.getsize(output_path) / 1024
        print(f"\n{'='*70}")
        print(f"OUTPUT: {output_path} ({size_kb:.1f} KB)")
        print(f"{'='*70}\n")
        with open(output_path) as f:
            print(f.read())
    else:
        print(f"\nERROR: Output file not created: {output_path}")
        return False

    assert len(summaries_failed) == 0, f"Failed: {summaries_failed}"
    assert len(summaries_generated) > 0, "No summaries generated"
    return True


if __name__ == '__main__':
    success = test_summaries_with_local_data()
    sys.exit(0 if success else 1)
