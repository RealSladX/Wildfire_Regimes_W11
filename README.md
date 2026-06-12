# Wildfire_Regimes_W11

Code and workflow for analysis and visualization of wildfire trends in important water-supply watersheds in the western United States.

This repository supports the manuscript analysis by generating geospatial burn-area matrices, water-yield summaries, statistical trend results, and publication figures for Western U.S. HUC12 watersheds.

## Repository status

This code is intended for reproducible scientific review. Raw geospatial and climate datasets are not stored in this repository because of size, licensing, and external distribution constraints. Users must download source data independently and place files in the expected directory structure before running the workflow.

## System requirements

The workflow uses Python and common scientific/geospatial libraries. It has been designed to work with any Python environment manager that can install packages from `requirements.txt`, including `pip`, `venv`, `conda`, `mamba`, `uv`, `poetry`, `hatch`, or `pixi` with pip interoperability.

Recommended baseline:

- Python 3.10 or 3.11
- GDAL-compatible geospatial stack
- Sufficient disk space for raw geospatial layers, ERA5 GRIB files, intermediate shapefiles, and output tables
- Multi-core machine recommended for Dask-based spatial joins

## Installation

Using `venv` and `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Using `conda` or `mamba`:

```bash
conda create -n wildfire-regimes-w11 python=3.11
conda activate wildfire-regimes-w11
python -m pip install -r requirements.txt
```

Using `uv`:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Required input data

Before running analysis, place source datasets under `DATA/` and make sure `config.json` points to the correct filenames.

| Dataset | Expected role in workflow | Notes |
|---|---|---|
| USGS Watershed Boundary Dataset | HUC12 watershed geometries | Used to define Western 11-state study watersheds |
| National Interagency Fire Center historical fire perimeters | Fire perimeter geometries and fire years | Must include `FIRE_YEAR_INT`, `INCIDENT`, and geometry |
| ERA5 runoff and precipitation GRIB file | Runoff (`ro`) and precipitation (`tp`) climate variables | Read with `xarray`, `cfgrib`, and ecCodes backend |
| EPA Level III ecoregions | Ecoregion overlays | Must include `NA_L1NAME`, `NA_L2NAME`, `US_L3NAME`, and geometry |
| Forests to Faucets dataset | Downstream population and water-supply attributes | Used for downstream consumer groupings |
| U.S. state boundary shapefile | Figure basemap | Used for Western state outlines |


## Expected local directory structure

Run `00_setup_directories.py` before analysis. It creates the derived-output directories.

```text
Wildfire_Regimes_W11/
  DATA/
    ERA5.grib
    <Watershed Boundary Dataset files>
    <NIFC fire perimeter files>
    <EPA ecoregion files>
    <Forests to Faucets geodatabase>
    <U.S. state boundary shapefile>
  Assets/
    Shapes/
    Tables/
    Results/
  Figures/
  utils/
    stat.py
    matplot.py
    geoplot.py
  config.json requirements.txt
```

`utils/stat.py` and `utils/matplot.py` are required helper modules. They must be included in any public release because scripts import `utils.stat` and `utils.matplot`. `utils/geoplot.py` is optional for the uploaded main workflow, but include it if retaining all helper utilities.


## Helper modules

The repository uses helper modules under `utils/`:

| Module | Required by uploaded workflow? | Purpose | External dependencies introduced |
|---|---:|---|---|
| `utils/stat.py` | Yes | Asset loading, quantile grouping, time-series aggregation, Mann-Kendall trend tests, Pettitt changepoint tests | `geopandas`, `pyhomogeneity`, `pymannkendall`, `scipy`, `statsmodels` |
| `utils/matplot.py` | Yes | Reusable figure and time-series plotting utilities | `matplotlib`, `seaborn`, `palettable` |
| `utils/geoplot.py` | Optional / legacy | Polygon plotting utilities | `geopandas`, `shapely`, `palettable`; also imports `pycollection.asset_manager.paths` |

Important: `utils/geoplot.py` currently imports `pycollection.asset_manager.paths`. The uploaded main analysis and figure scripts do not import `utils.geoplot`; therefore this dependency is not required for reproducing the manuscript workflow. For a public release, either remove or refactor that import, or include the exact local `pycollection` module if it is part of the project.

## Configuration

Create `config.json` in the repository root. The workflow expects the following structure:

```json
{
  "FILE_NAMES": {
    "WBD": "<path_or_filename_for_watershed_boundary_dataset>",
    "FIRES": "<path_or_filename_for_fire_perimeters>",
    "ECO": "<path_or_filename_for_ecoregions>"
  }
}
```

## Workflow order

Run scripts from the repository root in this order:

```bash
python 00_setup_directories.py
python 01_make_burn_area_matrix.py
python 02_make_water_yield_data.py
python 03_make_time_series_data.py
python 04_statistical_analysis.py
python make_figure_2.py
python make_figure_3.py
python make_figure_4.py
python make_figure_5.py
python make_figure_6.py
```

## Script descriptions

| Script | Purpose | Main outputs |
|---|---|---|
| `00_setup_directories.py` | Creates `Assets/`, `Assets/Shapes/`, `Assets/Tables/`, `Assets/Results/`, and `Figures/` | Directory scaffold |
| `01_make_burn_area_matrix.py` | Intersects Western HUC12 watersheds, fire perimeters, and ecoregions | `Assets/Tables/W11_BURN_AREA_MATRIX_5070.csv` |
| `02_make_water_yield_data.py` | Extracts ERA5 runoff and precipitation points to HUC12 watersheds | `Assets/Tables/W11_HUC12_Runoff.csv`; `Assets/Tables/W11_HUC12_Precip.csv` |
| `03_make_time_series_data.py` | Builds annual HUC12 burn-area, runoff, precipitation, and downstream-consumer tables | `HUC12_Annual_BAP_CONSUMERS_5070.csv`; `HUC12_Annual_BAP_RO_TP_5070.csv` |
| `04_statistical_analysis.py` | Produces burn-area, ecoregion, water-yield, runoff-ratio, and downstream-population trend results | Result CSVs in `Assets/Results/` |
| `make_figure_2.py` | Generates runoff-ratio percentile heatmap figure | `Figures/RO_TP_BAP_HEATMAP_5070_2.png` |
| `make_figure_3.py` | Generates split violin plots for runoff ratio by burn-area interval and changepoint period | `Figures/SPLIT_VIOLIN.png` |
| `make_figure_4.py` | Generates ecoregion geography figure | `Figures/ECO_GEO.png` |
| `make_figure_5.py` | Generates downstream-consumer burn-area time-series figure | `Figures/CONSUMERS_TS.png` |
| `make_figure_6.py` | Generates downstream-consumer geography/change-class figure | `Figures/POP_DS_GEO_CHANGE_CLASS` |

## Environment-manager compatibility

This repository uses a plain `requirements.txt` so users can install dependencies with their preferred environment manager. Examples:

```bash
python -m pip install -r requirements.txt
uv pip install -r requirements.txt
conda create -n wildfire-regimes-w11 python=3.11
conda activate wildfire-regimes-w11
python -m pip install -r requirements.txt
```

For strict archival reproducibility, create and publish a lock file from the environment used for final manuscript figures, such as `pip freeze > requirements-lock.txt`, `conda env export > environment-lock.yml`, or `uv pip compile requirements.txt -o requirements-lock.txt`. Keep `requirements.txt` as the portable input specification and use the lock file as the exact provenance snapshot.

## Reproducibility notes

- Coordinate reference systems are handled explicitly in scripts. Burn-area calculations use projected CRS EPSG:5070.
- ERA5 runoff and precipitation are converted from meters to millimeters in `03_make_time_series_data.py`.
- Burn-area percentage is calculated as `BurnAreaEco / huc12_sqkm * 100`.
- Burn-area intervals used across scripts are: `<1%`, `1-9.99%`, `10-19.99%`, `20-49.99%`, `50-99.99%`, and `>=100%`.
- Runoff, precipitation, and runoff-ratio percentile groups use ordered quantile classes: `20th`, `40th`, `60th`, `80th`, and `99th`.
- Several figure scripts depend on statistical result tables generated by `04_statistical_analysis.py`; rerun the full workflow after changing input data or statistical methods.

## Validation checklist before publication

Before archiving or submitting this repository, verify that:

- `requirements.txt` installs successfully in a clean Python environment.
- `utils/stat.py`, `utils/matplot.py`, and any retained optional helper modules are included.
- All scripts can be run from a clean clone using the documented workflow order.
- Figure outputs match manuscript figure names and captions.
- Statistical result CSVs match manuscript tables and supplementary tables.
- Any hard-coded changepoints, years, thresholds, or filters are documented and traceable to result tables or manuscript methods.

## Citation

If using or adapting this code, cite the associated manuscript and any original data sources
