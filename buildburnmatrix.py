import json
import os
from geopandas import read_file, GeoDataFrame
from pandas import concat
import dask_geopandas
import time

num_par = 8
fire_year_start = 1940
fire_year_end = 2025


project_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(project_path, "config.json")
with open(config_path, "r") as f:
    config = json.load(f)
data_path = os.path.join(project_path, "DATA")
assets_path = os.path.join(project_path, "Assets")
shapes_path = os.path.join(assets_path, "Shapes")
W11 = ["CA", "OR", "WA", "ID", "MT", "NV", "AZ", "NM", "CO", "WY", "UT"]


def custom_overlay(left, right):
    return (
        left.sjoin(right.assign(right_geometry=right.geometry))
        .assign(geometry=lambda x: x.geometry.intersection(x.right_geometry))
        .drop(columns=["right_geometry", "index_right"])
    )


def meta_info(df: GeoDataFrame):
    print(df.dtypes)
    print(len(df))
    print(type(df))
    print(df.columns)
    print(df.head())


if not os.path.exists(os.path.join(shapes_path, "W11_HUC12")):
    start = time.time()
    print("Getting W11 Watersheds")
    wbd = read_file(os.path.join(data_path, config["FILE_NAMES"]["WBD"]), layer=5)[
        ["huc12", "areasqkm", "states", "name", "geometry"]
    ]
    wbd = wbd.rename(columns={"areasqkm": "huc12_sqkm", "name": "huc12_name"})
    wbd = wbd.dropna(subset=["states"])
    study_area = []
    for state in W11:
        s = wbd[wbd["states"].str.contains(state)]
        study_area.append(s)
    study_area = concat(study_area)
    study_area.to_file(os.path.join(shapes_path, "W11_HUC12"))
    print(time.time() - start)


wbd = read_file(os.path.join(shapes_path, "W11_HUC12"))
wbd = wbd.drop(columns=["huc12_name", "states"])
wbd = dask_geopandas.from_geopandas(wbd, npartitions=num_par)
fires = read_file(os.path.join(data_path, config["FILE_NAMES"]["FIRES"]))[
    ["FIRE_YEAR_INT", "INCIDENT", "geometry"]
]
fires = fires[fires["FIRE_YEAR_INT"] >= fire_year_start]
fires = fires[fires["FIRE_YEAR_INT"] < fire_year_end]
fires = dask_geopandas.from_geopandas(fires, npartitions=num_par)
eco = read_file(os.path.join(data_path, config["FILE_NAMES"]["ECO"]))[
    ["NA_L1NAME", "NA_L2NAME", "US_L3NAME", "geometry"]
]
eco = dask_geopandas.from_geopandas(eco, npartitions=num_par)


if not os.path.exists(os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_3857")):
    start = time.time()
    print("BUILDING BURN AREA MATRIX")
    print("EPSG: 3857")
    wbd = wbd.to_crs(epsg=3857)
    fires = fires.to_crs(epsg=3857)
    eco = eco.to_crs(epsg=3857)
    bam = custom_overlay(wbd, fires)
    bam = bam.set_geometry("geometry")
    bam["BurnArea"] = bam["geometry"].area / (10**6)
    bam = custom_overlay(bam, eco)
    bam = bam.set_geometry("geometry")
    bam["BurnAreaEco"] = bam["geometry"].area / (10**6)
    bam = bam.drop(columns=["geometry"])
    bam.to_csv(
        os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_3857.csv"), single_file=True
    )
    print("\n", time.time() - start)


if not os.path.exists(os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_5070")):
    start = time.time()
    print("BUILDING BURN AREA MATRIX")
    print("EPSG: 5070")
    wbd = wbd.to_crs(epsg=5070)
    fires = fires.to_crs(epsg=5070)
    eco = eco.to_crs(epsg=5070)
    bam = custom_overlay(wbd, fires)
    bam = bam.set_geometry("geometry")
    bam["BurnArea"] = bam["geometry"].area / (10**6)
    bam = custom_overlay(bam, eco)
    bam = bam.set_geometry("geometry")
    bam["BurnAreaEco"] = bam["geometry"].area / (10**6)
    bam = bam.drop(columns=["geometry"])
    bam.to_csv(
        os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_5070.csv"), single_file=True
    )
    print("\n", time.time() - start)

if not os.path.exists(os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_9822")):
    start = time.time()
    print("BUILDING BURN AREA MATRIX")
    print("EPSG: 9822")
    wbd = wbd.to_crs(epsg=9822)
    fires = fires.to_crs(epsg=9822)
    eco = eco.to_crs(epsg=9822)
    bam = custom_overlay(wbd, fires)
    bam = bam.set_geometry("geometry")
    bam["BurnArea"] = bam["geometry"].area / (10**6)
    bam = custom_overlay(bam, eco)
    bam = bam.set_geometry("geometry")
    bam["BurnAreaEco"] = bam["geometry"].area / (10**6)
    bam = bam.drop(columns=["geometry"])
    bam.to_csv(
        os.path.join(shapes_path, "W11_BURN_AREA_MATRIX_9822.csv"), single_file=True
    )
    print("\n", time.time() - start)
