# Dasymetric Poverty Mapping Methodology
## Zamboanga City, Philippines (2024)

---

## 1. Overview

This project implements a **machine learning-based dasymetric mapping** approach to disaggregate poverty estimates from coarse administrative units (barangays) to a fine spatial resolution (1km² grid cells) in Zamboanga City, Philippines. The methodology combines multi-source geospatial data with supervised learning algorithms to produce high-resolution poverty maps that better capture spatial heterogeneity than traditional choropleth mapping.

### Core Approach

**Dasymetric mapping** is a cartographic technique that uses ancillary data to refine the spatial distribution of phenomena, moving beyond the assumption of uniform density within administrative boundaries (Mennis, 2003)[^1]. Our implementation uses machine learning to learn the relationship between poverty rates and diverse geospatial features, enabling predictions at a resolution that supports more targeted interventions.

### Justification

- **Jean et al. (2016)**[^2] demonstrated that satellite imagery combined with machine learning can accurately predict poverty in data-sparse regions, establishing a paradigm shift in poverty estimation methodologies.
- **Yeh et al. (2020)**[^3] validated that deep learning on satellite data can achieve performance comparable to traditional survey methods while being more scalable and frequently updatable.
- **Stevens et al. (2015)**[^4] showed that dasymetric approaches significantly reduce spatial uncertainty in population and socioeconomic estimates compared to areal weighting methods.

---

## 2. Data Sources & Feature Engineering

### 2.1 Satellite-Derived Features

#### **Spectral Indices**

**NDVI (Normalized Difference Vegetation Index)**
- Formula: `(NIR - Red) / (NIR + Red)`
- **Justification**: NDVI is a robust indicator of vegetation health and land cover. Urban poverty is often associated with less vegetation cover, while rural poverty may show distinct agricultural patterns (Duque et al., 2015)[^5].

**NDBI (Normalized Difference Built-up Index)**
- Formula: `(SWIR - NIR) / (SWIR + NIR)`
- **Justification**: NDBI effectively highlights built-up areas and urban density, which correlate with economic activity and infrastructure development (Zha et al., 2003)[^6].

**Data Source**: Sentinel-2 (10m resolution), 2024 composite

#### **Texture Features (GLCM)**

We extracted Gray-Level Co-occurrence Matrix (GLCM) texture features from both NIR and Red bands:

- **Contrast**: Measures local variations in intensity
- **Dissimilarity**: Similar to contrast but with linear weighting
- **Homogeneity**: Measures closeness of distribution to diagonal
- **Energy/ASM**: Uniformity of gray-level distribution
- **Correlation**: Linear dependency of gray levels

**Justification**: 
- **Haralick et al. (1973)**[^7] introduced GLCM as a fundamental method for texture analysis in image processing.
- **Kuffer et al. (2016)**[^8] demonstrated that texture features from VHR imagery effectively distinguish between formal and informal settlements, with informal settlements (often associated with poverty) exhibiting distinct textural patterns.
- **Duque et al. (2015)**[^5] showed that spatial texture metrics improve poverty prediction accuracy by capturing neighborhood-level built environment characteristics.

**Implementation**: We computed GLCM with distance=1 and angles=[0°, 45°, 90°, 135°], then averaged across directions for rotation invariance.

### 2.2 Nighttime Lights

**Data Source**: VIIRS Day/Night Band (DNB)

**Justification**:
- **Elvidge et al. (2009)**[^9] established nighttime lights as a proxy for economic activity and electricity access.
- **Jean et al. (2016)**[^2] used nighttime lights as a transfer learning target, showing strong correlation with economic development.
- **Henderson et al. (2012)**[^10] demonstrated that nighttime lights explain ~30% of cross-country variation in GDP.

**Preprocessing**: We extracted mean radiance values within each grid cell and applied log transformation to normalize the highly skewed distribution.

### 2.3 Population Data

**Data Source**: WorldPop 2024 (100m resolution)

**Justification**: Population density provides baseline context for human presence and is strongly associated with poverty patterns in urban environments (Tatem, 2017)[^11].

### 2.4 Infrastructure & Accessibility

**Road Accessibility**: Euclidean distance to nearest road
**POI Accessibility**: Euclidean distance to nearest Point of Interest (schools, markets, health facilities)

**Data Source**: OpenStreetMap (OSM)

**Justification**:
- **Weiss et al. (2018)**[^12] showed that accessibility metrics derived from road networks are strong predictors of health and socioeconomic outcomes.
- **Steele et al. (2017)**[^13] demonstrated that distance to services correlates with poverty, as marginalized populations often reside in areas with poor infrastructure access.

### 2.5 Topographic Features

**Elevation & Slope**: Derived from SRTM 30m DEM

**Justification**: Topography influences construction costs, agricultural productivity, and vulnerability to natural hazards, all factors that correlate with poverty (Minot et al., 2006)[^14].

### 2.6 Climate Variables

**Precipitation**: CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)
**Surface Temperature**: MODIS Land Surface Temperature

**Justification**: Climate variables affect agricultural livelihoods and health outcomes, particularly in rural contexts where poverty is intertwined with environmental vulnerability (Hallegatte et al., 2016)[^15].

### 2.7 Socioeconomic Census Data

Barangay-level indicators from Philippine Statistics Authority (PSA):
- Educational attainment percentages
- Employment types and sectors
- House construction materials (roof, walls)
- Water and electricity access
- Household structure

**Justification**: These variables provide ground-truth socioeconomic context and serve as the target variable source (poverty rate) for model training.

---

## 3. Spatial Imputation Strategy

### Challenge

OpenStreetMap-derived accessibility features exhibited significant missingness in three distinct geographic zones:
1. **Protected forest/watershed areas** (no roads or POIs by regulation)
2. **Offshore islands** (incomplete OSM coverage)
3. **Remote rural mainland areas** (sparse mapping)

Simple imputation (mean/median) would introduce systematic bias by ignoring geographic context.

### Solution: Multi-Stage Geography-Aware Imputation

#### **Stage 1: Zone Identification via DBSCAN Clustering**

We applied DBSCAN (Density-Based Spatial Clustering) on grid cell coordinates and NDVI values to identify distinct geographic zones.

**Justification**:
- **Ester et al. (1996)**[^16] introduced DBSCAN as a robust clustering method that handles irregular spatial patterns and doesn't require pre-specifying cluster count.
- This approach respects **Tobler's First Law of Geography**: "Everything is related to everything else, but near things are more related than distant things" (Tobler, 1970)[^17].

#### **Stage 2: Rule-Based Imputation for Special Zones**

- **Protected Forest**: Imputed accessibility to 0 (no infrastructure by design)
- **Islands**: Imputed using island-specific mean (prevents mainland data leakage)

**Justification**: These zones have known characteristics that justify deterministic imputation rather than statistical inference.

#### **Stage 3: Spatial KNN Imputation**

For the mainland, we applied k-Nearest Neighbors imputation using spatial coordinates (longitude, latitude) as the feature space.

**Formula**: 
```
imputed_value = Σ(w_i * value_i) / Σ(w_i)
where w_i = 1 / distance_i²
```

**Justification**:
- **Li & Heap (2008)**[^18] showed that spatial interpolation methods outperform non-spatial imputation for geographic data.
- **Inverse distance weighting** leverages spatial autocorrelation: closer neighbors provide more relevant information (Shepard, 1968)[^19].

**Parameters**: k=5 neighbors, Euclidean distance metric

---

## 4. Dasymetric Disaggregation Approach

### Fractional Assignment

Traditional dasymetric methods assign grid cells to a single administrative unit. We use **fractional assignment** where grid cells contribute to all overlapping barangays weighted by intersection area.

**Formula**:
```
grid_poverty_contribution_to_barangay_j = Σ(poverty_rate_predicted_i * area_overlap_ij / area_barangay_j)
```

**Justification**:
- **Mennis & Hultgren (2006)**[^20] showed that area-weighted aggregation preserves mass balance and reduces edge effects in dasymetric mapping.
- This approach ensures that predictions aggregate correctly to match known barangay-level statistics.

---

## 5. Machine Learning Models

### 5.1 Random Forest Regressor

**Architecture**: Ensemble of 100 decision trees with bootstrap aggregating

**Hyperparameters**:
- `n_estimators`: 100
- `max_depth`: 15
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `max_features`: 'sqrt'

**Justification**:
- **Breiman (2001)**[^21] introduced Random Forests, which are robust to outliers, handle non-linear relationships, and provide feature importance metrics.
- **Hengl et al. (2018)**[^22] demonstrated that Random Forest is highly effective for spatial prediction tasks with mixed predictors.

**Validation**: 5-fold cross-validation with spatial blocking to prevent information leakage (Roberts et al., 2017)[^23].

### 5.2 CatBoost Regressor

**Architecture**: Gradient boosting on decision trees with ordered boosting and symmetric trees

**Hyperparameters**:
- `iterations`: 1000
- `learning_rate`: 0.05
- `depth`: 6
- `l2_leaf_reg`: 3

**Justification**:
- **Prokhorenkova et al. (2018)**[^24] introduced CatBoost, which includes built-in mechanisms to handle categorical features and prevent overfitting through ordered boosting.
- Gradient boosting often outperforms Random Forest on tabular data (Dorogush et al., 2018)[^25].

**Validation**: Same spatial CV strategy as Random Forest for fair comparison.

---

## 6. Model Evaluation

### Metrics

- **R² (Coefficient of Determination)**: Proportion of variance explained
- **RMSE (Root Mean Squared Error)**: Penalizes large errors
- **MAE (Mean Absolute Error)**: Average absolute deviation

### Multi-Scale Validation

1. **Grid-level** (1km²): Direct prediction accuracy
2. **Barangay-level**: Aggregated predictions vs. actual barangay statistics

**Justification**: Multi-scale validation ensures that disaggregated predictions are locally accurate while maintaining consistency with administrative aggregates (Openshaw, 1984)[^26].

---

## 7. Limitations & Future Work

### Current Limitations

1. **Temporal**: Single time point (2024); cannot capture poverty dynamics
2. **Validation data**: Limited to barangays with survey coverage
3. **OSM completeness**: Varies spatially, particularly in rural areas
4. **Causality**: Model captures correlations, not causal mechanisms

### Future Directions

1. **Temporal analysis**: Incorporate multi-year data to track changes
2. **Additional features**: 
   - Social media activity (Blumenstock et al., 2015)[^27]
   - Mobile phone data (CDR) where privacy-compliant
   - SAR imagery for cloud-free monitoring
3. **Ensemble methods**: Combine Random Forest and CatBoost predictions
4. **Uncertainty quantification**: Implement conformal prediction intervals
5. **Causal inference**: Use instrumental variables or quasi-experiments to identify poverty drivers

---

## References

[^1]: Mennis, J. (2003). Generating surface models of population using dasymetric mapping. *The Professional Geographer*, 55(1), 31-42.

[^2]: Jean, N., Burke, M., Xie, M., Davis, W. M., Lobell, D. B., & Ermon, S. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790-794.

[^3]: Yeh, C., Perez, A., Driscoll, A., Azzari, G., Tang, Z., Lobell, D., ... & Burke, M. (2020). Using publicly available satellite imagery and deep learning to understand economic well-being in Africa. *Nature Communications*, 11(1), 2583.

[^4]: Stevens, F. R., Gaughan, A. E., Linard, C., & Tatem, A. J. (2015). Disaggregating census data for population mapping using random forests with remotely-sensed and ancillary data. *PLOS ONE*, 10(2), e0107042.

[^5]: Duque, J. C., Patino, J. E., Ruiz, L. A., & Pardo-Pascual, J. E. (2015). Measuring intra-urban poverty using land cover and texture metrics derived from remote sensing data. *Landscape and Urban Planning*, 135, 11-21.

[^6]: Zha, Y., Gao, J., & Ni, S. (2003). Use of normalized difference built-up index in automatically mapping urban areas from TM imagery. *International Journal of Remote Sensing*, 24(3), 583-594.

[^7]: Haralick, R. M., Shanmugam, K., & Dinstein, I. H. (1973). Textural features for image classification. *IEEE Transactions on Systems, Man, and Cybernetics*, (6), 610-621.

[^8]: Kuffer, M., Pfeffer, K., & Sliuzas, R. (2016). Slums from space—15 years of slum mapping using remote sensing. *Remote Sensing*, 8(6), 455.

[^9]: Elvidge, C. D., Sutton, P. C., Ghosh, T., Tuttle, B. T., Baugh, K. E., Bhaduri, B., & Bright, E. (2009). A global poverty map derived from satellite data. *Computers & Geosciences*, 35(8), 1652-1660.

[^10]: Henderson, J. V., Storeygard, A., & Weil, D. N. (2012). Measuring economic growth from outer space. *American Economic Review*, 102(2), 994-1028.

[^11]: Tatem, A. J. (2017). WorldPop, open data for spatial demography. *Scientific Data*, 4(1), 170004.

[^12]: Weiss, D. J., et al. (2018). A global map of travel time to cities to assess inequalities in accessibility in 2015. *Nature*, 553(7688), 333-336.

[^13]: Steele, J. E., et al. (2017). Mapping poverty using mobile phone and satellite data. *Journal of the Royal Society Interface*, 14(127), 20160690.

[^14]: Minot, N., Baulch, B., & Epprecht, M. (2006). Poverty and inequality in Vietnam: Spatial patterns and geographic determinants. *International Food Policy Research Institute* (IFPRI).

[^15]: Hallegatte, S., et al. (2016). Shock waves: managing the impacts of climate change on poverty. *World Bank Publications*.

[^16]: Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Kdd*, 96(34), 226-231.

[^17]: Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region. *Economic Geography*, 46(sup1), 234-240.

[^18]: Li, J., & Heap, A. D. (2008). A review of spatial interpolation methods for environmental scientists. *Geoscience Australia*, 68.

[^19]: Shepard, D. (1968). A two-dimensional interpolation function for irregularly-spaced data. *Proceedings of the 1968 23rd ACM National Conference*, 517-524.

[^20]: Mennis, J., & Hultgren, T. (2006). Intelligent dasymetric mapping and its application to areal interpolation. *Cartography and Geographic Information Science*, 33(3), 179-194.

[^21]: Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5-32.

[^22]: Hengl, T., et al. (2018). Random forest as a generic framework for predictive modeling of spatial and spatio-temporal variables. *PeerJ*, 6, e5518.

[^23]: Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40(8), 913-929.

[^24]: Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018). CatBoost: unbiased boosting with categorical features. *Advances in Neural Information Processing Systems*, 31.

[^25]: Dorogush, A. V., Ershov, V., & Gulin, A. (2018). CatBoost: gradient boosting with categorical features support. *arXiv preprint arXiv:1810.11363*.

[^26]: Openshaw, S. (1984). *The modifiable areal unit problem*. Geo Books.

[^27]: Blumenstock, J., Cadamuro, G., & On, R. (2015). Predicting poverty and wealth from mobile phone metadata. *Science*, 350(6264), 1073-1076.

---

## Citation

If you use this methodology or codebase, please cite:

```
[Your Name]. (2024). Dasymetric Poverty Mapping of Zamboanga City using Machine Learning 
and Multi-Source Geospatial Data. GitHub repository: https://github.com/regulus-j/povertyMap
```

---

**Last Updated**: November 8, 2025  
**Version**: 1.0  
**Contact**: [Your Email]
