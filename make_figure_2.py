import numpy as np
import utils.stat as stat
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle


project_path = os.path.dirname(os.path.abspath(__file__))
res_path = os.path.join(project_path, "Assets/Results")
figs_path = os.path.join(project_path, "Figures")

epsgs = ["5070"]


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


colors = ["#fed976", "#feb24c", "#fd8d3c", "#cb181d", "#a50f15", "#67000d"]
heat_cmap = LinearSegmentedColormap.from_list("heat_cmap", colors)


years = [
    (1944, 1964),
    (1965, 1984),
    (1985, 2004),
    (2005, 2024),
]


labels = ["<1%", "1-9.99%", "10-19.99%", "20-49.99%", "50-99.99%", "$\\geq$100%"]
percentiles = ["20th", "40th", "60th", "80th", "99th"]
runoff_colors = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]
subplotletters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

for epsg in epsgs:
    test = stat.load_asset(f"./Assets/Tables/RO_TP_HUC12_Percentiles_STATIC_{epsg}.csv")
    test = test.astype(
        {
            "ro": "float",
            "tp": "float",
            "RO/TP": "float",
            "BurnAreaEco": "float",
            "huc12_sqkm": "float",
            "FIRE_YEAR_INT": "float",
            "huc12": "int",
        }
    )
    test = (
        test[
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
                "ro",
                "tp",
                "RO/TP",
                "RO_Percentiles",
                "TP_Percentiles",
                "RO_Over_TP_Percentiles",
                "BurnAreaEco",
            ]
        ]
        .groupby(
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
                "ro",
                "tp",
                "RO/TP",
                "RO_Percentiles",
                "TP_Percentiles",
                "RO_Over_TP_Percentiles",
            ]
        )
        .sum()
        .reset_index()
    )

    test2 = stat.load_asset(f"./Assets/Tables/POP_DS_HUC12_GROUPS_{epsg}.csv")
    test2 = test2.astype(
        {
            "BurnAreaEco": "float",
            "huc12_sqkm": "float",
            "FIRE_YEAR_INT": "float",
            "huc12": "int",
        }
    )
    test2 = (
        test2[
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
                "BurnAreaEco",
            ]
        ]
        .groupby(
            [
                "FIRE_YEAR_INT",
                "huc12",
                "huc12_sqkm",
            ]
        )
        .sum()
        .reset_index()
    )

    test2["BurnAreaPercentage"] = (test2["BurnAreaEco"] / test2["huc12_sqkm"]) * 100
    test2["BAP Interval"] = test2["BurnAreaPercentage"].apply(categorize_percent)
    test2["BAP Interval"] = pd.Series(test2["BAP Interval"], dtype="category")
    test2["BAP Interval"] = test2["BAP Interval"].cat.set_categories(
        labels, ordered=True
    )

    test2["huc2"] = test2["huc12"].astype(str)
    test2["huc2"] = test2["huc2"].str[:2]

    bins = np.linspace(0, test["RO/TP"].max(), 20)
    res = stat.load_asset(f"./Assets/Results/RO_OVER_TP_RESULTS_STATIC_{epsg}_TS.csv")
    test["BurnAreaPercentage"] = (test["BurnAreaEco"] / test["huc12_sqkm"]) * 100
    test["FIRE_YEAR_INT"] = test["FIRE_YEAR_INT"].round(0)
    test["FIRE_YEAR_INT"] = test["FIRE_YEAR_INT"].astype(int)
    test["BAP Interval"] = test["BurnAreaPercentage"].apply(categorize_percent)
    test["BAP Interval"] = pd.Series(test["BAP Interval"], dtype="category")
    test["BAP Interval"] = test["BAP Interval"].cat.set_categories(labels, ordered=True)
    test["RO_Percentiles"] = pd.Series(test["RO_Percentiles"], dtype="category")
    test["RO_Over_TP_Percentiles"] = pd.Series(
        test["RO_Over_TP_Percentiles"], dtype="category"
    )
    test["RO_Percentiles"] = test["RO_Percentiles"].cat.set_categories(
        percentiles, ordered=True
    )
    test["RO_Over_TP_Percentiles"] = test["RO_Over_TP_Percentiles"].cat.set_categories(
        percentiles, ordered=True
    )
    extract = test[test["RO_Over_TP_Percentiles"] == "40th"]
    extract = extract[extract["FIRE_YEAR_INT"] == 1944]
    heat_map_data = pd.pivot_table(
        test[["FIRE_YEAR_INT", "RO_Over_TP_Percentiles", "BurnAreaPercentage"]],
        values="BurnAreaPercentage",
        index="RO_Over_TP_Percentiles",
        columns="FIRE_YEAR_INT",
        aggfunc="mean",
        observed=False,
    )
    fig5, ax5 = plt.subplots(figsize=(42, 10), tight_layout=False)
    sns.heatmap(
        heat_map_data.iloc[::-1],
        annot=False,
        cmap=heat_cmap,
        ax=ax5,
        # square=True,
        xticklabels=4,
        cbar_kws={"label": "Burn area %", "shrink": 0.98, "pad": 0.08},
    )
    ax5.figure.axes[-1].yaxis.label.set_size(35)
    ax5.tick_params(axis="x", labelsize=35)
    ax5.tick_params(axis="y", labelsize=35)
    ax5.set_xlabel("Year", fontsize=35)
    ax5.set_ylabel("Runoff Ratio Percentiles", fontsize=35)
    for i, l in enumerate(percentiles):
        row_idx = heat_map_data.index.get_loc(l)
        print(l, row_idx)
        n = res[res["RO_Over_TP_Percentiles"] == l]["watersheds"].iloc[0]
        arrow = (
            "$\\uparrow$"
            if res[res["RO_Over_TP_Percentiles"] == l]["Trend"].iloc[0] == "increasing"
            else ""
        )
        ax5.annotate(
            f"n={n}{arrow}",
            (2250, (i * 110) + 70),
            size=35,
            xycoords="axes points",
            ha="left",
            va="top",
        )
        cp = res[res["RO_Over_TP_Percentiles"] == l]["Changepoint (cp)"].iloc[0]
        print(l, cp)
        cp = int(cp)
        col_idx = heat_map_data.columns.get_loc(cp)
        rect = Rectangle(
            (col_idx, max(4 - row_idx, 0)),
            1,
            1,
            fill=False,
            edgecolor="#6a51a3",
            linewidth=4,
        )
        ax5.add_patch(rect)

    fig5.savefig(os.path.join(figs_path, f"RO_TP_BAP_HEATMAP_{epsg}_2.png"), dpi=300)
