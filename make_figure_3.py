import pycollection.tsa.stat as stat
import os
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import seaborn as sns

project_path = os.path.dirname(os.path.abspath(__file__))
tables_path = os.path.join(project_path, "Assets/Tables")
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


years = [1940, 1949, 1979, 1984, 1999, 2000, 2024]


labels = ["<1%", "1-9.99%", "10-19.99%", "20-49.99%", "50-99.99%", "$\\geq$100%"]
percentiles = ["20th", "40th", "60th", "80th", "99th"]
runoff_colors = ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]
subplotletters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

test = stat.load_asset(os.path.join(tables_path, "RO_TP_HUC12_Percentiles_STATIC_5070.csv"))
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

cp_bap_years = {
    "<1%": 1962,
    "1-9.99%": 1988,
    "10-19.99%": 1961,
    "20-49.99%": 1985,
    "50-99.99%": 1999,
    "$\\geq$100%": 1968,
}

fig, ax = plt.subplots(1, 6, sharex=True, sharey=True, figsize=(28, 12))


def changepoint(year, cp):
    if year < cp:
        return "pre-cp"
    else:
        return "post-cp"


for i, (k, v) in enumerate(cp_bap_years.items()):
    t = test[test["BAP Interval"] == k]
    t["period"] = t["FIRE_YEAR_INT"].apply(changepoint, cp=v)
    print(t)
    s = sns.violinplot(
        data=t,
        # x="BAP Interval",
        y="RO/TP",
        hue="period",
        split=True,
        ax=ax[i % 6],
        color="#FFFFFF",
        inner="quartiles",
        legend="full",
        cut=0,
    )
    for l in s.lines[:3]:
        l.set_linestyle("--")
        l.set_color("#ffffff")
        l.set_linewidth(4)
    s.lines[1].set_linestyle("-")
    for l in s.lines[3:]:
        l.set_linestyle("--")
        l.set_color("#000000")
        l.set_linewidth(4)

    s.lines[4].set_linestyle("-")
    ax[i % 6].legend(
        handles=[None, None],
        labels=["", ""],
        fontsize=24,
        markerscale=8.5,
        handlelength=2,
        title=f"{chr(i + 97)}) {k}",
        title_fontsize=28,
        loc="upper left",
        fancybox=False,
        frameon=False,
    )
h, l = s.get_legend_handles_labels()
fig.legend(
    h, l, fontsize=24, markerscale=8.5, handlelength=2, fancybox=False, frameon=False
)
ax[0].set_ylabel("Annual runoff ratio", fontsize=24)
ax[0].tick_params(axis="y", labelsize=24)
fig.subplots_adjust(top=0.97, bottom=0.15, wspace=0, hspace=0)
fig.savefig(os.path.join(figs_path, "SPLIT_VIOLIN.png"), dpi=300)
