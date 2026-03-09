"""Tests for Section 05: Funding Charts and Gap Charts.

Validates create_total_funding_by_year_chart, create_stacked_funding_chart,
the six missing funding analysis chart functions, and the 12 gap chart
functions (investment type, market segment, state-of-market, top-10 countries).
"""
import json
import os
import sys

NOTEBOOK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Robotics_Industry_Analysis.ipynb')
TEST_OUTPUT_DIR = None


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

    # Create mock analysis_df (disclosed amounts, valid years)
    mock_funding = {
        'year': [2000, 2000, 2001, 2001, 2005, 2005, 2005, 2010, 2010, 2015,
                 2015, 2015, 2015, 2018, 2018, 2020, 2020, 2020, 2020, 2020],
        'amount_usd': [
            5e6, 10e6, 2e6, 150e6,  # 2000-2001
            8e6, 200e6, 3e6,         # 2005
            50e6, 500e6,              # 2010
            1e6, 2e6, 300e6, 5e6,    # 2015
            100e6, 50e6,              # 2018
            10e6, 20e6, 400e6, 5e6, 1e6,  # 2020
        ],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'Robotics',
                           'AI', 'Logistics', 'Robotics', 'AI', 'Robotics',
                           'AI', 'Healthcare', 'Logistics', 'Robotics', 'AI',
                           'Robotics', 'AI', 'Healthcare', 'Logistics', 'Drones'],
        'country_clean': ['United States'] * 10 + ['China'] * 5 + ['Germany'] * 5,
        'investment_type': ['Seed', 'Series A', 'Seed', 'Series B', 'Seed',
                           'Series A', 'Series B', 'Series C', 'Series A', 'Seed',
                           'Series A', 'Series B', 'Series C', 'Series A', 'Seed',
                           'Seed', 'Series A', 'Series B', 'Series C', 'Seed'],
    }
    env['mock_analysis_df'] = pd.DataFrame(mock_funding)

    # Create mock all_events_df (includes extra rows with 0 amounts for undisclosed)
    mock_all = mock_funding.copy()
    # Add some undisclosed events (amount_usd = 0)
    mock_all['year'] = mock_all['year'] + [2000, 2005, 2010, 2015, 2020]
    mock_all['amount_usd'] = mock_all['amount_usd'] + [0, 0, 0, 0, 0]
    mock_all['category_clean'] = mock_all['category_clean'] + ['Robotics', 'AI', 'Robotics', 'AI', 'Robotics']
    mock_all['country_clean'] = mock_all['country_clean'] + ['United States', 'China', 'Germany', 'United States', 'China']
    mock_all['investment_type'] = mock_all['investment_type'] + ['Seed', 'Series A', 'Seed', 'Series A', 'Seed']
    env['mock_all_events_df'] = pd.DataFrame(mock_all)

    # Create mock companies_df (company-level data for state-of-market charts)
    import numpy as np_local
    mock_companies = {
        'founded_year': [2005, 2008, 2010, 2012, 2014, 2015, 2016, 2017, 2018, 2019,
                         2020, 2020, 2021, 2021, 2022, 2005, 2010, 2015, 2018, 2020,
                         2012, 2014, 2016, 2019, 2021],
        'category_clean': ['Robotics', 'AI', 'Robotics', 'Healthcare', 'Logistics',
                           'Robotics', 'AI', 'Healthcare', 'Robotics', 'Logistics',
                           'AI', 'Robotics', 'Healthcare', 'AI', 'Robotics',
                           'Robotics', 'AI', 'Healthcare', 'Logistics', 'Robotics',
                           'AI', 'Healthcare', 'Robotics', 'Logistics', 'AI'],
        'country_clean': ['United States'] * 8 + ['China'] * 5 + ['Germany'] * 5 +
                         ['United Kingdom'] * 4 + ['India'] * 3,
        'Is Funded': ['Yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes',
                      'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'Yes', 'No',
                      'Yes', 'No', 'Yes', 'Yes', 'No'],
        'Is Deadpooled': ['No', 'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No', 'No',
                          'No', 'Yes', 'No', 'No', 'No', 'Yes', 'No', 'No', 'No', 'No',
                          'No', 'No', 'Yes', 'No', 'No'],
        'Is Acquired': ['No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'Yes', 'No', 'No',
                        'No', 'No', 'No', 'Yes', 'No', 'No', 'No', 'No', 'No', 'Yes',
                        'No', 'No', 'No', 'No', 'No'],
        'Is IPO': ['No'] * 25,
        'Company Stage': ['Seed', 'Series A', 'Deadpooled', 'Series B', 'Unfunded',
                          'Seed', 'Deadpooled', 'Acquired', 'Series A', 'Seed',
                          'Unfunded', 'Deadpooled', 'Series B', 'Acquired', 'Seed',
                          'Deadpooled', 'Unfunded', 'Series A', 'Seed', 'Acquired',
                          'Seed', 'Unfunded', 'Deadpooled', 'Seed', 'Unfunded'],
        'Total Employee Count': [50, 200, 10, 100, 5, 30, 150, 80, 60, 25,
                                 15, 40, 120, 90, 20, 35, 70, 110, 45, 55,
                                 65, 85, 130, 95, 75],
    }
    env['mock_companies_df'] = pd.DataFrame(mock_companies)

    global TEST_OUTPUT_DIR
    TEST_OUTPUT_DIR = env['CHART_OUTPUT_DIR']

    return env


def cleanup_test_files(*filenames):
    for fn in filenames:
        path = os.path.join(TEST_OUTPUT_DIR, f'{fn}_no_title.png')
        if os.path.exists(path):
            os.remove(path)


def test_total_funding_chart():
    """Test: create_total_funding_by_year_chart returns valid dual-axis figure."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_total_funding_by_year_chart'](
        env['mock_analysis_df'], start_year=2000, filename='test_total_funding'
    )
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2  # primary + twinx

    path = os.path.join(TEST_OUTPUT_DIR, 'test_total_funding_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_total_funding')


def test_stacked_funding_chart():
    """Test: create_stacked_funding_chart returns valid figure with correct legend."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_stacked_funding_chart'](
        env['mock_analysis_df'], env['mock_all_events_df'],
        scope_filter=None,
        start_year=2000, filename='test_stacked'
    )
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 2  # primary + twinx

    legend = fig.axes[0].get_legend()
    labels = [t.get_text() for t in legend.get_texts()]
    assert '< $100M' in labels and '>= $100M' in labels

    path = os.path.join(TEST_OUTPUT_DIR, 'test_stacked_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_stacked')


def test_stacked_funding_empty_filter():
    """Test: create_stacked_funding_chart returns None for empty filter."""
    env = get_chart_env()

    result = env['create_stacked_funding_chart'](
        env['mock_analysis_df'], env['mock_all_events_df'],
        scope_filter=lambda df: df[df['category_clean'] == 'ZZZZZ'],
        start_year=2000, filename='test_empty'
    )
    assert result is None


def test_stacked_funding_with_scope_filter():
    """Test: create_stacked_funding_chart works with sector filter."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_stacked_funding_chart'](
        env['mock_analysis_df'], env['mock_all_events_df'],
        scope_filter=lambda df: df[df['category_clean'] == 'Robotics'],
        start_year=2000, filename='test_sector_filter'
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
    cleanup_test_files('test_sector_filter')


def test_auto_scale_billions():
    """Test: auto-scale selects billions when total >= $1B."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    # Mock data total is > $1B, so should use billions
    total = env['mock_analysis_df']['amount_usd'].sum()
    assert total >= 1_000_000_000, f"Mock data total {total} should be >= 1B for this test"

    fig = env['create_stacked_funding_chart'](
        env['mock_analysis_df'], env['mock_all_events_df'],
        scope_filter=None,
        start_year=2000, filename='test_scale_b'
    )
    # Check that formatter uses 'B'
    formatter = fig.axes[0].yaxis.get_major_formatter()
    label = formatter(1.0, 0)
    assert 'B' in label, f"Expected billions format, got '{label}'"
    plt.close(fig)
    cleanup_test_files('test_scale_b')


# --- Missing Funding Analysis Chart Tests ---

def test_missing_funding_by_year():
    """Test: create_missing_funding_by_year_chart produces valid bar chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_by_year_chart'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_by_year'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Funding Rounds Without Amount (%)'
    assert ax.get_xlabel() == 'Year'

    # Should have bars (patches)
    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) > 0

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_by_year_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_by_year')


def test_missing_funding_by_country():
    """Test: create_missing_funding_by_country_chart produces valid horizontal bar chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_by_country_chart'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_by_country'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Funding Rounds Without Amount (%)'
    assert ax.get_ylabel() == 'Country'

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_by_country_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_by_country')


def test_missing_funding_by_region():
    """Test: create_missing_funding_by_region_chart produces valid bar chart with 3 regions."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_by_region_chart'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_by_region'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Region'
    assert ax.get_ylabel() == 'Funding Rounds Without Amount (%)'

    # Should have bars for mapped regions
    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) > 0

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_by_region_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_by_region')


def test_missing_funding_by_category():
    """Test: create_missing_funding_by_category_chart produces valid horizontal bar chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_by_category_chart'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_by_category'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Funding Rounds Without Amount (%)'
    assert ax.get_ylabel() == 'Robotics Category'

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_by_category_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_by_category')


def test_missing_funding_by_type():
    """Test: create_missing_funding_by_type_chart produces valid horizontal bar chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_by_type_chart'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_by_type'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Funding Rounds Without Amount (%)'
    assert ax.get_ylabel() == 'Investment Type'

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_by_type_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_by_type')


def test_missing_funding_overview_pie():
    """Test: create_missing_funding_overview_pie produces valid pie chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_missing_funding_overview_pie'](
        env['mock_all_events_df'], start_year=2000, filename='test_missing_pie'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]

    # Pie chart should have wedge patches
    from matplotlib.patches import Wedge
    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    assert len(wedges) == 2, f"Expected 2 pie slices, got {len(wedges)}"

    path = os.path.join(TEST_OUTPUT_DIR, 'test_missing_pie_no_title.png')
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
    plt.close(fig)
    cleanup_test_files('test_missing_pie')


# --- Phase 1: Investment Type Chart Tests ---

def test_investment_type_overview_amount():
    """Test: create_investment_type_overview_chart with metric='amount'."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_investment_type_overview_chart'](
        env['mock_analysis_df'], 'amount', None, 2000, 'test_it_ov_amount'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Total Funding Amount (USD)'
    assert ax.get_xlabel() == 'Investment Type'

    # Should have bars
    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) > 0

    path = os.path.join(TEST_OUTPUT_DIR, 'test_it_ov_amount_no_title.png')
    assert os.path.exists(path)
    plt.close(fig)
    cleanup_test_files('test_it_ov_amount')


def test_investment_type_overview_count():
    """Test: create_investment_type_overview_chart with metric='count'."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_investment_type_overview_chart'](
        env['mock_all_events_df'], 'count', None, 2000, 'test_it_ov_count'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Number of Funding Events'

    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) > 0

    plt.close(fig)
    cleanup_test_files('test_it_ov_count')


def test_investment_type_yearly_stacked():
    """Test: create_investment_type_yearly_chart produces stacked bar with legend."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_investment_type_yearly_chart'](
        env['mock_analysis_df'], 'amount', None, 2000, 'test_it_yearly'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Investment Amount (USD)'

    legend = ax.get_legend()
    assert legend is not None, "Expected legend on yearly chart"

    plt.close(fig)
    cleanup_test_files('test_it_yearly')


def test_investment_type_overview_with_scope():
    """Test: investment type overview with scope filter returns valid chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_investment_type_overview_chart'](
        env['mock_analysis_df'], 'amount',
        lambda df: df[df['country_clean'] == 'United States'],
        2000, 'test_it_ov_scope'
    )
    assert isinstance(fig, plt.Figure)
    plt.close(fig)
    cleanup_test_files('test_it_ov_scope')


def test_macro_region_overview():
    """Test: create_macro_region_overview_chart produces 3 bars."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_macro_region_overview_chart'](
        env['mock_all_events_df'], 'count', 2000, 'test_macro_ov'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Number of Funding Events'

    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) == 3, f"Expected 3 macro-region bars, got {len(bars)}"

    plt.close(fig)
    cleanup_test_files('test_macro_ov')


def test_macro_region_yearly():
    """Test: create_macro_region_yearly_chart produces stacked bars with 3 regions."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_macro_region_yearly_chart'](
        env['mock_all_events_df'], 'count', 2000, 'test_macro_yearly'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]

    legend = ax.get_legend()
    assert legend is not None

    plt.close(fig)
    cleanup_test_files('test_macro_yearly')


# --- Phase 2: Market Segment Chart Tests ---

def test_funding_by_category_pie():
    """Test: create_funding_by_category_pie produces valid pie chart."""
    env = get_chart_env()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge

    fig = env['create_funding_by_category_pie'](
        env['mock_analysis_df'], None, 2000, 'test_cat_pie'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]

    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    assert len(wedges) > 0, "Expected pie wedges"

    plt.close(fig)
    cleanup_test_files('test_cat_pie')


def test_funding_by_category_yearly():
    """Test: create_funding_by_category_yearly produces stacked bars with legend."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_funding_by_category_yearly'](
        env['mock_analysis_df'], None, 2000, 'test_cat_yearly'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Investment Amount (USD)'

    legend = ax.get_legend()
    assert legend is not None

    plt.close(fig)
    cleanup_test_files('test_cat_yearly')


# --- Phase 3: State of Market Chart Tests ---

def test_funded_percentage_chart():
    """Test: create_funded_percentage_chart produces donut chart with 2 wedges."""
    env = get_chart_env()
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge

    fig = env['create_funded_percentage_chart'](
        env['mock_companies_df'], None, 'test_funded_pct'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]

    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    assert len(wedges) == 2, f"Expected 2 donut wedges, got {len(wedges)}"

    plt.close(fig)
    cleanup_test_files('test_funded_pct')


def test_companies_by_funding_type():
    """Test: create_companies_by_funding_type_chart produces horizontal bars."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_by_funding_type_chart'](
        env['mock_companies_df'], None, 'test_by_funding_type'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_xlabel() == 'Number of Companies'

    bars = [p for p in ax.patches if hasattr(p, 'get_width')]
    assert len(bars) > 0

    plt.close(fig)
    cleanup_test_files('test_by_funding_type')


def test_companies_by_year_deadpool():
    """Test: create_companies_by_year_deadpool_chart produces stacked bars."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_companies_by_year_deadpool_chart'](
        env['mock_companies_df'], None, 2000, 'test_deadpool'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Number of Companies'

    legend = ax.get_legend()
    assert legend is not None

    plt.close(fig)
    cleanup_test_files('test_deadpool')


def test_regional_company_bars():
    """Test: create_regional_company_bars produces bars for each metric variant."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    for metric in ['count', 'deadpooled', 'funded', 'pct_funded']:
        fname = f'test_reg_{metric}'
        fig = env['create_regional_company_bars'](
            env['mock_companies_df'], metric, fname
        )
        assert isinstance(fig, plt.Figure), f"Failed for metric={metric}"
        ax = fig.axes[0]
        bars = [p for p in ax.patches if hasattr(p, 'get_height')]
        assert len(bars) == 3, f"Expected 3 region bars for {metric}, got {len(bars)}"
        plt.close(fig)
        cleanup_test_files(fname)


def test_category_status_chart():
    """Test: create_category_status_chart produces stacked percentage bars."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    for metric in ['deadpooled', 'funded']:
        fname = f'test_cat_status_{metric}'
        fig = env['create_category_status_chart'](
            env['mock_companies_df'], metric, fname
        )
        assert isinstance(fig, plt.Figure), f"Failed for metric={metric}"

        legend = fig.axes[0].get_legend()
        assert legend is not None

        plt.close(fig)
        cleanup_test_files(fname)


# --- Phase 4: Top 10 Country Chart Tests ---

def test_top10_countries():
    """Test: create_top10_countries_chart produces bars sorted descending."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_top10_countries_chart'](
        env['mock_companies_df'], 'count', 'Number of Companies', 'test_top10'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Number of Companies'

    bars = [p for p in ax.patches if hasattr(p, 'get_height')]
    assert len(bars) > 0
    assert len(bars) <= 10

    # Verify bars are sorted descending
    heights = [b.get_height() for b in bars]
    assert heights == sorted(heights, reverse=True), "Bars should be sorted descending"

    plt.close(fig)
    cleanup_test_files('test_top10')


def test_top10_countries_log_scale():
    """Test: create_top10_countries_chart with log scale."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_top10_countries_chart'](
        env['mock_analysis_df'], 'sum_amount', 'Funding (USD)', 'test_top10_log',
        use_log=True
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_yscale() == 'log'

    plt.close(fig)
    cleanup_test_files('test_top10_log')


def test_top10_countries_employee_count():
    """Test: create_top10_countries_chart with employee count metric."""
    env = get_chart_env()
    import matplotlib.pyplot as plt

    fig = env['create_top10_countries_chart'](
        env['mock_companies_df'], 'Total Employee Count', 'Total Employee Count',
        'test_top10_emp'
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert ax.get_ylabel() == 'Total Employee Count'

    plt.close(fig)
    cleanup_test_files('test_top10_emp')


if __name__ == '__main__':
    tests = [
        test_total_funding_chart,
        test_stacked_funding_chart,
        test_stacked_funding_empty_filter,
        test_stacked_funding_with_scope_filter,
        test_auto_scale_billions,
        test_missing_funding_by_year,
        test_missing_funding_by_country,
        test_missing_funding_by_region,
        test_missing_funding_by_category,
        test_missing_funding_by_type,
        test_missing_funding_overview_pie,
        # Phase 1
        test_investment_type_overview_amount,
        test_investment_type_overview_count,
        test_investment_type_yearly_stacked,
        test_investment_type_overview_with_scope,
        test_macro_region_overview,
        test_macro_region_yearly,
        # Phase 2
        test_funding_by_category_pie,
        test_funding_by_category_yearly,
        # Phase 3
        test_funded_percentage_chart,
        test_companies_by_funding_type,
        test_companies_by_year_deadpool,
        test_regional_company_bars,
        test_category_status_chart,
        # Phase 4
        test_top10_countries,
        test_top10_countries_log_scale,
        test_top10_countries_employee_count,
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
    if TEST_OUTPUT_DIR and os.path.exists(TEST_OUTPUT_DIR) and not os.listdir(TEST_OUTPUT_DIR):
        os.rmdir(TEST_OUTPUT_DIR)
    sys.exit(1 if failed else 0)
