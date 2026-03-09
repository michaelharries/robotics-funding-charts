"""Tests for Section 06: Generation and Export.

Validates the master generation wrapper and ZIP export logic.
Tests use mock data to simulate the full pipeline.
"""
import json
import os
import sys
import zipfile as zf
import glob
import shutil

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Robotics_Industry_Analysis.ipynb')
TEST_OUTPUT_DIR = None


def load_cell_source(notebook_path, cell_index):
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    return ''.join(nb['cells'][cell_index]['source'])


def get_full_env():
    """Execute Cells 3, 5, 6 and prepare mock data for Cell 7 testing."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import pandas as pd
    import numpy as np

    env = {
        'plt': plt, 'pd': pd, 'np': np, 'os': os, 'gc': __import__('gc'),
        'FuncFormatter': FuncFormatter, 'zipfile': __import__('zipfile'),
    }

    # Cell 3: config
    exec(load_cell_source(NOTEBOOK_PATH, 2), env)
    # Cell 5: utilities
    exec(load_cell_source(NOTEBOOK_PATH, 4), env)
    # Cell 6: chart functions
    exec(load_cell_source(NOTEBOOK_PATH, 5), env)

    # Create mock companies_df
    mock_companies = {
        'founded_year': [2000, 2005, 2005, 2010, 2010, 2015, 2015, 2015, 2018, 2020],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'AI',
                           'Robotics', 'AI', 'Logistics', 'Robotics', 'AI'],
        'country_clean': ['United States'] * 5 + ['China'] * 3 + ['Germany'] * 2,
        'Is Deadpooled': ['No'] * 8 + ['Yes', 'No'],
        'Is Acquired': ['No'] * 4 + ['Yes'] + ['No'] * 5,
        'Is IPO': ['No'] * 3 + ['Yes'] + ['No'] * 6,
        'Is Funded': ['Yes'] * 6 + ['No'] * 4,
        'Subcategory': ['Autonomous Vehicles', 'Computer Vision', 'Autonomous Vehicles',
                        'Medical Robotics', 'Computer Vision', 'Autonomous Vehicles',
                        'NLP', 'Warehouse Automation', 'Drones', 'Computer Vision'],
    }
    env['companies_df'] = pd.DataFrame(mock_companies)

    # Create mock analysis_df
    mock_funding = {
        'year': [2000, 2005, 2005, 2010, 2010, 2015, 2015, 2018, 2020, 2020],
        'amount_usd': [5e6, 200e6, 8e6, 500e6, 50e6, 300e6, 2e6, 100e6, 400e6, 10e6],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'AI',
                           'Robotics', 'Logistics', 'Robotics', 'AI', 'Robotics'],
        'country_clean': ['United States'] * 5 + ['China'] * 3 + ['Germany'] * 2,
        'Subcategory': ['Autonomous Vehicles', 'Computer Vision', 'Autonomous Vehicles',
                        'Medical Robotics', 'Computer Vision', 'Autonomous Vehicles',
                        'Warehouse Automation', 'Drones', 'Computer Vision', 'Autonomous Vehicles'],
        'investment_type': ['Seed', 'Series A', 'Seed', 'Series B', 'Series A',
                           'Seed', 'Series A', 'Series B', 'Series A', 'Seed'],
    }
    env['analysis_df'] = pd.DataFrame(mock_funding)

    # Create mock all_events_df (analysis + some undisclosed)
    mock_all = {k: list(v) for k, v in mock_funding.items()}
    mock_all['year'] += [2000, 2010, 2020]
    mock_all['amount_usd'] += [0, 0, 0]
    mock_all['category_clean'] += ['Robotics', 'AI', 'Healthcare']
    mock_all['country_clean'] += ['United States', 'China', 'Germany']
    mock_all['Subcategory'] += ['Autonomous Vehicles', 'Computer Vision', 'Medical Robotics']
    mock_all['investment_type'] += ['Seed', 'Series A', 'Seed']
    env['all_events_df'] = pd.DataFrame(mock_all)

    global TEST_OUTPUT_DIR
    TEST_OUTPUT_DIR = env['CHART_OUTPUT_DIR']

    return env


def test_generation_wrapper():
    """Test: generate_chart wrapper tracks success and handles errors."""
    env = get_full_env()
    import matplotlib.pyplot as plt

    # Override plt.show for non-interactive test
    env['plt'].show = lambda: None

    # Execute Cell 7 (master generation)
    cell7_source = load_cell_source(NOTEBOOK_PATH, 6)
    exec(cell7_source, env)

    charts_generated = env['charts_generated']
    charts_failed = env['charts_failed']

    # Should have generated charts without errors
    assert len(charts_failed) == 0, f"Failed charts: {charts_failed}"
    assert len(charts_generated) > 0, "No charts were generated"

    # Check specific files exist
    expected = [
        'companies_founded_absolute_1900_no_title.png',
        'companies_founded_absolute_all_years_no_title.png',
        'companies_founded_absolute_2000_no_title.png',
        'companies_founded_bar_2000_no_title.png',
        'companies_founded_outcomes_absolute_no_title.png',
        'companies_founded_by_sector_stacked_2000_no_title.png',
        'companies_founded_by_funding_status_stacked_2000_no_title.png',
        'total_global_funding_by_year_2000_no_title.png',
        'robotics_funding_by_year_2000_onwards_no_title.png',
    ]
    for fname in expected:
        path = os.path.join(TEST_OUTPUT_DIR, fname)
        assert os.path.exists(path), f"Missing: {fname}"
        assert os.path.getsize(path) > 0, f"Empty: {fname}"

    plt.close('all')


def test_filename_conventions():
    """Test: all generated filenames follow conventions."""
    env = get_full_env()
    env['plt'].show = lambda: None
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)

    for f in os.listdir(TEST_OUTPUT_DIR):
        if f.endswith('.png'):
            assert f.endswith('_no_title.png'), f"Doesn't end with _no_title.png: {f}"
            assert ' ' not in f, f"Contains space: {f}"
            assert '(' not in f and ')' not in f, f"Contains parentheses: {f}"

    import matplotlib.pyplot as plt
    plt.close('all')


def test_no_open_figures():
    """Test: no matplotlib figures remain open after generation."""
    env = get_full_env()
    env['plt'].show = lambda: None
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)

    import matplotlib.pyplot as plt
    assert len(plt.get_fignums()) == 0, f"Open figures: {plt.get_fignums()}"


def test_zip_export():
    """Test: ZIP file is created with correct structure."""
    env = get_full_env()
    env['plt'].show = lambda: None
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)

    # Create ZIP (Cell 8 logic, minus files.download)
    zip_filename = 'test_robotics_charts.zip'
    zip_count = 0
    with zf.ZipFile(zip_filename, 'w', zf.ZIP_DEFLATED) as z:
        for png_file in sorted(os.listdir(TEST_OUTPUT_DIR)):
            if png_file.endswith('.png'):
                filepath = os.path.join(TEST_OUTPUT_DIR, png_file)
                z.write(filepath, arcname=png_file)
                zip_count += 1

    assert os.path.exists(zip_filename)
    assert os.path.getsize(zip_filename) > 0

    # Check ZIP has same count as directory
    dir_count = len(glob.glob(os.path.join(TEST_OUTPUT_DIR, '*.png')))
    assert zip_count == dir_count, f"ZIP has {zip_count} files but dir has {dir_count}"

    # Check flat structure (no directory prefix)
    with zf.ZipFile(zip_filename, 'r') as z:
        for name in z.namelist():
            assert '/' not in name, f"ZIP entry has directory prefix: {name}"

    os.remove(zip_filename)
    import matplotlib.pyplot as plt
    plt.close('all')


if __name__ == '__main__':
    tests = [
        test_generation_wrapper,
        test_filename_conventions,
        test_no_open_figures,
        test_zip_export,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1

    # Clean up output dir
    if TEST_OUTPUT_DIR and os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
