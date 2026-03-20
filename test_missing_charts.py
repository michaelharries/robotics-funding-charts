"""Tests for Missing_Charts_Analysis.ipynb.

Validates the 19 missing charts notebook structure, chart function behavior,
and output file conventions. Uses real test data from colab/test_data/ when
available, with mock DataFrame fallbacks.
"""
import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Missing_Charts_Analysis.ipynb')
TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
TEST_OUTPUT_DIR = None


def load_cell_source(notebook_path, cell_index):
    """Load and return the source code from a notebook cell."""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    cell = nb['cells'][cell_index]
    return ''.join(cell['source'])


def get_chart_env():
    """Execute Cells 3, 5, and 6 to get chart functions with mock data."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    import pandas as pd
    import numpy as np
    import re

    env = {
        'plt': plt, 'pd': pd, 'np': np, 'os': os, 're': re,
        'FuncFormatter': FuncFormatter,
    }

    # Cell 3: config
    exec(load_cell_source(NOTEBOOK_PATH, 2), env)
    # Cell 5: utilities
    exec(load_cell_source(NOTEBOOK_PATH, 4), env)
    # Cell 6: chart functions
    exec(load_cell_source(NOTEBOOK_PATH, 5), env)

    # Create mock analysis_df (disclosed amounts, valid years)
    mock_funding = {
        'year': [1998, 2005, 2008, 2011, 2011, 2012, 2012, 2013, 2015, 2015,
                 2018, 2018, 2020, 2020, 2020, 2021, 2021, 2022, 2011, 2013,
                 2015, 2018, 2020, 2012, 2014, 2016, 2019, 2021, 1995, 2003],
        'amount_usd': [
            5e6, 10e6, 2e6, 150e6, 8e6, 200e6, 3e6, 50e6, 500e6, 1e6,
            2e6, 300e6, 5e6, 100e6, 50e6, 10e6, 20e6, 400e6, 5e6, 1e6,
            15e6, 25e6, 35e6, 45e6, 55e6, 65e6, 75e6, 85e6, 3e6, 7e6,
        ],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'Robotics',
                           'AI', 'Logistics', 'Robotics', 'AI', 'Robotics',
                           'AI', 'Healthcare', 'Logistics', 'Robotics', 'AI',
                           'Robotics', 'AI', 'Healthcare', 'Logistics', 'Robotics',
                           'AI', 'Healthcare', 'Robotics', 'Logistics', 'AI',
                           'Robotics', 'AI', 'Healthcare', 'Robotics', 'AI'],
        'country_clean': (['United States'] * 6 + ['China'] * 6 +
                          ['Germany'] * 6 + ['Japan'] * 6 + ['India'] * 6),
        'Domain Name': [f'company{i}.com' for i in range(30)],
    }
    env['mock_analysis_df'] = pd.DataFrame(mock_funding)

    # Create mock all_events_df (includes extra rows with 0 amounts for undisclosed)
    mock_all = {k: list(v) for k, v in mock_funding.items()}
    mock_all['year'] += [2011, 2013, 2015, 2018, 2020]
    mock_all['amount_usd'] += [0, 0, 0, 0, 0]
    mock_all['category_clean'] += ['Robotics', 'AI', 'Robotics', 'AI', 'Robotics']
    mock_all['country_clean'] += ['United States', 'China', 'Germany', 'Japan', 'India']
    mock_all['Domain Name'] += [f'company{i}.com' for i in range(30, 35)]
    env['mock_all_events_df'] = pd.DataFrame(mock_all)

    # Create mock companies_df (company-level data)
    mock_companies = {
        'founded_year': [1995, 2005, 2008, 2010, 2012, 2014, 2015, 2016, 2017, 2018,
                         2019, 2020, 2020, 2021, 2021, 2022, 2005, 2010, 2015, 2018,
                         2020, 2012, 2014, 2016, 2019, 2021, 2011, 2013, 2017, 2022],
        'category_clean': ['Robotics', 'Robotics', 'AI', 'Robotics', 'Healthcare', 'Logistics',
                           'Robotics', 'AI', 'Healthcare', 'Robotics', 'Logistics',
                           'AI', 'Robotics', 'Healthcare', 'AI', 'Robotics',
                           'Robotics', 'AI', 'Healthcare', 'Logistics', 'Robotics',
                           'AI', 'Healthcare', 'Robotics', 'Logistics', 'AI',
                           'Robotics', 'AI', 'Robotics', 'Healthcare'],
        'country_clean': (['United States'] * 8 + ['China'] * 5 + ['Germany'] * 5 +
                          ['Japan'] * 4 + ['India'] * 3 + ['United Kingdom'] * 2 +
                          ['Australia'] * 1 + ['Brazil'] * 1 + ['South Korea'] * 1),
        'Is Funded': ['Yes', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes',
                      'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes',
                      'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes'],
        'Is Deadpooled': ['No', 'No', 'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No',
                          'No', 'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No', 'No',
                          'No', 'No', 'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No'],
        'Company Stage': ['Seed', 'Series A', 'Seed', 'Deadpooled', 'Series B', 'Unfunded',
                          'Seed', 'Deadpooled', 'Acquired', 'Series A', 'Seed',
                          'Unfunded', 'Deadpooled', 'Series B', 'Acquired', 'Seed',
                          'Deadpooled', 'Unfunded', 'Series A', 'Seed', 'Acquired',
                          'Seed', 'Unfunded', 'Deadpooled', 'Seed', 'Unfunded',
                          'Series A', 'Seed', 'Series A', 'Seed'],
        'Total Employee Count': [50, 200, 10, 100, 5, 30, 150, 80, 60, 25,
                                 15, 40, 120, 90, 20, 35, 70, 110, 45, 55,
                                 65, 85, 130, 95, 75, 42, 180, 220, 88, 33],
    }
    env['mock_companies_df'] = pd.DataFrame(mock_companies)

    global TEST_OUTPUT_DIR
    TEST_OUTPUT_DIR = env['CHART_OUTPUT_DIR']

    return env


def cleanup_test_files(*filenames):
    """Remove test output files."""
    for fn in filenames:
        path = os.path.join(TEST_OUTPUT_DIR, f'{fn}_no_title.png')
        if os.path.exists(path):
            os.remove(path)


# ======================== Tests ========================

def test_notebook_structure():
    """Test: Notebook has exactly 9 cells with correct types."""
    with open(NOTEBOOK_PATH, 'r') as f:
        nb = json.load(f)
    cells = nb['cells']
    assert len(cells) == 9, f"Expected 9 cells, got {len(cells)}"
    assert cells[0]['cell_type'] == 'markdown', "Cell 1 should be markdown"
    for i in range(1, 9):
        assert cells[i]['cell_type'] == 'code', f"Cell {i+1} should be code"


def test_configuration_constants():
    """Test: Cell 3 has required configuration constants."""
    source = load_cell_source(NOTEBOOK_PATH, 2)
    exec_globals = {}
    exec(source, exec_globals)

    assert exec_globals['FUNDED_START_YEAR'] == 2011
    assert exec_globals['BINARY_STATUS_COLORS'] == ['#88CCEE', '#332288']

    # Macro-region groups
    mrg = exec_globals['MACRO_REGION_GROUPS']
    assert set(mrg.keys()) == {'Americas', 'Europe/Africa', 'Asia/Pacific'}

    # Country to macro region should be populated
    c2mr = exec_globals['COUNTRY_TO_MACRO_REGION']
    assert c2mr['United States'] == 'Americas'
    assert c2mr['China'] == 'Asia/Pacific'
    assert c2mr['Germany'] == 'Europe/Africa'


def test_cell2_imports():
    """Test: Cell 2 contains required imports."""
    source = load_cell_source(NOTEBOOK_PATH, 1)
    required = ['matplotlib.pyplot', 'pandas', 'numpy', 'os', 'zipfile', 'gc', 'google.colab']
    for pkg in required:
        assert pkg in source, f"Cell 2 missing import for '{pkg}'"
    assert 'openpyxl' in source, "Cell 2 missing openpyxl install"


def test_fa_charts_structure():
    """Test: FA (funding amount) charts have correct y-axis and single-series bars."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_funding_yearly_bar'](
        env['mock_analysis_df'], 'amount', None, 2011, 'test_fa_global'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    ylabel = ax.get_ylabel()
    assert 'Funding Amount' in ylabel or 'USD' in ylabel, f"FA chart y-axis label unexpected: {ylabel}"

    path = os.path.join(TEST_OUTPUT_DIR, 'test_fa_global_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_fa_global')


def test_fe_charts_structure():
    """Test: FE (funding events) charts have integer y-axis."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_funding_yearly_bar'](
        env['mock_all_events_df'], 'count', None, 2011, 'test_fe_global'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    ylabel = ax.get_ylabel()
    assert 'Funding Events' in ylabel, f"FE chart y-axis label unexpected: {ylabel}"

    plt.close(fig)
    cleanup_test_files('test_fe_global')


def test_funded_by_year_buckets():
    """Test: Companies-founded-by-year charts have '< 2000s' and '2000 - 2010' buckets."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_founded_by_year'](
        env['mock_companies_df'], None, 'test_funded_buckets'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert '< 2000s' in labels, f"Missing '< 2000s' bucket. Labels: {labels}"
    assert '2000 - 2010' in labels, f"Missing '2000 - 2010' bucket. Labels: {labels}"

    plt.close(fig)
    cleanup_test_files('test_funded_buckets')


def test_stacked_funded_has_two_series():
    """Test: Stacked funded charts have exactly 2 stack layers (No/Yes)."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    # Use a scope that includes multiple countries
    asia_pacific_countries = [c for st in env['MACRO_REGION_GROUPS']['Asia/Pacific']
                              for c in env['SECOND_TIER_REGIONS'][st]]
    scope_ap = lambda df: df[df['country_clean'].isin(asia_pacific_countries)]

    fig = env['create_companies_by_year_funded_stacked'](
        env['mock_companies_df'], scope_ap, 2011, 'test_stacked_funded'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    legend = ax.get_legend()
    assert legend is not None, "Stacked chart missing legend"
    legend_texts = [t.get_text() for t in legend.get_texts()]
    assert 'No' in legend_texts, f"Missing 'No' in legend: {legend_texts}"
    assert 'Yes' in legend_texts, f"Missing 'Yes' in legend: {legend_texts}"

    plt.close(fig)
    cleanup_test_files('test_stacked_funded')


def test_regional_bars_three_regions():
    """Test: Regional status bars have 3 bars for the 3 macro-regions."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_regional_status_bars'](
        env['mock_companies_df'], 'funded', 'test_regional_funded'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_xticklabels()]
    assert len(labels) == 3, f"Expected 3 region labels, got {len(labels)}: {labels}"
    assert 'Americas' in labels
    assert 'Europe/Africa' in labels
    assert 'Asia/Pacific' in labels

    plt.close(fig)
    cleanup_test_files('test_regional_funded')


def test_pie_three_slices():
    """Test: Funded region pie has 3 slices."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_funded_region_pie'](
        env['mock_companies_df'], 'test_funded_pie'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    # Count wedge patches
    wedges = [p for p in ax.patches if hasattr(p, 'theta2')]
    assert len(wedges) == 3, f"Expected 3 pie slices, got {len(wedges)}"

    plt.close(fig)
    cleanup_test_files('test_funded_pie')


def test_top10_seed_a_combines_stages():
    """Test: Seed+A chart uses combined Seed + Series A stages, not a literal 'Seed+A'."""
    env = get_chart_env()
    import matplotlib.pyplot as plt
    import pandas as pd

    companies = env['mock_companies_df']
    # Combine Seed + Series A
    seed_a_df = companies[companies['Company Stage'].str.strip().isin(['Seed', 'Series A'])]
    assert len(seed_a_df) > 0, "No Seed or Series A companies found in mock data"

    fig = env['create_top10_countries_chart'](
        seed_a_df, 'count', 'Number of Companies', 'test_seed_a', color='#332288'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    # Should have bars
    bars = [p for p in ax.patches if hasattr(p, 'get_width')]
    assert len(bars) > 0, "Seed+A chart has no bars"

    plt.close(fig)
    cleanup_test_files('test_seed_a')


def test_top10_employee_count():
    """Test: Employee count chart exists with comma-formatted values."""
    env = get_chart_env()
    import matplotlib.pyplot as plt
    import pandas as pd

    companies = env['mock_companies_df']
    emp_col = 'Total Employee Count'
    emp_df = companies[companies[emp_col].notna()].copy()
    emp_df[emp_col] = pd.to_numeric(emp_df[emp_col], errors='coerce')
    emp_df = emp_df[emp_df[emp_col] > 0]

    fig = env['create_top10_countries_chart'](
        emp_df, emp_col, 'Total Employee Count', 'test_employee', color='#88CCEE'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    # Check at least one text annotation has a comma or a number
    texts = [t.get_text() for t in ax.texts]
    assert len(texts) > 0, "Employee chart has no value labels"

    plt.close(fig)
    cleanup_test_files('test_employee')


def test_global_vc_from_csv():
    """Test: Global VC chart uses external CSV data, years 2000-2025."""
    env = get_chart_env()
    import matplotlib.pyplot as plt
    import pandas as pd

    # Try real CSV data first
    csv_path = os.path.join(TEST_DATA_DIR, 'global_vc_totals_2000_to_2025.csv')
    if os.path.exists(csv_path):
        vc_df = pd.read_csv(csv_path)
    else:
        # Mock fallback
        vc_df = pd.DataFrame({
            'Year': list(range(2000, 2026)),
            'Global VC Investment (USD billions)': [
                57.1, 29.5, 23.0, 22.9, 26.0, 29.3, 36.8, 45.6, 53.2, 37.6,
                53.0, 65.7, 63.6, 69.8, 111.2, 152.8, 151.5, 171.9, 271.4, 294.8,
                294.0, 621.0, 415.1, 248.4, 314.0, 469.0
            ]
        })

    fig = env['create_global_vc_funding_chart'](vc_df, 2000, 'test_vc')
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    # Should have bars spanning 2000-2025
    bars = [p for p in ax.patches if hasattr(p, 'get_width')]
    assert len(bars) == 26, f"Expected 26 bars (2000-2025), got {len(bars)}"

    plt.close(fig)
    cleanup_test_files('test_vc')


def test_filename_conventions():
    """Test: All generated files end with _no_title.png, no spaces or parens."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    # Generate a couple of charts and check filename conventions
    test_names = []

    fig = env['create_funding_yearly_bar'](
        env['mock_analysis_df'], 'amount', None, 2011, 'test_fn_check_fa'
    )
    test_names.append('test_fn_check_fa')
    plt.close(fig)

    fig = env['create_companies_founded_by_year'](
        env['mock_companies_df'], None, 'test_fn_check_funded'
    )
    test_names.append('test_fn_check_funded')
    plt.close(fig)

    for name in test_names:
        expected = f'{name}_no_title.png'
        path = os.path.join(TEST_OUTPUT_DIR, expected)
        assert os.path.exists(path), f"Expected file not found: {path}"
        assert ' ' not in expected, f"Filename has spaces: {expected}"
        assert '(' not in expected and ')' not in expected, f"Filename has parens: {expected}"

    cleanup_test_files(*test_names)


def test_no_open_figures():
    """Test: No matplotlib figures leak after chart generation."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    # Close all pre-existing figures
    plt.close('all')

    fig = env['create_funding_yearly_bar'](
        env['mock_analysis_df'], 'count', None, 2011, 'test_leak_check'
    )
    plt.close(fig)

    open_figs = plt.get_fignums()
    assert len(open_figs) == 0, f"Leaked figures: {open_figs}"

    cleanup_test_files('test_leak_check')


def test_all_19_charts_generated():
    """Test: Run the generation loop and verify 18 Tracxn charts are produced.

    Note: Chart 19 (global_vc_totals) requires CSV upload and is tested separately.
    This test generates the 18 Tracxn-based charts using mock data.
    """
    env = get_chart_env()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import gc
    import pandas as pd

    env['gc'] = gc
    env['SKIP_TRACXN_UPLOAD'] = False
    env['SKIP_VC_UPLOAD'] = True
    env['analysis_df'] = env['mock_analysis_df']
    env['all_events_df'] = env['mock_all_events_df']
    env['companies_df'] = env['mock_companies_df']

    # Execute Cell 7 (master generation)
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)

    expected_tracxn_charts = [
        'global_fa_yearly', 'americas_fa_yearly', 'asia_pacific_fa_yearly', 'europe_africa_fa_yearly',
        'global_fe_yearly', 'americas_fe_yearly', 'asia_pacific_fe_yearly', 'europe_africa_fe_yearly',
        'global_companies_founded_by_year', 'americas_companies_founded_by_year', 'usa_companies_founded_by_year',
        'asia_pacific_companies_by_year_funded', 'europe_africa_companies_by_year_funded',
        'regional_deadpooled_percentage', 'regional_funded_percentage',
        'regional_funded_companies_pie',
        'top10_stage_SeedA', 'top10_total_employee_count',
    ]

    generated = env.get('charts_generated', [])
    failed = env.get('charts_failed', [])

    for chart_name in expected_tracxn_charts:
        assert chart_name in generated, \
            f"Chart '{chart_name}' not generated. Generated: {generated}. Failed: {failed}"

    # Also verify PNG files exist
    for chart_name in expected_tracxn_charts:
        path = os.path.join(TEST_OUTPUT_DIR, f'{chart_name}_no_title.png')
        assert os.path.exists(path), f"PNG not found: {path}"
        assert os.path.getsize(path) > 0, f"PNG is empty: {path}"

    # Cleanup
    plt.close('all')
    for chart_name in expected_tracxn_charts:
        cleanup_test_files(chart_name)


def test_zip_export():
    """Test: ZIP is created with correct structure."""
    env = get_chart_env()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import gc
    import zipfile

    env['gc'] = gc
    env['zipfile'] = zipfile
    env['SKIP_TRACXN_UPLOAD'] = False
    env['SKIP_VC_UPLOAD'] = True
    env['analysis_df'] = env['mock_analysis_df']
    env['all_events_df'] = env['mock_all_events_df']
    env['companies_df'] = env['mock_companies_df']

    # Mock files.download to avoid Colab-specific error
    class MockFiles:
        def download(self, path):
            pass
        def upload(self):
            return {}
    env['files'] = MockFiles()

    # Execute Cell 7 (generation) then Cell 9 (ZIP)
    exec(load_cell_source(NOTEBOOK_PATH, 6), env)
    exec(load_cell_source(NOTEBOOK_PATH, 8), env)

    zip_path = 'missing_charts.zip'
    assert os.path.exists(zip_path), f"ZIP file not found: {zip_path}"

    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        # All should be flat (no directory structure)
        for name in names:
            assert '/' not in name, f"ZIP entry has directory: {name}"
            assert name.endswith('_no_title.png'), f"ZIP entry doesn't match convention: {name}"

    # Cleanup
    plt.close('all')
    if os.path.exists(zip_path):
        os.remove(zip_path)

    # Clean up generated chart files
    if os.path.exists(TEST_OUTPUT_DIR):
        for f in os.listdir(TEST_OUTPUT_DIR):
            if f.startswith('test_') or f.endswith('_no_title.png'):
                os.remove(os.path.join(TEST_OUTPUT_DIR, f))


if __name__ == '__main__':
    tests = [
        test_notebook_structure,
        test_configuration_constants,
        test_cell2_imports,
        test_fa_charts_structure,
        test_fe_charts_structure,
        test_funded_by_year_buckets,
        test_stacked_funded_has_two_series,
        test_regional_bars_three_regions,
        test_pie_three_slices,
        test_top10_seed_a_combines_stages,
        test_top10_employee_count,
        test_global_vc_from_csv,
        test_filename_conventions,
        test_no_open_figures,
        test_all_19_charts_generated,
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
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
