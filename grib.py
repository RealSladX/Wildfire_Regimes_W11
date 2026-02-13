import xarray as xr
import os
import geopandas as gpd
import dask_geopandas
import time

project_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DATA")
ds = xr.open_dataset(
    f"{data_path}/ERA5.grib",
    engine="cfgrib",
    backend_kwargs={"filter_by_keys": {"shortName": "e"}},
)
for v in ds:
    print("{}, {}, {}".format(v, ds[v].attrs["long_name"], ds[v].attrs["units"]))

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/Raw_Runoff")):
    ds = xr.open_dataset(
        f"{data_path}/ERA5.grib",
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"shortName": "ro"}},
    )
    ro = ds.get("ro")

    df = ro.to_dataframe()
    df["latitude"] = df.index.get_level_values("latitude")
    df["longitude"] = df.index.get_level_values("longitude")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df.index.get_level_values("longitude"),
            df.index.get_level_values("latitude"),
        ),
        crs="EPSG:4326",
    )
    gdf[["valid_time", "ro", "geometry"]].to_file("./Assets/Shapes/Raw_Runoff")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/Raw_Precip")):
    ds = xr.open_dataset(
        f"{data_path}/ERA5.grib",
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"shortName": "tp"}},
    )
    tp = ds.get("tp")

    df = tp.to_dataframe()
    df["latitude"] = df.index.get_level_values("latitude")
    df["longitude"] = df.index.get_level_values("longitude")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df.index.get_level_values("longitude"),
            df.index.get_level_values("latitude"),
        ),
        crs="EPSG:4326",
    )
    gdf[["valid_time", "tp", "geometry"]].to_file("./Assets/Shapes/Raw_Precip")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/Raw_Evap")):
    ds = xr.open_dataset(
        f"{data_path}/ERA5.grib",
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"shortName": "e"}},
    )
    ev = ds.get("e")

    df = ev.to_dataframe()
    df["latitude"] = df.index.get_level_values("latitude")
    df["longitude"] = df.index.get_level_values("longitude")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df.index.get_level_values("longitude"),
            df.index.get_level_values("latitude"),
        ),
        crs="EPSG:4326",
    )
    gdf[["valid_time", "e", "geometry"]].to_file("./Assets/Shapes/Raw_Evap")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/Raw_Evap")):
    ds = xr.open_dataset(
        f"{data_path}/ERA5.grib",
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"shortName": "e"}},
    )
    ev = ds.get("e")

    df = ev.to_dataframe()
    df["latitude"] = df.index.get_level_values("latitude")
    df["longitude"] = df.index.get_level_values("longitude")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df.index.get_level_values("longitude"),
            df.index.get_level_values("latitude"),
        ),
        crs="EPSG:4326",
    )
    gdf[["valid_time", "e", "geometry"]].to_file("./Assets/Shapes/Raw_Evap")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/Raw_PEV")):
    ds = xr.open_dataset(
        f"{data_path}/ERA5.grib",
        engine="cfgrib",
        backend_kwargs={"filter_by_keys": {"shortName": "pev"}},
    )
    pev = ds.get("pev")

    df = pev.to_dataframe()
    df["latitude"] = df.index.get_level_values("latitude")
    df["longitude"] = df.index.get_level_values("longitude")
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df.index.get_level_values("longitude"),
            df.index.get_level_values("latitude"),
        ),
        crs="EPSG:4326",
    )
    gdf[["valid_time", "pev", "geometry"]].to_file("./Assets/Shapes/Raw_PEV")


if not os.path.exists(os.path.join(project_path, "Assets/Shapes/W11_HUC12_Runoff.csv")):
    start = time.time()
    huc12 = gpd.read_file(os.path.join(project_path, "Assets/Shapes/W11_HUC12")).to_crs(
        epsg=4326
    )[["huc12", "geometry"]]
    ro = gpd.read_file(os.path.join(project_path, "Assets/Shapes/Raw_Runoff"))
    ro = ro.drop(columns=["time", "latitude", "longitude"])

    ddf = dask_geopandas.from_geopandas(ro, npartitions=8)
    ddf2 = dask_geopandas.from_geopandas(huc12, npartitions=8)
    ddf3 = ddf2.sjoin(ddf)
    ddf3 = ddf3.drop(columns="geometry")
    ddf3.to_csv(
        os.path.join(project_path, "Assets/Shapes/W11_HUC12_Runoff.csv"),
        single_file=True,
    )
    print(f"{time.time() - start:.2f}")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/W11_HUC12_Precip.csv")):
    start = time.time()
    huc12 = gpd.read_file(os.path.join(project_path, "Assets/Shapes/W11_HUC12")).to_crs(
        epsg=4326
    )[["huc12", "geometry"]]
    tp = gpd.read_file(os.path.join(project_path, "Assets/Shapes/Raw_Precip"))
    tp = tp.drop(columns=["time", "latitude", "longitude"])

    ddf = dask_geopandas.from_geopandas(tp, npartitions=8)
    ddf2 = dask_geopandas.from_geopandas(huc12, npartitions=8)
    ddf3 = ddf2.sjoin(ddf)
    ddf3 = ddf3.drop(columns="geometry")
    ddf3.to_csv(
        os.path.join(project_path, "Assets/Shapes/W11_HUC12_Precip.csv"),
        single_file=True,
    )
    print(f"{time.time() - start:.2f}")


if not os.path.exists(os.path.join(project_path, "Assets/Shapes/W11_HUC12_Evap.csv")):
    start = time.time()
    huc12 = gpd.read_file(os.path.join(project_path, "Assets/Shapes/W11_HUC12")).to_crs(
        epsg=4326
    )[["huc12", "geometry"]]
    ev = gpd.read_file(os.path.join(project_path, "Assets/Shapes/Raw_Evap"))
    ev = ev.drop(columns=["time", "latitude", "longitude"])

    ddf = dask_geopandas.from_geopandas(ev, npartitions=8)
    ddf2 = dask_geopandas.from_geopandas(huc12, npartitions=8)
    ddf3 = ddf2.sjoin(ddf)
    ddf3 = ddf3.drop(columns="geometry")
    ddf3.to_csv(
        os.path.join(project_path, "Assets/Shapes/W11_HUC12_Evap.csv"), single_file=True
    )
    print(f"{time.time() - start:.2f}")

if not os.path.exists(os.path.join(project_path, "Assets/Shapes/W11_HUC12_PEV.csv")):
    start = time.time()
    huc12 = gpd.read_file(os.path.join(project_path, "Assets/Shapes/W11_HUC12")).to_crs(
        epsg=4326
    )[["huc12", "geometry"]]
    pev = gpd.read_file(os.path.join(project_path, "Assets/Shapes/Raw_PEV"))
    pev = pev.drop(columns=["time", "latitude", "longitude"])

    ddf = dask_geopandas.from_geopandas(pev, npartitions=8)
    ddf2 = dask_geopandas.from_geopandas(huc12, npartitions=8)
    ddf3 = ddf2.sjoin(ddf)
    ddf3 = ddf3.drop(columns="geometry")
    ddf3.to_csv(
        os.path.join(project_path, "Assets/Shapes/W11_HUC12_PEV.csv"), single_file=True
    )
    print(f"{time.time() - start:.2f}")
