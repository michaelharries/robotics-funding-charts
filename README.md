# Robotics Industry Funding Charts

A Google Colab notebook that generates publication-ready charts from Tracxn robotics company and funding data. Upload two Excel files, run all cells, and download a ZIP of PNG charts.

## Prerequisites

- A Google account (for Google Colab)
- Two data exports from [Tracxn](https://tracxn.com/) in Excel format:

### 1. Companies export

Must contain at least these columns:

| Column | Description |
|---|---|
| `Subcategory` | Used to auto-detect this file |
| `Domain Name` | Join key for merging with funding data |
| `Category` | Sector classification |
| `Country` | Company headquarters country |
| `Founded Year` | Year the company was founded |
| `Is Funded` | Whether the company has received funding |
| `Is Acquired` | Acquisition status |
| `Is IPO` | IPO status |
| `Is Deadpooled` | Whether the company has shut down |

### 2. Funding rounds export

Must contain at least these columns:

| Column | Description |
|---|---|
| `Domain Name` | Join key for merging with company data |
| `Round Amount (in USD)` or `Round Amount (USD)` | Funding amount (both naming variants are supported) |
| `Round Date` | Date of the funding round |
| `Round Name` | Type of funding round |

## Open in Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michaelharries/robotics-funding-charts/blob/main/Robotics_Industry_Analysis.ipynb)

## How to run

1. Click the "Open in Colab" badge above.
2. Run all cells (**Runtime > Run all**).
3. When prompted, upload your two Tracxn Excel files (companies + funding rounds). The notebook auto-detects which is which based on the presence of a `Subcategory` column.
4. Wait for all charts to generate.
5. Download the `robotics_charts.zip` file from the Colab file browser (click the folder icon in the left sidebar). It contains all charts as 300 DPI PNGs.

> **Note:** Colab's filesystem is ephemeral -- download the ZIP before your session ends.

## What it produces

The notebook generates charts across several categories:

- **Companies founded** -- line charts, bar charts, outcome breakdowns (active/failed/acquired/IPO), sector breakdowns, and funding status
- **Global funding** -- total annual funding with round counts, stacked by round size (above/below $100M)
- **Sector funding** -- one stacked funding chart per sector
- **Region funding** -- one stacked funding chart per geographic region (USA, China, Western Europe, APAC, etc.)
- **Subcategory funding** -- one stacked funding chart per Tracxn subcategory

All charts use a colorblind-friendly palette (Paul Tol) and IEEE-compatible styling.
