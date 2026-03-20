"""Generate all 19 missing charts locally using real test data."""
import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Missing_Charts_Analysis.ipynb')
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')

COMPANIES_FILE = os.path.join(TEST_DATA_DIR,
    '20260222 - classified_companies_combined only to end 2025.xlsx')
FUNDING_FILE = os.path.join(TEST_DATA_DIR,
    '20260222 - funding_rounds_combined - to end 2025.xlsx')
VC_CSV_FILE = os.path.join(TEST_DATA_DIR, 'global_vc_totals_2000_to_2025.csv')


def load_cell_source(notebook_path, cell_index):
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    return ''.join(nb['cells'][cell_index]['source'])


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import pandas as pd
    import numpy as np
    import gc
    import zipfile

    # Check test data exists
    for path, label in [(COMPANIES_FILE, 'Companies'), (FUNDING_FILE, 'Funding'), (VC_CSV_FILE, 'VC CSV')]:
        if not os.path.exists(path):
            print(f"ERROR: {label} file not found: {path}")
            sys.exit(1)

    env = {
        'plt': plt, 'pd': pd, 'np': np, 'os': os,
        'FuncFormatter': FuncFormatter, 'gc': gc, 'zipfile': zipfile,
    }

    # Cell 3: Configuration
    print("Loading configuration...")
    exec(load_cell_source(NOTEBOOK_PATH, 2), env)

    # Cell 5: Utilities
    print("Loading utilities...")
    exec(load_cell_source(NOTEBOOK_PATH, 4), env)

    # Cell 6: Chart functions
    print("Loading chart functions...")
    exec(load_cell_source(NOTEBOOK_PATH, 5), env)

    # --- Load real data (bypass Colab upload) ---
    print(f"\nLoading companies: {os.path.basename(COMPANIES_FILE)}")
    companies_raw = pd.read_excel(COMPANIES_FILE, engine='openpyxl')
    print(f"  {companies_raw.shape[0]:,} rows, {companies_raw.shape[1]} columns")

    print(f"Loading funding: {os.path.basename(FUNDING_FILE)}")
    funding_raw = pd.read_excel(FUNDING_FILE, engine='openpyxl')
    print(f"  {funding_raw.shape[0]:,} rows, {funding_raw.shape[1]} columns")

    # --- Run cleaning pipeline from Cell 4 (inline, not exec) ---
    import re
    from datetime import datetime

    COUNTRY_STANDARDIZATION = env['COUNTRY_STANDARDIZATION']

    def clean_amount(amount):
        if pd.isna(amount) or amount is None:
            return 0.0
        if isinstance(amount, (int, float)):
            return float(amount)
        if isinstance(amount, str):
            amount = amount.replace(',', '').replace('$', '').replace(' ', '')
            if amount == '':
                return 0.0
            try:
                return float(amount)
            except ValueError:
                return 0.0
        return 0.0

    def extract_year(date_str):
        if pd.isna(date_str) or date_str is None:
            return None
        date_str = str(date_str).strip()
        if date_str == '' or date_str.lower() == 'none':
            return None
        if len(date_str) == 4 and date_str.isdigit():
            year = int(date_str)
            return year if 1800 <= year <= 2030 else None
        if ',' in date_str:
            try:
                year = datetime.strptime(date_str.strip(), '%b %d, %Y').year
                return year if 1800 <= year <= 2030 else None
            except (ValueError, TypeError):
                pass
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %Y', '%B %Y']:
            try:
                year = datetime.strptime(date_str, fmt).year
                return year if 1800 <= year <= 2030 else None
            except ValueError:
                continue
        match = re.search(r'\b(18|19|20)\d{2}\b', date_str)
        if match:
            year = int(match.group())
            return year if 1800 <= year <= 2030 else None
        return None

    def clean_category(category):
        if pd.isna(category) or category is None:
            return 'Unknown'
        category = str(category).strip()
        if category == '':
            return 'Unknown'
        if ',' in category:
            category = category.split(',')[0].strip()
        return category

    def clean_country(country):
        if pd.isna(country) or country is None:
            return 'Unknown'
        country = str(country).strip()
        if country == '':
            return 'Unknown'
        if ',' in country:
            country = country.split(',')[0].strip()
        return COUNTRY_STANDARDIZATION.get(country, country)

    # Detect round amount column
    ROUND_AMOUNT_COL = None
    for candidate in ['Round Amount (in USD)', 'Round Amount (USD)']:
        if candidate in funding_raw.columns:
            ROUND_AMOUNT_COL = candidate
            break
    assert ROUND_AMOUNT_COL is not None, \
        f"Funding file missing amount column. Columns: {list(funding_raw.columns)}"
    print(f"Using round amount column: '{ROUND_AMOUNT_COL}'")

    # Inner join
    merged_df = pd.merge(companies_raw, funding_raw, on='Domain Name', how='inner',
                         suffixes=('_Companies', '_Funding'))
    print(f"Merged: {merged_df.shape[0]:,} rows")

    # Clean columns
    cat_col = 'Category_Companies' if 'Category_Companies' in merged_df.columns else 'Category'
    country_col = 'Country_Companies' if 'Country_Companies' in merged_df.columns else 'Country'

    merged_df['amount_usd'] = merged_df[ROUND_AMOUNT_COL].apply(clean_amount)
    merged_df['year'] = merged_df['Round Date'].apply(extract_year)
    merged_df['category_clean'] = merged_df[cat_col].apply(clean_category)
    merged_df['country_clean'] = merged_df[country_col].apply(clean_country)

    # Filter DataFrames
    analysis_df = merged_df[(merged_df['amount_usd'] > 0) & (merged_df['year'].notna())].copy()
    analysis_df['year'] = analysis_df['year'].astype(int)

    all_events_df = merged_df[merged_df['year'].notna()].copy()
    all_events_df['year'] = all_events_df['year'].astype(int)

    companies_df = companies_raw.copy()
    companies_df['founded_year'] = companies_df['Founded Year'].apply(extract_year)
    companies_df = companies_df[companies_df['founded_year'].notna()].copy()
    companies_df['founded_year'] = companies_df['founded_year'].astype(int)
    companies_df = companies_df[(companies_df['founded_year'] >= 1800) & (companies_df['founded_year'] <= 2030)]
    companies_df['category_clean'] = companies_df['Category'].apply(clean_category)
    companies_df['country_clean'] = companies_df['Country'].apply(clean_country)

    print(f"\nanalysis_df:   {analysis_df.shape[0]:,} rows")
    print(f"all_events_df: {all_events_df.shape[0]:,} rows")
    print(f"companies_df:  {companies_df.shape[0]:,} rows")

    # --- Inject data into env and run generation ---
    env['SKIP_TRACXN_UPLOAD'] = False
    env['SKIP_VC_UPLOAD'] = True  # We'll handle VC separately
    env['analysis_df'] = analysis_df
    env['all_events_df'] = all_events_df
    env['companies_df'] = companies_df

    print(f"\n{'='*60}")
    print("Generating 18 Tracxn-based charts...")
    print(f"{'='*60}\n")

    # Inject 're' module needed by employee count parsing
    import re as _re
    env['re'] = _re

    # Execute Cell 7 (master generation)
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)

    # --- Global VC chart ---
    print(f"\nGenerating global VC chart from CSV...")
    vc_df = pd.read_csv(VC_CSV_FILE)
    generate_chart = env['generate_chart']
    create_global_vc_funding_chart = env['create_global_vc_funding_chart']
    generate_chart('global_vc_totals',
        create_global_vc_funding_chart, vc_df, 2000, 'global_vc_totals')
    plt.close('all')

    # Write .txt description for VC chart
    vc_txt = os.path.join(env['CHART_OUTPUT_DIR'], 'global_vc_totals_no_title.txt')
    with open(vc_txt, 'w') as f:
        f.write('Global VC investment by year (2000+) from external summary CSV. Not derived from Tracxn company/funding data.\nOriginal: missing/Economic Plots/StateofMarket/007 global_vc_totals_2000_to_2024.png\n')

    # --- Final summary ---
    output_dir = env['CHART_OUTPUT_DIR']
    if os.path.exists(output_dir):
        pngs = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
        # Filter to only our 19 charts
        expected = [
            'global_fa_yearly', 'americas_fa_yearly', 'asia_pacific_fa_yearly', 'europe_africa_fa_yearly',
            'global_fe_yearly', 'americas_fe_yearly', 'asia_pacific_fe_yearly', 'europe_africa_fe_yearly',
            'global_companies_founded_by_year', 'americas_companies_founded_by_year', 'usa_companies_founded_by_year',
            'asia_pacific_companies_by_year_funded', 'europe_africa_companies_by_year_funded',
            'regional_deadpooled_percentage', 'regional_funded_percentage',
            'regional_funded_companies_pie',
            'top10_stage_SeedA', 'top10_total_employee_count',
            'global_vc_totals',
        ]
        our_pngs = [f for f in pngs if any(f.startswith(e + '_no_title') for e in expected)]
        print(f"\n{'='*60}")
        print(f"ALL DONE — {len(our_pngs)} of 19 missing charts generated")
        print(f"{'='*60}")
        print(f"Output directory: {os.path.abspath(output_dir)}/")
        print()
        for f in our_pngs:
            size_kb = os.path.getsize(os.path.join(output_dir, f)) / 1024
            print(f"  {f}  ({size_kb:.0f} KB)")


if __name__ == '__main__':
    main()
