"""Tests for Section 04: Companies Charts.

Validates the 5 companies-founded chart functions using mock data.
"""
import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Robotics_Industry_Analysis.ipynb')
TEST_OUTPUT_DIR = None  # Set after loading config


def load_cell_source(notebook_path, cell_index):
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    return ''.join(nb['cells'][cell_index]['source'])


def get_chart_env():
    """Execute Cells 3, 5, and 6 to get chart functions with mock data."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import pandas as pd
    import numpy as np

    env = {
        'plt': plt, 'pd': pd, 'np': np, 'os': os,
        'FuncFormatter': FuncFormatter,
    }

    # Cell 3: config
    exec(load_cell_source(NOTEBOOK_PATH, 2), env)

    # Cell 5: utilities
    exec(load_cell_source(NOTEBOOK_PATH, 4), env)

    # Cell 6: chart functions
    exec(load_cell_source(NOTEBOOK_PATH, 5), env)

    # Create mock companies_df
    mock_data = {
        'founded_year': [2000, 2001, 2002, 2003, 2005, 2005, 2005, 2010, 2010, 2015,
                         2015, 2015, 2015, 2018, 2018, 2020, 2020, 2020, 2020, 2020],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'Robotics', 'AI', 'Logistics',
                           'Robotics', 'AI', 'Robotics', 'AI', 'Healthcare', 'Logistics',
                           'Robotics', 'AI', 'Robotics', 'AI', 'Healthcare', 'Logistics', 'Drones'],
        'country_clean': ['United States'] * 10 + ['China'] * 5 + ['Germany'] * 5,
        'Is Deadpooled': ['No'] * 15 + ['Yes', 'No', 'No', 'No', 'No'],
        'Is Acquired': ['No'] * 10 + ['Yes', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No', 'No'],
        'Is IPO': ['No'] * 5 + ['Yes', 'No', 'No', 'No', 'No'] + ['No'] * 10,
        'Is Funded': ['Yes'] * 12 + ['No'] * 8,
        'Subcategory': ['Sub1'] * 20,
    }
    env['mock_companies_df'] = pd.DataFrame(mock_data)

    global TEST_OUTPUT_DIR
    TEST_OUTPUT_DIR = env['CHART_OUTPUT_DIR']

    return env


def cleanup_test_files(*filenames):
    """Remove test chart files."""
    for fn in filenames:
        path = os.path.join(TEST_OUTPUT_DIR, f'{fn}_no_title.png')
        if os.path.exists(path):
            os.remove(path)


def test_line_chart():
    """Test: create_companies_founded_line_chart returns valid figure."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_line_chart'](env['mock_companies_df'], 2000, 'test_line')
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1

    line = fig.axes[0].get_lines()[0]
    assert line.get_marker() == 'o'

    path = os.path.join(TEST_OUTPUT_DIR, 'test_line_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_line')


def test_bar_chart():
    """Test: create_companies_founded_bar_chart returns valid figure."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_bar_chart'](env['mock_companies_df'], 2000, 'test_bar')
    assert isinstance(fig, plt.Figure)
    patches = fig.axes[0].patches
    assert len(patches) > 0

    path = os.path.join(TEST_OUTPUT_DIR, 'test_bar_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_bar')


def test_outcomes_chart():
    """Test: create_companies_founded_outcomes_chart has correct legend and text inset."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_outcomes_chart'](env['mock_companies_df'], 2000, 'test_outcomes')
    assert isinstance(fig, plt.Figure)

    legend = fig.axes[0].get_legend()
    labels = [t.get_text() for t in legend.get_texts()]
    assert set(labels) == {'Active/Unknown', 'Failed', 'Acquired', 'IPO'}

    # Verify summary statistics text inset exists
    ax = fig.axes[0]
    text_objects = [t for t in ax.texts if 'Total Companies' in t.get_text()]
    assert len(text_objects) == 1, "Missing summary statistics text inset"
    stats_text = text_objects[0].get_text()
    assert 'Active/Unknown' in stats_text
    assert 'Failed' in stats_text
    assert 'Acquired' in stats_text
    assert 'IPO' in stats_text
    assert '%' in stats_text  # Should have percentages

    path = os.path.join(TEST_OUTPUT_DIR, 'test_outcomes_no_title.png')
    assert os.path.exists(path)
    plt.close(fig)
    cleanup_test_files('test_outcomes')


def test_sector_chart():
    """Test: create_companies_founded_by_sector_chart has correct legend count."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_by_sector_chart'](env['mock_companies_df'], 2000, 'test_sector')
    assert isinstance(fig, plt.Figure)

    legend = fig.axes[0].get_legend()
    assert len(legend.get_texts()) <= 8  # top 7 + Other

    path = os.path.join(TEST_OUTPUT_DIR, 'test_sector_no_title.png')
    assert os.path.exists(path)
    plt.close(fig)
    cleanup_test_files('test_sector')


def test_funding_status_chart():
    """Test: create_companies_founded_by_funding_status_chart has Funded/Not Funded."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_by_funding_status_chart'](env['mock_companies_df'], 2000, 'test_funding_status')
    assert isinstance(fig, plt.Figure)

    legend = fig.axes[0].get_legend()
    labels = [t.get_text() for t in legend.get_texts()]
    assert 'Funded' in labels and 'Not Funded' in labels

    path = os.path.join(TEST_OUTPUT_DIR, 'test_funding_status_no_title.png')
    assert os.path.exists(path)
    plt.close(fig)
    cleanup_test_files('test_funding_status')


if __name__ == '__main__':
    tests = [test_line_chart, test_bar_chart, test_outcomes_chart,
             test_sector_chart, test_funding_status_chart]
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
    print(f"\n{passed} passed, {failed} failed")
    # Clean up output dir if empty
    if TEST_OUTPUT_DIR and os.path.exists(TEST_OUTPUT_DIR) and not os.listdir(TEST_OUTPUT_DIR):
        os.rmdir(TEST_OUTPUT_DIR)
    sys.exit(1 if failed else 0)
