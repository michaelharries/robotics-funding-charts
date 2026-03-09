"""Tests for Section 02: Data Pipeline.

Validates cleaning functions and data pipeline logic by extracting
Cell 4 source from the notebook and running it in a mock environment.
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


def get_cleaning_functions():
    """Execute Cell 3 (config) and Cell 4 (pipeline) to get cleaning functions.

    Skips google.colab and files.upload() lines so tests run locally.
    Returns the exec'd globals namespace.
    """
    # Execute Cell 3 first (config constants)
    cell3_source = load_cell_source(NOTEBOOK_PATH, 2)
    env = {}
    exec(cell3_source, env)

    # Execute Cell 4, skipping Colab-specific lines
    cell4_source = load_cell_source(NOTEBOOK_PATH, 3)
    lines = cell4_source.split('\n')
    filtered_lines = []
    skip_block = False
    for line in lines:
        # Skip google.colab upload calls and the upload-dependent block
        if 'files.upload()' in line:
            skip_block = True
            continue
        if 'pd.read_excel' in line and 'uploaded' in line:
            continue
        if skip_block and line.strip() == '':
            skip_block = False
            continue
        if skip_block:
            continue
        # Skip lines that reference uploaded/filenames from upload block
        if 'filenames = list(uploaded' in line:
            continue
        filtered_lines.append(line)

    # Only execute the function definitions, not the full pipeline
    func_source = []
    in_func = False
    for line in filtered_lines:
        stripped = line.strip()
        if stripped.startswith('def '):
            in_func = True
        if in_func:
            func_source.append(line)
            if stripped == '' or (not stripped.startswith(' ') and not stripped.startswith('def ') and stripped != ''):
                if not stripped.startswith('def '):
                    in_func = False

    # Execute just the function definitions in the config environment
    import pandas as pd
    import numpy as np
    import re
    from datetime import datetime
    env['pd'] = pd
    env['np'] = np
    env['re'] = re
    env['datetime'] = datetime

    # Extract all function defs from the cell source
    exec_source = extract_function_defs(cell4_source)
    exec(exec_source, env)

    return env


def extract_function_defs(source):
    """Extract all function definitions from source code."""
    lines = source.split('\n')
    result = []
    in_func = False
    indent_level = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('def '):
            in_func = True
            indent_level = len(line) - len(line.lstrip())
            result.append(line)
        elif in_func:
            if stripped == '':
                result.append(line)
            elif len(line) - len(line.lstrip()) > indent_level:
                result.append(line)
            else:
                in_func = False
                # Check if this line starts a new function
                if stripped.startswith('def '):
                    in_func = True
                    indent_level = len(line) - len(line.lstrip())
                    result.append(line)
    return '\n'.join(result)


# --- clean_amount tests ---

def test_clean_amount():
    """Test: clean_amount converts various inputs correctly."""
    env = get_cleaning_functions()
    clean_amount = env['clean_amount']

    assert clean_amount("$1,234,567") == 1234567.0
    assert clean_amount("1234567") == 1234567.0
    assert clean_amount("") == 0.0
    assert clean_amount(None) == 0.0
    assert clean_amount("abc") == 0.0
    assert clean_amount("$0") == 0.0
    assert clean_amount(42) == 42.0
    assert clean_amount(3.14) == 3.14


# --- extract_year tests ---

def test_extract_year():
    """Test: extract_year handles various date formats."""
    env = get_cleaning_functions()
    extract_year = env['extract_year']

    assert extract_year("Jan 15, 2020") == 2020
    assert extract_year("2020-01-15") == 2020
    assert extract_year("01/15/2020") == 2020
    assert extract_year("2020") == 2020
    assert extract_year("") is None
    assert extract_year(None) is None
    assert extract_year("1750") is None  # Below 1800
    assert extract_year("2050") is None  # Above 2030


# --- clean_category tests ---

def test_clean_category():
    """Test: clean_category handles comma-separated and edge cases."""
    env = get_cleaning_functions()
    clean_category = env['clean_category']

    assert clean_category("Robotics, AI") == "Robotics"
    assert clean_category(None) == "Unknown"
    assert clean_category("") == "Unknown"
    assert clean_category("Healthcare") == "Healthcare"


# --- clean_country tests ---

def test_clean_country():
    """Test: clean_country applies standardization mapping."""
    env = get_cleaning_functions()
    clean_country = env['clean_country']

    assert clean_country("USA") == "United States"
    assert clean_country("United Arab Emirates") == "UAE"
    assert clean_country("Germany, France") == "Germany"
    assert clean_country("Canada") == "Canada"


if __name__ == '__main__':
    tests = [test_clean_amount, test_extract_year, test_clean_category, test_clean_country]
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
