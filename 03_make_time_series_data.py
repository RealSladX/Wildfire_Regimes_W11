import os
import utils.stat as stat

project_path = os.path.dirname(os.path.abspath(__file__))
tables_path = os.path.join(project_path, "Assets/Tables")
if not os.path.exists(os.path.join(tables_path, "HUC12_Average_Monthly_Runoff.csv")):
    ro = stat.read_file(os.path.join(tables_path, "W11_HUC12_Runoff.csv"))
    ro = ro.astype({"ro": "float"})
    ro["ro"] = ro["ro"] * 1000
    ro["Year"] = ro["valid_time"].str[:4]
    avg = ro[["Year", "huc12", "ro"]].groupby(["Year", "huc12"]).mean()
    avg.to_csv(os.path.join(tables_path, "HUC12_Average_Monthly_Runoff.csv"))


if not os.path.exists(os.path.join(tables_path, "HUC12_Average_Monthly_Precip.csv")):
    ro = stat.read_file(os.path.join(tables_path, "W11_HUC12_Precip.csv"))
    ro = ro.astype({"tp": "float"})
    ro["tp"] = ro["tp"] * 1000
    ro["Year"] = ro["valid_time"].str[:4]
    avg = ro[["Year", "huc12", "tp"]].groupby(["Year", "huc12"]).mean()
    avg.to_csv(os.path.join(tables_path, "HUC12_Average_Monthly_Precip.csv"))


ro_all = stat.load_asset(os.path.join(tables_path, "HUC12_Average_Monthly_Runoff.csv"))
tp_all = stat.load_asset(os.path.join(tables_path, "HUC12_Average_Monthly_Precip.csv"))
epsgs = ["5070"]
for epsg in epsgs:
    print(epsg)
    fire_eco_all = stat.load_asset(
        os.path.join(tables_path, f"W11_BURN_AREA_MATRIX_{epsg}.csv")
    )
    fire_eco_all["FIRE_YEAR_INT"] = fire_eco_all["FIRE_YEAR_INT"].astype(float).round(0)
    fire_eco_all["FIRE_YEAR_INT"] = fire_eco_all["FIRE_YEAR_INT"].astype(int)
    fire_eco_all["huc12_sqkm"] = fire_eco_all["huc12_sqkm"].astype(float)
    fire_eco_all["BurnAreaEco"] = fire_eco_all["BurnAreaEco"].astype(float)

    annual_bap = (
        fire_eco_all[
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
                "BurnAreaEco",
                "US_L3NAME",
                "NA_L2NAME",
                "NA_L1NAME",
            ]
        ]
        .groupby(
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
                "US_L3NAME",
                "NA_L2NAME",
                "NA_L1NAME",
            ]
        )
        .sum()
        .reset_index()
    )

    annual_bap["BurnAreaPercentage"] = (
        annual_bap["BurnAreaEco"] / annual_bap["huc12_sqkm"]
    ) * 100
    f2f = stat.read_file("./DATA/F2F2_Assessment.gdb/", layer=1)[
        ["HUC12", "SW_Pop", "GW_POP", "POP_DS"]
    ]
    water = ro_all.merge(tp_all, on=["Year", "huc12"])
    water["Year"] = water["Year"].astype(int)
    consumer = annual_bap.merge(f2f, left_on=["huc12"], right_on=["HUC12"])
    print("Consumers:", consumer["huc12"].unique().__len__())
    consumer.to_csv(f"./Assets/Tables/HUC12_Annual_BAP_CONSUMERS_{epsg}.csv")
    cov = annual_bap.merge(
        water, left_on=["FIRE_YEAR_INT", "huc12"], right_on=["Year", "huc12"]
    )
    print("RO and TP:", cov["huc12"].unique().__len__())
    cov.to_csv(f"./Assets/Tables/HUC12_Annual_BAP_RO_TP_{epsg}.csv")
