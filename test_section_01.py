"""Tests for Section 01: Setup and Configuration.

Validates that the notebook's Cell 3 configuration constants are correct
by extracting and executing the cell source from the .ipynb JSON.
"""
import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Robotics_Industry_Analysis.ipynb')


def load_cell_source(notebook_path, cell_index):
    """Load and return the source code from a notebook cell."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    cell = nb['cells'][cell_index]
    return ''.join(cell['source'])


def test_notebook_structure():
    """Test: Notebook has exactly 8 cells with correct types."""
    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)
    cells = nb['cells']
    assert len(cells) == 9, f"Expected 9 cells, got {len(cells)}"
    assert cells[0]['cell_type'] == 'markdown', "Cell 1 should be markdown"
    for i in range(1, 9):
        assert cells[i]['cell_type'] == 'code', f"Cell {i+1} should be code"


def test_cell2_imports():
    """Test: Cell 2 contains required imports."""
    source = load_cell_source(NOTEBOOK_PATH, 1)
    required = [
        'matplotlib.pyplot',
        'matplotlib.ticker',
        'FuncFormatter',
        'pandas',
        'numpy',
        'os',
        'zipfile',
        'gc',
        'google.colab',
    ]
    for pkg in required:
        assert pkg in source, f"Cell 2 missing import for '{pkg}'"
    assert 'openpyxl' in source, "Cell 2 missing openpyxl install"
    assert 'retina' in source, "Cell 2 missing retina display config"


def test_cell3_configuration():
    """Test: Cell 3 configuration constants are correct."""
    # Extract Cell 3 source and execute it (skip google.colab-dependent lines)
    source = load_cell_source(NOTEBOOK_PATH, 2)
    exec_globals = {}
    exec(source, exec_globals)

    # Year/threshold constants
    assert exec_globals['START_YEAR_DEFAULT'] == 2000
    assert exec_globals['START_YEAR_ALL'] == 1900
    assert exec_globals['ROUND_SIZE_THRESHOLD'] == 100_000_000
    assert exec_globals['TOP_SECTORS_COUNT'] == 7
    assert isinstance(exec_globals['CHART_OUTPUT_DIR'], str) and len(exec_globals['CHART_OUTPUT_DIR']) > 0

    # Paul Tol palette
    palette = exec_globals['PAUL_TOL_PRIMARY']
    assert len(palette) == 7
    assert palette == ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB']

    extended = exec_globals['PAUL_TOL_EXTENDED']
    assert len(extended) == 16
    assert extended[:7] == palette
    assert extended[7:] == [
        '#332288', '#88CCEE', '#44AA99', '#117733',
        '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499'
    ]

    # Region mapping
    regions = exec_globals['SECOND_TIER_REGIONS']
    assert len(regions) == 12

    for region, countries in regions.items():
        assert isinstance(countries, list) and len(countries) > 0, f"Region '{region}' has empty country list"

    # No duplicate countries
    all_countries = []
    for countries in regions.values():
        all_countries.extend(countries)
    assert len(all_countries) == len(set(all_countries)), "Duplicate country found across regions"

    # Post-standardization names
    assert 'United States' in regions['USA']
    assert 'UAE' in regions['Middle East']
    assert 'South Korea' in regions['APAC']

    # Country standardization
    std = exec_globals['COUNTRY_STANDARDIZATION']
    assert std['USA'] == 'United States'
    assert std['United Arab Emirates'] == 'UAE'
    assert std['Republic of Korea'] == 'South Korea'

    # Reverse lookup
    c2r = exec_globals['COUNTRY_TO_REGION']
    assert len(c2r) == len(all_countries), "Reverse lookup count doesn't match total countries"
    assert c2r['United States'] == 'USA'
    assert c2r['UAE'] == 'Middle East'
    assert c2r['South Korea'] == 'APAC'


if __name__ == '__main__':
    tests = [test_notebook_structure, test_cell2_imports, test_cell3_configuration]
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
