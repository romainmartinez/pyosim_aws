import numpy as np
import pandas as pd


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


def random_balanced_design(d, params, random_state):
    g = d.drop_duplicates("filename").groupby(params)
    minimum = g.size().min()
    return pd.concat(
        [
            igroupby.sample(minimum, random_state=random_state)["filename"]
            for idx, igroupby in g
        ]
    ).to_list()


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
