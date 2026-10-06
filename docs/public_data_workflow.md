# Public / Customer Geophysical Data Workflow

The v0.7 architecture deliberately separates **data ingestion** from **data redistribution**. This lets a customer use licensed, classified, proprietary, or public map products without those datasets being bundled into the open repository.

Recommended workflow:

1. Acquire a gravity, gravity-gradient, magnetic-anomaly, bathymetric, or terrain-derived product from an authoritative source.
2. Record the source, datum, coordinate reference system, units, resolution, epoch, and license.
3. Convert or export the product to a regular geodetic grid.
4. Load it with `GeoGridMap`.
5. Define a local navigation reference origin.
6. Validate interpolation and units independently.
7. Run Monte Carlo navigation studies with realistic sensor and map uncertainties.
8. Preserve the source metadata in the generated engineering report.

The suite does not assume that two maps with the same numeric units are equivalent. Operational studies should document map provenance and uncertainty explicitly.
