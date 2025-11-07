# Dasymetric Poverty Mapping — Zamboanga City (2024)

Short project README distilled from `workflow_methodology.html`.

Overview
- Purpose: produce high-resolution (grid-level) poverty estimates for Zamboanga City by combining barangay-level socioeconomic data with satellite-derived geospatial features and machine learning (dasymetric mapping).
- Approach: generate a regular 1 km × 1 km grid, extract multi-source features (Sentinel-2 indices and texture, nighttime lights, population, OSM-derived accessibility), apply geography-aware imputation, use fractional (area-weighted) assignment to create barangay-level training samples, train a Random Forest regressor, and predict fine-scale poverty estimates.

Key outputs (not included in this repository — see Data & Exclusions)
- Grid-level predictions and validation CSVs
- Engineered feature CSVs and GeoJSONs
- Plots for validation and feature importance

How the workflow is organized
- `dataprep/` — notebooks and scripts for preparing inputs (satellite export, feature engineering, spatial imputation, road/POI processing).
- `assets/` — generated data exports, shapefiles, rasters, and CSVs (excluded from git by default; see Data & Exclusions).
- `notebooks/` — exploratory analysis and ad-hoc visualizations.

Data & Exclusions (important)
- This repository intentionally excludes large data files and generated artifacts to keep the git history small:
  - `assets/` and `data/` directories are ignored and should be stored separately.
  - Generated analysis artifacts excluded: `assets_unused.json`, `file_metadata.tsv`, `file_usage_counts.tsv`, `searchable_files.txt`, `unused_deprecated_report.json`, and `workflow_methodology.html`.
- To reproduce results you must obtain the following inputs (not included here):
  - Sentinel-2 composite (2024) covering Zamboanga City
  - Population rasters (e.g., WorldPop)
  - OSM extracts for roads/POIs or local OSM export
  - Barangay-level socioeconomic/census data (used for training/validation)

Quickstart (developer machine)
1. Prepare a Python environment (recommended: Python 3.10+). Example dependencies:
   - pandas, numpy, geopandas, rasterio, rtree, shapely, scikit-learn, scikit-image, matplotlib
2. Place data under `assets/` and `data/` (per the structure expected by the notebooks).
3. Open and run the notebooks in `dataprep/` in the following order:
   - `sentinel2Export.ipynb` (if you need to generate/prepare imagery)
   - `geospatialPrep.ipynb` (create grid, extract zonal stats)
   - `featureEngineering.ipynb` (compute indices, GLCM, spatial lag)
   - `dasymetricMapping.ipynb` (fractional assignment, train model, predict)

  CatBoost methodology (new)
  - We added a CatBoost-based regression model notebook (`notebooks/catBoostDasymetric.ipynb`) that mirrors the Random Forest pipeline but leverages CatBoost’s gradient-boosted decision trees, which:
    - handle categorical features natively (if present),
    - are robust on heterogeneous/tabular datasets,
    - often deliver strong accuracy with minimal preprocessing.

  How to run the CatBoost notebook
  1. Install dependencies: `pip install -r requirements.txt` (CatBoost is included as a dependency).
  2. Ensure required inputs are present under `assets/` (ignored in git) in the same structure used by the Random Forest notebook.
  3. Open `notebooks/catBoostDasymetric.ipynb` and run all cells. The notebook will:
     - perform dataset validation and preprocessing,
     - train CatBoost with cross-validation,
     - save tabular outputs (CSV) to `output/catBoost/data/`,
     - save visualizations (PNG) to `output/catBoost/visualizations/`,
     - copy Random Forest outputs for comparison into `output/catBoost/randomForest_outputs/` and produce a `randomForest_output_list.md` describing them.

  Output directory layout (updated)
  ```
  output/
    catBoost/
      data/                # CSV: metrics, feature importances, predictions, CV results
      visualizations/      # PNG: feature importance, residuals, predicted vs actual plots
      randomForest_outputs/
        randomForest_output_list.md  # Markdown listing RF outputs with brief descriptions
        ... (copied RF outputs for comparison)
  ```

  Comparison with Random Forest outputs
  - The CatBoost notebook automatically compiles a list of Random Forest outputs for side-by-side inspection. These are copied into `output/catBoost/randomForest_outputs/` to simplify comparisons during review.

Reproducibility notes
- Fractional assignment: grid cells contribute to overlapping barangays by area-weighted fractions to avoid losing information from small administrative units.
- Geography-aware imputation: DBSCAN zoning and zone-specific rules reduce bias from missing OSM-derived features.
- Model: Random Forest regression with 5-fold CV. Hyperparameters and training details are in `dataprep/dasymetricMapping.ipynb`.

License & contact
- This repo contains code and documentation. Data used may be subject to third-party licenses (e.g., Sentinel-2, WorldPop, OSM). Check each data source's license before redistribution.
- If you need help reproducing the analysis or would like me to push data handling scripts for secure archival, reply with the preferred remote storage (S3, GDrive, etc.).

Files explicitly excluded from commits
```
assets_unused.json
file_metadata.tsv
file_usage_counts.tsv
searchable_files.txt
unused_deprecated_report.json
workflow_methodology.html
```
