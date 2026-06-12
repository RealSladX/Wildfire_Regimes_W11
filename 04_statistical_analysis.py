import utils.stat as stat
import pandas as pd
import os

project_path = os.path.dirname(os.path.abspath(__file__))
results_path = os.path.join(project_path, "Assets/Results")
tables_path = os.path.join(project_path, "Assets/Tables")
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

ro = os.path.join(tables_path, "HUC12_Average_Monthly_Runoff.csv")
tp = os.path.join(tables_path, "HUC12_Average_Monthly_Precip.csv")

runoff_bins5 = [0, 0.2, 0.4, 0.6, 0.8, 1]
runoff_labels5 = ["20th", "40th", "60th", "80th", "99th"]

bap_intervals = ["<1%", "1-9.99%", "10-19.99%", "20-49.99%", "50-99.99%", "$\\geq$100%"]

epsgs = ["5070"]


def ro_tp_test():
    for epsg in epsgs:
        ts_ro = stat.read_file(ro)
        ts_tp = stat.read_file(tp)
        ts_ro = ts_ro.astype(
            {
                "ro": "float",
            }
        )

        ts_tp = ts_tp.astype(
            {
                "tp": "float",
            }
        )

        ts_ro = ts_ro[["huc12", "ro"]].groupby("huc12").mean().reset_index()
        ts_tp = ts_tp[["huc12", "tp"]].groupby("huc12").mean().reset_index()
        ts = ts_ro.merge(ts_tp, on="huc12")
        ro_ress = []
        tp_ress = []
        ro_over_tp_ress = []
        fires = os.path.join(tables_path, f"W11_BURN_AREA_MATRIX_{epsg}.csv")
        ts_fires = stat.read_file(fires)
        ts_fires = ts_fires.astype(
            {
                "FIRE_YEAR_INT": "float",
                "huc12_sqkm": "float",
                "BurnAreaEco": "float",
            }
        )
        ts_fires = ts_fires.astype(
            {
                "FIRE_YEAR_INT": "int",
            }
        )

        ts = ts.merge(
            ts_fires[["FIRE_YEAR_INT", "huc12", "huc12_sqkm", "BurnAreaEco"]],
            on="huc12",
        )
        ts["RO/TP"] = ts["ro"] / ts["tp"]
        ts["TP/RO"] = ts["tp"] / ts["ro"]
        stat.quantile_cut(ts, "ro", runoff_bins5, runoff_labels5, "RO_Percentiles")
        stat.quantile_cut(ts, "tp", runoff_bins5, runoff_labels5, "TP_Percentiles")
        stat.quantile_cut(
            ts,
            "RO/TP",
            runoff_bins5,
            runoff_labels5,
            "RO_Over_TP_Percentiles",
        )
        ts.to_csv(os.path.join(tables_path, f"RO_TP_HUC12_Percentiles_STATIC_{epsg}.csv"))
        ro_res = stat.significance_by_class(
            ts,
            "FIRE_YEAR_INT",
            "RO_Percentiles",
            runoff_labels5,
            "BurnAreaEco",
            "huc12_sqkm",
            "BAP_RO",
            "Burned Areas",
            "huc12",
            "watersheds",
            os.path.join(results_path, f"RO_RESULTS_STATIC_{epsg}"),
        )
        ro_res.insert(loc=1, column="Period", value="1940-2024")
        ro_res.insert(loc=1, column="EPSG", value=f"{epsg}")
        ro_ress.append(ro_res)
        tp_res = stat.significance_by_class(
            ts,
            "FIRE_YEAR_INT",
            "TP_Percentiles",
            runoff_labels5,
            "BurnAreaEco",
            "huc12_sqkm",
            "BAP_TP",
            "Burned Areas",
            "huc12",
            "watersheds",
            os.path.join(results_path, f"TP_RESULTS_STATIC_{epsg}"),
        )
        tp_res.insert(loc=1, column="Period", value="1940-2024")
        tp_res.insert(loc=1, column="EPSG", value=f"{epsg}")
        tp_ress.append(tp_res)
        ro_over_tp_res = stat.significance_by_class(
            ts,
            "FIRE_YEAR_INT",
            "RO_Over_TP_Percentiles",
            runoff_labels5,
            "BurnAreaEco",
            "huc12_sqkm",
            "BAP_RO/TP",
            "Burned Areas",
            "huc12",
            "watersheds",
            os.path.join(results_path, f"RO_OVER_TP_RESULTS_STATIC_{epsg}"),
        )
        ro_over_tp_res.insert(loc=1, column="Period", value="1940-2024")
        ro_over_tp_res.insert(loc=1, column="EPSG", value=f"{epsg}")
        ro_over_tp_ress.append(ro_over_tp_res)
    return pd.concat(ro_ress), pd.concat(tp_ress), pd.concat(ro_over_tp_ress)


ro_ress, tp_ress, ro_over_tp_ress = ro_tp_test()

ro_ress.to_csv(os.path.join(results_path, "RO_TP_HUC12_Percentiles_STATIC.csv"))
tp_ress.to_csv(os.path.join(results_path, "RO_TP_HUC12_Percentiles_STATIC.csv"))
ro_over_tp_ress.to_csv(os.path.join(results_path, "RO_TP_HUC12_Percentiles_STATIC.csv"))


def categorize_percent(percent):
    if percent < 1:
        return "<1%"
    elif percent < 10:
        return "1-9.99%"
    elif percent < 20:
        return "10-19.99%"
    elif percent < 50:
        return "20-49.99%"
    elif percent < 100:
        return "50-99.99%"
    else:
        return "$\\geq$100%"


bap_intervals = ["<1%", "1-9.99%", "10-19.99%", "20-49.99%", "50-99.99%", "$\\geq$100%"]


def BAP_Interval_Test():
    for epsg in epsgs:
        ts_path = f"./Assets/Tables/HUC12_Annual_BAP_CONSUMERS_{epsg}.csv"
        ts = stat.read_file(ts_path)[
            ["FIRE_YEAR_INT", "huc12", "huc12_sqkm", "BurnAreaEco"]
        ]
        ts = ts.astype(
            {"FIRE_YEAR_INT": "float", "huc12_sqkm": "float", "BurnAreaEco": "float"}
        )
        ts["FIRE_YEAR_INT"] = ts["FIRE_YEAR_INT"].round(0)
        ts["FIRE_YEAR_INT"] = ts["FIRE_YEAR_INT"].astype(int)

        annual = (
            ts.groupby(["FIRE_YEAR_INT", "huc12", "huc12_sqkm"]).sum().reset_index()
        )
        annual["BurnAreaPercentage"] = (
            annual["BurnAreaEco"] / annual["huc12_sqkm"]
        ) * 100
        annual["BAP Interval"] = annual["BurnAreaPercentage"].apply(categorize_percent)
        annual.to_csv("./Assets/Tables/BAP_INTERVAL_TS.csv")
        pivot = stat.freq_table(annual, "BAP Interval", groupby="FIRE_YEAR_INT")

        interval_results = []
        interval_results_ts = []
        for b in bap_intervals:
            num_obs = len(annual[annual["BAP Interval"] == b]["huc12"].unique())
            res, autocorr = stat.time_series_significance(
                pivot[pivot["BAP Interval"] == b], "BAP Interval", "proportion"
            )
            res.insert(loc=1, column="# of watersheds", value=num_obs)
            res["Changepoint (cp)"] = res["Changepoint (cp)"] + 1940
            interval_results.append(res)
            i_res = pd.merge(pivot[pivot["BAP Interval"] == b], res, on="BAP Interval")
            interval_results_ts.append(i_res)
        #

        interval_results = pd.concat(interval_results)
        interval_results_ts = pd.concat(interval_results_ts)
        interval_results.to_csv(os.path.join(results_path, f"BAP_INTERVAL_RESULTS_{epsg}.csv"))
        interval_results_ts.to_csv(os.path.join(results_path, f"BAP_INTERVAL_MK_HG_TS_{epsg}.csv"))


BAP_Interval_Test()


def eco_test():
    for epsg in epsgs:
        ts_path = f"./Assets/Tables/HUC12_Annual_BAP_CONSUMERS_{epsg}.csv"
        ts = stat.read_file(ts_path)

        eco_test = ts.astype(
            {
                "FIRE_YEAR_INT": "float",
                "huc12": "int",
                "huc12_sqkm": "float",
                "BurnAreaEco": "float",
            }
        )

        eco_test["NA_L2NAME"] = eco_test["NA_L2NAME"].replace(
            "UPPER GILA MOUNTAINS (?)", "UPPER GILA MOUNTAINS"
        )
        eco_test["US_L3NAME"] = eco_test["US_L3NAME"].replace(
            "Klamath Mountains/California High North Coast Range", "Klamath Mountains"
        )
        eco_test["US_L3NAME"] = eco_test["US_L3NAME"].replace(
            "Arizona/New Mexico Mountains", "AZ/NM Mountains"
        )
        eco_test["US_L3NAME"] = eco_test["US_L3NAME"].replace(
            "Arizona/New Mexico Plateau", "AZ/NM Plateau"
        )

        eco_test["FIRE_YEAR_INT"] = eco_test["FIRE_YEAR_INT"].round(0)
        eco_test["FIRE_YEAR_INT"] = eco_test["FIRE_YEAR_INT"].astype(int)
        eco_test["BurnAreaEco"] = eco_test["BurnAreaEco"].astype(float)
        eco_test["huc12_sqkm"] = eco_test["huc12_sqkm"].astype(float)

        eco_results = stat.significance_by_class(
            eco_test,
            "FIRE_YEAR_INT",
            "US_L3NAME",
            sorted(eco_test["US_L3NAME"].unique()),
            "BurnAreaEco",
            "huc12_sqkm",
            "BurnAreaPercentage",
            "# of burned areas",
            "huc12",
            "# of watersheds",
            os.path.join(results_path, f"ECO_MK_HG_L3_{epsg}"),
        )
        print(eco_results[eco_results["Trend"] == "increasing"])
        print(eco_results[eco_results["Trend"] == "no trend"])
        print(eco_results[eco_results["Trend"] == "decreasing"])
        print("\n")

eco_test()


def classify_pop(pop):
    if pop == 0:
        return "0"
    elif pop < 100:
        return "<100"
    elif pop < 1000:
        return "100-999"
    elif pop < 10000:
        return "1,000-9,999"
    elif pop < 100000:
        return "10,000-99,999"
    else:
        return "$\\geq100,000$"


con_t_5070 = os.path.join(tables_path, "HUC12_Annual_BAP_CONSUMERS_5070.csv")

con_tests = [(con_t_5070, "5070")]

intervals = ["0", "<100", "100-999", "1,000-9,999", "10,000-99,999", "$\\geq100,000$"]
for tp, tn in con_tests:
    ts = stat.read_file(tp)
    ts = ts.astype(
        {
            "FIRE_YEAR_INT": "float",
            "huc12": "int",
            "huc12_sqkm": "float",
            "BurnAreaEco": "float",
            "POP_DS": "float",
        }
    )
    ts["FIRE_YEAR_INT"] = ts["FIRE_YEAR_INT"].round(0)
    ts["FIRE_YEAR_INT"] = ts["FIRE_YEAR_INT"].astype(int)
    ts["POP Interval"] = ts["POP_DS"].apply(classify_pop)
    ts.to_csv(f"./Assets/Tables/POP_DS_HUC12_GROUPS_{tn}.csv")
    ro_res = stat.significance_by_class(
        ts,
        "FIRE_YEAR_INT",
        "POP Interval",
        intervals,
        "BurnAreaEco",
        "huc12_sqkm",
        "BAP_POP_DS",
        "Burned Areas",
        "huc12",
        "watersheds",
        os.path.join(results_path, f"POP_DS_RESULTS_{tn}"),
    )

