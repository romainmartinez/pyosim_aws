import numpy as np
import pandas as pd
import altair as alt

def parse_conditions(df, filename_col="filename", prefix="", suffix=""):
    return df.assign(
        filename=lambda x: x[filename_col]
        .str.replace(prefix, "")
        .str.replace(suffix, "")
        .astype("category"),
        participant=lambda x: x[filename_col].str[:4].str.lower().astype("category"),
        men=lambda x: x[filename_col].str[4].replace({"H": 1, "F": 0, "M": 1}),
        height=lambda x: x[filename_col].str[-3].astype(int),

        mass=lambda x: x[filename_col].str[5:].str.split("H").str[0].astype(int),
        n_trial=lambda x: x[filename_col].str[-1].astype(int),
    )


def condition_counter(d):
    lines = "-" * 10
    d = d.drop_duplicates("filename")
    print(f"n. participants: {d['participant'].nunique()}")
    print(lines)
    cols = ["men", "height", "mass", ["men", "mass"]]
    for icol in cols:
        print(d.groupby(icol).size().to_string())
        print(lines)


def random_balanced_design(d, params, random_state, participant=False):
    output_cols = ["filename", "participant"] if participant else ["filename"]
    g = d.drop_duplicates(output_cols).groupby(params)
    minimum = g.size().min()
    return pd.concat(
        [
            igroupby.sample(minimum, random_state=random_state)[output_cols]
            for idx, igroupby in g
        ]
    )


def get_spm_cluster(spm, labels=None, mult=1):
    labels = labels if labels else {}
    out = []
    for ieffect in spm:
        for icluster in ieffect.clusters:
            out.append(
                pd.Series(
                    {
                        "effect": ieffect.effect,
                        "p": icluster.P,
                        "start": icluster.endpoints[0] * mult,
                        "end": icluster.endpoints[1] * mult,
                    }
                )
            )
    return pd.concat(out, axis=1).T.assign(effect=lambda x: x["effect"].replace(labels))

def ridge_plot(d, value, groupby, step=30, overlap=0.8, sort=None):
    return (
        alt.Chart(d)
        .transform_joinaggregate(mean_value=f"mean({value})", groupby=[groupby])
        .transform_bin(["bin_max", "bin_min"], value)
        .transform_aggregate(
            value="count()", groupby=[groupby, "mean_value", "bin_min", "bin_max"]
        )
        .transform_impute(
            impute="value", groupby=[groupby, "mean_value"], key="bin_min", value=0
        )
        .mark_area(
            interpolate="monotone", fillOpacity=0.8, stroke="lightgray", strokeWidth=0.5
        )
        .encode(
            alt.X("bin_min:Q", bin="binned", title=value),
            alt.Y("value:Q", scale=alt.Scale(range=[step, -step * overlap]), axis=None),
            alt.Fill(
                "mean_value:Q",
                legend=None,
                scale=alt.Scale(
                    domain=[d[value].max(), d[value].min()], scheme="redyellowblue"
                ),
            ),
            alt.Row(
                f"{groupby}:N",
                title=None,
                sort=alt.SortArray(sort) if sort else None,
                header=alt.Header(labelAngle=0, labelAlign="right", format="%B"),
            ),
        )
        .properties(bounds="flush", height=step)
#         .configure_facet(spacing=0)
#         .configure_view(stroke=None)
    )
