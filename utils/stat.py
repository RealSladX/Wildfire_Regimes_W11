from pandas import options
from pandas import qcut, merge, concat, DataFrame
import pyhomogeneity as hg
import pymannkendall as mk
from geopandas import read_file as read_file
from scipy.stats import pearsonr as pearson
from scipy.stats import spearmanr as spearman
from statsmodels.formula.api import quantreg
from statsmodels.formula.api import ols
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
from statsmodels.stats.diagnostic import acorr_ljungbox
import numpy as np

options.mode.chained_assignment = None


def load_asset(path):
    return read_file(path)


def quantile_cut(data, column, bins, labels, q_col):
    data[q_col] = qcut(data[column], bins, labels=labels)


def freq_table(data, var_col, groupby=None):
    if groupby:
        return (
            data[[groupby, var_col]]
            .groupby(groupby, observed=False)
            .value_counts(normalize=True)
            .reset_index()
        )
    else:
        return data[[var_col]].value_counts(normalize=True).reset_index()


def corr_analysis(data, x, y):
    print("Pearson:", pearson(data[[x]], data[[y]]))
    print("Spearman:", spearman(data[[x, y]]))


def lin_model(data, x, y):
    X = add_constant(data[[x]])
    mod = OLS(data[y], exog=X)
    res = mod.fit()
    print(res.summary())


def q_regression(data, x, y, qs):
    mod = quantreg(f"{y} ~ {x}", data[[x, y]])
    LAD = mod.fit(q=0.5)
    print("LAD\n")
    print(LAD.summary())
    models = []
    for q in qs:
        res = mod.fit(q=q)
        test_res = [q, res.params["Intercept"], res.params[x]] + res.conf_int().loc[
            x
        ].tolist()
        models.append(test_res)
    models = DataFrame(models, columns=[f"{x} q", "a", "b", "lb", "ub"])

    ols_mod = ols(f"{y} ~ {x}", data[[x, y]]).fit()
    ols_ci = ols_mod.conf_int().loc[x].tolist()
    ols_mod = dict(
        a=ols_mod.params["Intercept"], b=ols_mod.params[x], lb=ols_ci[0], ub=ols_ci[1]
    )

    print(models)
    print(ols_mod)
    return (models, ols_mod)


def make_time_series_by_class(data, time_col, class_col, var_col, norm_col, test_col):
    agg = (
        data[[time_col, class_col, var_col, norm_col]]
        .groupby([time_col, class_col], observed=False)
        .sum()
        .reset_index()
    )
    agg[test_col] = (agg[var_col] / agg[norm_col]) * 100
    agg = agg.dropna(subset=[test_col])
    return agg


def mk_power_simulation(
    n=85, tau_target=0.2, n_sims=10000, alpha=0.05, ar1=0.15, cv=0.5
):
    rejections = 0
    for _ in range(n_sims):
        t = np.arange(n)
        noise = np.random.normal(0, 1, n)
        ar_noise = np.zeros(n)
        for i in range(1, n):
            ar_noise[i] = ar1 * ar_noise[i - 1] + noise[i]
        # Trend based on target tau (approximate)
        trend_strength = (
            tau_target
            * np.sqrt(n * (n - 1) * (2 * n + 5) / 18)
            / np.sqrt(n * (n - 1) / 2)
        )  # Rough scaling
        y = trend_strength * t + cv * ar_noise
        # Apply modified MK if autocorr present
        result = mk.hamed_rao_modification_test(y, lag=3)
        if result.p < alpha:
            rejections += 1
    power = rejections / n_sims
    return power


def mk_test(time_series, class_col, test_col):
    print(time_series.head())
    lb_test = acorr_ljungbox(time_series[test_col], lags=[1], return_df=True)
    lb_test.insert(loc=0, column=class_col, value=time_series[class_col].iloc[0])
    lb_test = lb_test.round({"lb_stat": 2, "lb_pvalue": 4})
    if lb_test["lb_pvalue"].iloc[0] < 0.05:
        print(
            f"{class_col} {time_series[class_col].iloc[0]}: Significant autocorrelation detected. Using modified MK"
        )
        mk_res = mk.hamed_rao_modification_test(time_series[test_col], lag=3)
        power = mk_power_simulation(tau_target=mk_res.Tau)
        mk_df = DataFrame(
            [
                [
                    mk_res.trend,
                    "{:.2e}".format(mk_res.p),
                    mk_res.Tau,
                    mk_res.slope,
                    mk_res.intercept,
                    power,
                ]
            ],
            columns=[
                "Trend",
                "p-value",
                "Kendall's $\\tau$",
                "Slope",
                "Intercept",
                "Stat Power (n=10,000)",
            ],
        )
        mk_df.insert(loc=0, column=class_col, value=time_series[class_col].iloc[0])
        mk_df = mk_df.round({"Kendall's $\\tau$": 2, "Slope": 3, "Intercept": 3})
    else:
        mk_res = mk.original_test(time_series[test_col])
        power = mk_power_simulation(tau_target=mk_res.Tau)
        mk_df = DataFrame(
            [
                [
                    mk_res.trend,
                    "{:.2e}".format(mk_res.p),
                    mk_res.Tau,
                    mk_res.slope,
                    mk_res.intercept,
                    power,
                ]
            ],
            columns=[
                "Trend",
                "p-value",
                "Kendall's $\\tau$",
                "Slope",
                "Intercept",
                "Stat Power (n=10,000)",
            ],
        )
        mk_df.insert(loc=0, column=class_col, value=time_series[class_col].iloc[0])
        mk_df = mk_df.round({"Kendall's $\\tau$": 2, "Slope": 3, "Intercept": 3})
    return (mk_df, lb_test)


def hg_test(time_series, class_col, test_col):
    h, cp, p, U, mu = hg.pettitt_test(time_series[test_col])
    data = [h, cp, "{:.2e}".format(p), mu[0], mu[1]]
    hg_df = DataFrame(
        [data],
        columns=[
            "Nonhomogeneous",
            "Changepoint (cp)",
            "cp p-value",
            "Pre-cp average",
            "Post-cp average",
        ],
    )
    hg_df.insert(loc=0, column=class_col, value=time_series[class_col].iloc[0])
    hg_df = hg_df.round({"Pre-cp average": 2, "Post-cp average": 2})
    return hg_df


def time_series_significance(time_series, class_col, test_col):
    mk_res = mk_test(time_series, class_col, test_col)
    results = merge(
        mk_res[0],
        hg_test(time_series, class_col, test_col),
        on=class_col,
    )
    return results, mk_res[1]


def significance_by_class(
    data,
    time_col,
    class_col,
    class_labels,
    var_col,
    norm_col,
    test_col,
    obs_label,
    count_col,
    count_label,
    save_path,
):
    tss = make_time_series_by_class(
        data, time_col, class_col, var_col, norm_col, test_col
    )
    results = []
    lb_results = []
    ts_results = []
    for cl in class_labels:
        ts = tss[tss[class_col] == cl]
        num_areas = len(data[data[class_col] == cl][count_col].unique())
        num_obs = len(data[data[class_col] == cl])
        class_result, lb_result = time_series_significance(ts, class_col, test_col)
        class_result["Changepoint (cp)"] += ts[time_col].min()
        class_result.insert(loc=1, column=count_label, value=num_areas)
        class_result.insert(loc=1, column=obs_label, value=num_obs)
        results.append(class_result)
        lb_results.append(lb_result)
        ts_result = merge(ts, class_result, on=class_col)
        ts_results.append(ts_result)
    results = concat(results)
    results.to_csv(f"{save_path}.csv")
    lb_results = concat(lb_results)
    lb_results.to_csv(f"{save_path}_LB.csv")
    ts_results = concat(ts_results)
    ts_results.to_csv(f"{save_path}_TS.csv")
    return results
