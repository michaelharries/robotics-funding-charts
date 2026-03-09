"""Tests for Section 03: Shared Utilities.

Validates setup_charts, format_currency_axis, save_figure, get_colors,
sanitize_filename, and complete_year_range functions.
"""
import json
import os
import sys
import shutil

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Robotics_Industry_Analysis.ipynb')


def load_cell_source(notebook_path, cell_index):
    """Load and return the source code from a notebook cell."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    cell = nb['cells'][cell_index]
    return ''.join(cell['source'])


def get_utilities_env():
    """Execute Cells 3 and 5 to get utility functions."""
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

    # Execute Cell 3 (config)
    cell3_source = load_cell_source(NOTEBOOK_PATH, 2)
    exec(cell3_source, env)

    # Execute Cell 5 (utilities)
    cell5_source = load_cell_source(NOTEBOOK_PATH, 4)
    exec(cell5_source, env)

    return env


def test_setup_charts():
    """Test: setup_charts sets rcParams correctly."""
    env = get_utilities_env()
    import matplotlib.pyplot as plt

    env['setup_charts']()
    assert plt.rcParams['font.family'] == ['serif']
    assert plt.rcParams['text.usetex'] == False
    assert plt.rcParams['savefig.dpi'] == 300
    assert plt.rcParams['axes.spines.top'] == False
    assert plt.rcParams['axes.spines.right'] == False
    assert plt.rcParams['axes.grid'] == True


def test_format_currency_axis():
    """Test: format_currency_axis formats values correctly."""
    env = get_utilities_env()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    format_currency_axis = env['format_currency_axis']

    # Test billions scale
    fig, ax = plt.subplots()
    ax.bar([0], [1.5])
    format_currency_axis(ax, axis='y', scale='B')
    formatter = ax.yaxis.get_major_formatter()
    assert '$' in formatter(1.5, 0) and 'B' in formatter(1.5, 0)
    plt.close(fig)

    # Test millions scale
    fig, ax = plt.subplots()
    ax.bar([0], [250])
    format_currency_axis(ax, axis='y', scale='M')
    formatter = ax.yaxis.get_major_formatter()
    assert '$' in formatter(250, 0) and 'M' in formatter(250, 0)
    plt.close(fig)


def test_save_figure():
    """Test: save_figure creates PNG file in output directory."""
    env = get_utilities_env()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    save_figure = env['save_figure']
    output_dir = env['CHART_OUTPUT_DIR']

    # Clean up first
    test_path = os.path.join(output_dir, 'test_chart_no_title.png')
    if os.path.exists(test_path):
        os.remove(test_path)

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    save_figure(fig, 'test_chart')

    assert os.path.exists(test_path), f"File not created at {test_path}"
    assert os.path.getsize(test_path) > 0, "Saved file is empty"
    plt.close(fig)

    # Clean up
    os.remove(test_path)
    if os.path.exists(output_dir) and not os.listdir(output_dir):
        os.rmdir(output_dir)


def test_get_colors():
    """Test: get_colors returns correct palette slices."""
    env = get_utilities_env()
    get_colors = env['get_colors']

    assert len(get_colors(3)) == 3
    assert get_colors(1) == ['#4477AA']
    assert get_colors(7) == ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']
    assert len(get_colors(8)) == 8
    assert len(get_colors(16)) == 16
    assert len(get_colors(20)) == 20  # cycles


def test_sanitize_filename():
    """Test: sanitize_filename produces expected output."""
    env = get_utilities_env()
    sanitize = env['sanitize_filename']

    assert sanitize("Americas (No Canada and USA)") == "Americas_No_Canada_and_USA"
    assert sanitize("Nordics and Baltics") == "Nordics_and_Baltics"
    assert sanitize("Healthcare and Assistive Robotics") == "Healthcare_and_Assistive_Robotics"
    assert sanitize("Food & Beverage") == "Food_and_Beverage"
    assert sanitize("Test/Name") == "Test_Name"
    assert sanitize("Name, Inc.") == "Name_Inc."


def test_complete_year_range():
    """Test: complete_year_range fills gaps with zeros."""
    env = get_utilities_env()
    import pandas as pd

    complete_year_range = env['complete_year_range']

    # Test with Series
    s = pd.Series({2005: 10, 2007: 20, 2010: 30})
    result = complete_year_range(s, start_year=2005, end_year=2010)
    assert len(result) == 6  # 2005-2010
    assert result[2006] == 0  # filled gap
    assert result[2005] == 10  # preserved
    assert result[2007] == 20  # preserved

    # Test with start before data
    result2 = complete_year_range(s, start_year=2000, end_year=2010)
    assert len(result2) == 11  # 2000-2010
    assert result2[2000] == 0
    assert result2[2005] == 10


if __name__ == '__main__':
    tests = [
        test_setup_charts, test_format_currency_axis, test_save_figure,
        test_get_colors, test_sanitize_filename, test_complete_year_range,
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
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
