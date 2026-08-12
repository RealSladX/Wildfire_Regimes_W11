import utils.stat as stat
import os
import utils.matplot as mplot

project_path = os.path.dirname(os.path.abspath(__file__))
shapes_path = os.path.join(project_path, "Assets/Shapes")
results_path = os.path.join(project_path, "Assets/Results")
fig_path = os.path.join(project_path, "Figures")

test_colors = ["#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"]
test_labels = [
    "Downstream consumers",
]


ds = stat.load_asset(os.path.join(results_path, "POP_DS_RESULTS_5070_TS.csv"))
ds["BAP_POP_DS"] = ds["BAP_POP_DS"].astype(float)
ds = ds[ds["BAP_POP_DS"] < 70]
mplot.plot_multi_col_same_cats(
    [ds],
    ["POP Interval"],
    ["0", "<100", "100-999", "1,000-9,999", "10,000-99,999", "$\\geq100,000$"],
    ["0", "<100", "100-999", "1,000-9,999", "10,000-99,999", "$\\geq100,000$"],
    "FIRE_YEAR_INT",
    "BAP_POP_DS",
    test_colors,
    1940,
    2024,
    "Year",
    "Burn Area %",
    "upper left",
    "legend",
    os.path.join(fig_path, "CONSUMERS_TS.png"),
)
