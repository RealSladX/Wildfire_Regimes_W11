import matplotlib.pyplot as plt
from matplotlib.pyplot import rcParams, show, subplots, subplots_adjust
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from numpy import arange, array, zeros
from palettable import colorbrewer
from pandas import Categorical, options, pivot_table
from pandas.plotting import table
from seaborn import heatmap

options.mode.chained_assignment = None

rcParams["legend.fontsize"] = 18
rcParams["legend.title_fontsize"] = 18
rcParams["axes.grid"] = False
inc_cmap = colorbrewer.sequential.OrRd_9.mpl_colormap

cmap_dict = {"inc": inc_cmap}


def table_plot(data, fontsize=18):
    fig, ax = plt.subplots()
    table_p = table(ax, data, loc="center")
    table_p.set_fontsize(fontsize)
    table_p.scale(5, 10)
    ax.axis("tight")
    ax.axis("off")
    show()


def classify_label(data, ax_letter, cat):
    if data["Trend"].iloc[0] == "increasing":
        label = f"{ax_letter} {data[cat].iloc[0]}" + "$\\uparrow$"

    elif data["Trend"].iloc[0] == "no trend":
        label = f"{ax_letter} {data[cat].iloc[0]}"

    else:
        label = f"{ax_letter} {data[cat].iloc[0]}" + "$\\downarrow$"
    return label


def ts_heatmap(
    data, time_col, cat_col, plot_col, filter_col, cmap, xlabel, cbar_label, vmax=0.35
):
    # for filter_val in data[filter_col].unique():
    data_ = data[data[filter_col] == "increasing"]
    pivot = pivot_table(
        data_[[time_col, cat_col, plot_col]],
        index=cat_col,
        columns=time_col,
        values=plot_col,
    )
    ax = heatmap(
        pivot,
        cmap=cmap_dict[cmap],
        xticklabels=4,
        yticklabels=True,
        vmax=vmax,
        cbar_kws={"label": cbar_label, "pad": 0.02, "extend": "max", "shrink": 0.85},
    )
    ax.tick_params(
        axis="x",
        labelsize=12,
        which="both",
    )
    ax.tick_params(
        axis="y",
        labelsize=12,
        which="both",
    )
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("")
    subplots_adjust(top=0.98, bottom=0.1, left=0.35, right=1.01, hspace=0, wspace=0)
    show()
    data_ = data[data[filter_col] != "increasing"]
    pivot = pivot_table(
        data_[[time_col, cat_col, plot_col]],
        index=cat_col,
        columns=time_col,
        values=plot_col,
    )
    ax = heatmap(
        pivot,
        cmap=cmap_dict[cmap],
        xticklabels=4,
        yticklabels=True,
        vmax=vmax,
        cbar_kws={"label": cbar_label, "pad": 0.02, "extend": "max", "shrink": 0.85},
    )
    ax.tick_params(
        axis="x",
        labelsize=12,
        which="both",
    )
    ax.tick_params(
        axis="y",
        labelsize=12,
        which="both",
    )
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("")
    subplots_adjust(top=0.98, bottom=0.1, left=0.35, right=1.01, hspace=0, wspace=0)
    show()
    return pivot


def plot_stacked_histogram_reg(
    data,
    cat_col,
    categories,
    plot_col,
    bar_width,
    time_col,
    colors,
    leg_title,
    legend_loc,
    ylabel,
    log=False,
):
    fig, ax = subplots()
    x = arange(data[time_col].min(), data[time_col].max() + 1)
    bottom = zeros(len(x))
    handles = []
    labels = []
    for i, cat in enumerate(categories):
        plot_t = data[data[cat_col] == cat]
        plot = array(plot_t[plot_col])
        cp = plot_t["Changepoint (cp)"].iloc[0].astype(int)
        ax.bar(
            x[:cp],
            plot[:cp],
            bar_width,
            bottom=bottom[:cp],
            facecolor=colors[i],
            edgecolor="black",
            align="center",
            alpha=0.6,
            linewidth=0.1,
        )
        p = ax.bar(
            x[cp:],
            plot[cp:],
            bar_width,
            bottom=bottom[cp:],
            color=colors[i],
            align="center",
            edgecolor="black",
            linewidth=0.1,
        )
        handles.append(p)
        p_label = classify_label(plot_t, "", cat_col)
        labels.append(p_label)
        bottom += plot
    handles.reverse()
    labels.reverse()
    ax.set_xlim(data[time_col].min() - 2, data[time_col].max() + 2)
    ax.legend(
        handles,
        labels,
        loc=legend_loc,
        bbox_to_anchor=(1, 0),
        fontsize=18,
        ncols=1,
        title=leg_title,
        frameon=False,
    )
    ax.set_ylabel(ylabel)
    # yticks = arange(0,1.1,0.2)
    # labels = [
    #     "{}".format(str(round(yticks[i],1)))
    #     for i in range(len(yticks))
    # ]
    # ax.set_yticks(ticks=yticks, labels=labels, fontsize=18)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    if log:
        ax.set_yscale("log", base=log)

    ax.tick_params(
        axis="y",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected  # ticks along the bottom edge are off
        width=2,
        labelbottom=True,
        labelsize=12,
    )  # labels along the bottom edge are off
    ax.tick_params(
        axis="x",  # changes apply to the x-axis
        which="major",
        length=5,  # both major and minor ticks are affected  # ticks along the bottom edge are off
    )  # labels along the bottom edge are off
    ax.tick_params(
        axis="x",  # changes apply to the x-axis
        which="minor",
        length=2,  # both major and minor ticks are affected  # ticks along the bottom edge are off
    )  # labels along the bottom edge are off
    ax.tick_params(
        axis="y",  # changes apply to the x-axis
        which="major",
        length=5,  # both major and minor ticks are affected  # ticks along the bottom edge are off
    )  # labels along the bottom edge are off
    ax.tick_params(
        axis="y",  # changes apply to the x-axis
        which="minor",
        length=2,  # both major and minor ticks are affected  # ticks along the bottom edge are off
    )
    subplots_adjust(left=0.05, right=0.85, hspace=0, wspace=0)
    show()


def plot_stacked_histogram(
    data,
    cat_col,
    cat_labels,
    time_col,
    colors,
    legend_label,
    legend_loc,
    xlabel,
    ylabel,
):
    data[cat_col] = Categorical(
        data[cat_col],
        categories=cat_labels.keys(),
        ordered=True,
    )
    pivot_df = (
        data.groupby([time_col, cat_col], observed=False).size().unstack(fill_value=0)
    )
    # get the totals for each row
    totals = pivot_df.sum(axis=1)
    percent = pivot_df.div(totals, axis=0) * 100
    x = sorted(percent.index.values)
    fig, ax = subplots()
    bottom = zeros(len(x))
    handles1 = []
    handles2 = []
    for i, cat in enumerate(percent.columns):
        cp = cat_labels[cat]
        bars1 = ax.bar(
            x[:cp],
            percent.iloc[:cp, i],
            bottom=bottom[:cp],
            edgecolor=colors[i],
            linewidth=1.5,
            fill=False,
        )
        bars2 = ax.bar(
            x[cp:],
            percent.iloc[cp:, i],
            bottom=bottom[cp:],
            label=None,
            color=colors[i],
            alpha=0.8,
        )
        bottom += percent.iloc[:, i]
        handles1.append(bars1)
        handles2.append(bars2)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_xlabel(xlabel)
    handles1.reverse()
    handles2.reverse()
    handles = handles1 + handles2
    ax.legend(title=legend_label, loc=legend_loc)
    show()


def plot_multi_col_same_cats(
    data,
    cat_cols,
    cat_cols_names,
    cat_labels,
    time_col,
    plot_col,
    colors,
    ts_start,
    ts_end,
    xlabel,
    ylabel,
    legend_loc,
    leg_title,
    savepath,
    swap=False,
):
    if swap:
        fig, ax = subplots(
            len(data), len(cat_labels), sharex=True, sharey=True, figsize=(24, 18)
        )
    else:
        fig, ax = subplots(
            len(cat_labels), len(data), sharex=True, sharey=True, figsize=(24, 18)
        )
    letters = [
        "a)",
        "b)",
        "c)",
        "d)",
        "e)",
        "f)",
        "g)",
        "h)",
        "i)",
        "j)",
        "k)",
        "l)",
        "m)",
        "n)",
        "o)",
    ]
    l = 0
    d_handles = []
    d_labels = []
    for i, d in enumerate(data):
        d[time_col] = d[time_col].astype(int)
        d[plot_col] = d[plot_col].astype(float)
        d = d.astype(
            {
                "Kendall's $\\tau$": "float",
                "Slope": "float",
                "Intercept": "float",
                "Changepoint (cp)": "float",
                "Pre-cp average": "float",
                "Post-cp average": "float",
            }
        )
        if len(cat_cols) == 1:
            for j, cat in enumerate(cat_labels):
                ts = d[d[cat_cols[0]] == cat]
                label = classify_label(ts, letters[j], cat_cols[0])
                cp = ts["Changepoint (cp)"].iloc[0].astype(int)

                ax[j].axvline(
                    x=cp,
                    lw=4,
                    color="#e31a1c",
                )
                ax[j].plot(
                    ts[ts[time_col] >= (cp)][time_col],
                    ts[ts[time_col] >= (cp)][plot_col],
                    lw=5,
                    label=f"{label}",
                    color=colors[i],
                )
                ax[j].legend(loc=legend_loc, fontsize=26, frameon=False)
                ax[j].text(cp + 1, 25, f"{cp}", rotation=90, fontsize=22)
                ax[j].plot(
                    ts[ts[time_col] <= (cp)][time_col],
                    ts[ts[time_col] <= (cp)][plot_col],
                    lw=5,
                    label="Pre-cp",
                    color=colors[i],
                    alpha=0.5,
                )
                # slopeline = ax[j].plot(
                #     ts[time_col],
                #     (ts["Slope"].iloc[0] * (ts[time_col] - (ts_start - 1)))
                #     + ts["Intercept"].iloc[0],
                #     label=f"(m): {ts['Slope'].iloc[0]:.2f}",
                #     lw=2,
                #     color="#88429d",
                # )

                # slopelabel = [l.get_label() for l in slopeline]
                preline = ax[j].hlines(
                    ts["Pre-cp average"],
                    xmin=ts_start,
                    xmax=cp,
                    lw=2,
                    linestyles="-.",
                    colors="#fd8d3c",
                )
                postline = ax[j].hlines(
                    ts["Post-cp average"],
                    xmin=cp,
                    xmax=ts_end,
                    lw=2,
                    linestyles="-.",
                    colors="#238443",
                )
                ax[j].tick_params(axis="x", labelsize=20, which="both", bottom=False)
                ax[j].tick_params(axis="y", labelsize=20, which="both", left=False)
                # ax[j].set_facecolor('none')
                # ax[j].grid(False)
            for r in range(len(cat_labels)):
                ax[r].tick_params(axis="y", labelsize=20, which="both", left=True)
            ax[len(cat_labels) - 1].tick_params(
                axis="x", labelsize=20, which="both", bottom=True
            )
            ax[j].set_xlim(1940, 2024)
            ax[len(cat_labels) - 1].xaxis.set_major_locator(MultipleLocator(4))
            # ax[len(cat_labels) - 1].xaxis.set_minor_locator(AutoMinorLocator())
            ax[len(cat_labels) - 1].yaxis.set_minor_locator(AutoMinorLocator())
        else:
            repeat = False
            for j, cat in enumerate(cat_labels):
                ts = d[d[cat_cols[i]] == cat]
                label = classify_label(ts, letters[l], cat_cols[i])
                l += 1
                cp = ts["Changepoint (cp)"].iloc[0].astype(int)

                ax[i][j].axvline(
                    x=cp,
                    lw=2,
                    color="#e31a1c",
                )
                ax[i][j].plot(
                    ts[ts[time_col] >= (cp)][time_col],
                    ts[ts[time_col] >= (cp)][plot_col],
                    lw=4,
                    label=f"{label}",
                    color=colors[i],
                )
                if not repeat:
                    d_handle, la = ax[i][j].get_legend_handles_labels()
                    d_handles.append(d_handle[0])
                    d_labels.append(cat_cols_names[i])
                    repeat = True
                ax[i][j].legend(
                    loc=legend_loc, fontsize=28, frameon=False, handlelength=0
                )
                ax[i][j].text(cp + 1, 55, f"{cp}", rotation=90, fontsize=22)
                ax[i][j].plot(
                    ts[ts[time_col] <= (cp)][time_col],
                    ts[ts[time_col] <= (cp)][plot_col],
                    lw=4,
                    label="Pre-cp",
                    color=colors[i],
                    alpha=0.3,
                )
                # slopeline = ax[i][j].plot(
                #     ts[time_col],
                #     (ts["Slope"].iloc[0] * (ts[time_col] - (ts_start - 1)))
                #     + ts["Intercept"].iloc[0],
                #     label=f"(m): {ts['Slope'].iloc[0]:.2f}",
                #     lw=2,
                #     color="#88429d",
                # )
                #
                # slopelabel = [l.get_label() for l in slopeline]
                preline = ax[i][j].hlines(
                    ts["Pre-cp average"],
                    xmin=ts_start,
                    xmax=cp,
                    lw=2,
                    linestyles="-.",
                    colors="#fd8d3c",
                )
                postline = ax[i][j].hlines(
                    ts["Post-cp average"],
                    xmin=cp,
                    xmax=ts_end,
                    lw=2,
                    linestyles="-.",
                    colors="#238443",
                )
                ax[i][j].tick_params(axis="x", labelsize=18, which="both", bottom=False)
                ax[i][j].tick_params(axis="y", labelsize=18, which="both", left=False)

            for r in range(len(data)):
                ax[r][0].tick_params(axis="y", which="both", left=False)
            for c in range(len(cat_labels)):
                ax[len(data) - 1][c].tick_params(
                    axis="x", labelsize=18, which="both", bottom=True
                )
    # fig.patch.set_alpha(0)        # or: fig.patch.set_facecolor('none')
    fig.text(0.08, 0.5, ylabel, va="center", rotation="vertical", size=28)
    fig.legend(
        d_handles
        + [
            preline,
            postline,
            # slopeline[0]
        ],
        d_labels + ["Pre-cp average", "Post-cp average", "Slope"],
        loc="lower center",
        ncols=2,
        fontsize=22,
        frameon=False,
        bbox_to_anchor=(0.5, 0.047),
    )
    subplots_adjust(hspace=0, wspace=0)
    fig.savefig(savepath, dpi=300)
    # show()


def subplot_lines_by_cat(
    data,
    cat_col,
    cat_labels,
    ax_letters,
    ts_start,
    ts_end,
    legend_loc,
    leg_title,
):
    fig, axesgrid = plt.subplots(len(data), len(cat_labels), sharex="col", sharey="row")
    l = 0
    plotlines = []
    for i, (ylabel, (ts, time_col, plot_col, color)) in enumerate(data.items()):
        for j, cat in enumerate(cat_labels):
            curr1 = ts[ts[cat_col] == cat]
            label1 = classify_label(curr1, ax_letters[l], cat_col)
            l = l + 1
            cp1 = curr1["Changepoint (cp)"].iloc[0].astype(int)
            if cp1 < 1900:
                cp1 = ts_start + cp1
            axesgrid[i][j].axvline(
                x=cp1,
                lw=3,
                color="#e31a1c",
            )
            axesgrid[i][j].text(
                cp1 + 1, ts[plot_col].max() - 5, f"{cp1}", fontsize=16, rotation=90
            )
            axesgrid[i][j].plot(
                curr1[curr1[time_col] >= (cp1)][time_col],
                curr1[curr1[time_col] >= (cp1)][plot_col],
                lw=3.5,
                label=f"{label1}",
                color=color,
            )
            handles, labels = axesgrid[i][j].get_legend_handles_labels()
            precpplot1 = axesgrid[i][j].plot(
                curr1[curr1[time_col] <= (cp1)][time_col],
                curr1[curr1[time_col] <= (cp1)][plot_col],
                lw=3.5,
                label="Pre-cp",
                color=color,
                alpha=0.6,
            )
            plotlines.append(precpplot1[0])
            slopeline = axesgrid[i][j].plot(
                curr1[time_col],
                (
                    curr1["Slope"].iloc[0] * (curr1[time_col] - (ts_start - 1))
                    + curr1["Intercept"].iloc[0]
                ),
                lw=3,
                color="#88419d",
            )

            precp1label = [l.get_label() for l in precpplot1]

            preline = axesgrid[i][j].hlines(
                curr1["Pre-cp average"],
                xmin=ts_start,
                xmax=cp1,
                lw=3,
                linestyles="-.",
                label="Pre-cp average",
                colors="#fd8d3c",
            )
            postline = axesgrid[i][j].hlines(
                curr1["Post-cp average"],
                xmin=cp1,
                xmax=ts_end,
                lw=3,
                linestyles="-.",
                label="Post-cp average",
                colors="#238443",
            )
            axesgrid[i][j].set_ylim(0, ts[plot_col].max() + 10)
            axesgrid[i][j].set_xlim(ts_start, ts_end)
            axesgrid[i][j].xaxis.set_major_locator(MultipleLocator(10))
            axesgrid[i][j].xaxis.set_minor_locator(MultipleLocator(2))
            axesgrid[i][j].yaxis.set_major_locator(MultipleLocator(5))
            axesgrid[i][j].yaxis.set_minor_locator(MultipleLocator(1))
            axesgrid[i][j].tick_params(
                axis="x",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected  # ticks along the bottom edge are off
                width=2,
                labelbottom=True,
                labelrotation=45,
                labelsize=12,
            )  # labels along the bottom edge are off
            axesgrid[i][j].tick_params(
                axis="y",  # changes apply to the x-axis
                which="both",  # both major and minor ticks are affected  # ticks along the bottom edge are off
                width=2,
                labelbottom=True,
                labelsize=12,
            )  # labels along the bottom edge are off
            axesgrid[i][j].tick_params(
                axis="x",  # changes apply to the x-axis
                which="major",
                length=5,  # both major and minor ticks are affected  # ticks along the bottom edge are off
            )  # labels along the bottom edge are off
            axesgrid[i][j].tick_params(
                axis="x",  # changes apply to the x-axis
                which="minor",
                length=2,  # both major and minor ticks are affected  # ticks along the bottom edge are off
            )  # labels along the bottom edge are off
            axesgrid[i][j].tick_params(
                axis="y",  # changes apply to the x-axis
                which="major",
                length=5,  # both major and minor ticks are affected  # ticks along the bottom edge are off
            )  # labels along the bottom edge are off
            axesgrid[i][j].tick_params(
                axis="y",  # changes apply to the x-axis
                which="minor",
                length=2,  # both major and minor ticks are affected  # ticks along the bottom edge are off
            )  # labels along the bottom edge are off
            # axesgrid[i][j].tick_params(
            #     axis="y",  # changes apply to the x-axis
            #     which="both",  # both major and minor ticks are affected
            #     left=True,
            #     labelleft=True,
            #     labelsize=9
            # )
            if i == 0:
                axesgrid[i][j].tick_params(
                    axis="x",  # changes apply to the x-axis
                    which="both",  # both major and minor ticks are affected
                    bottom=True,  # ticks along the bottom edge are off
                    labelbottom=False,
                )  # labels along the bottom edge are off
            if j != 0:
                axesgrid[i][j].tick_params(
                    axis="y",  # changes apply to the x-axis
                    which="both",  # both major and minor ticks are affected
                    left=True,
                    labelleft=False,
                )
            if j == 0:
                axesgrid[i][j].set_ylabel(ylabel)
            axesgrid[i][j].legend(
                handles,
                labels,
                loc=legend_loc,
                fontsize=15,
                fancybox=False,
                frameon=False,
                handlelength=0.5,
            )
    fig.legend(
        [plotlines[0], plotlines[len(cat_labels)], preline, postline, slopeline[0]],
        ["Pre-cp", "Pre-cp", "Pre-cp average", "Post-cp average", "Slope (m)"],
        loc="lower center",
        alignment="center",
        ncols=5,
        frameon=False,
        bbox_to_anchor=(0.5, 0),
        fontsize=14,
        title=leg_title,
    )
    plt.subplots_adjust(left=0.04, right=0.995, hspace=0, wspace=0.1)
    show()
