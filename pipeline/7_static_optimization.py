"""
Static optimization
"""
import yaml
from pyosim import Conf
from pyosim import StaticOptimization

import pandas as pd

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

model_names = ["wu"]

blacklist = [
    "wu_AnnSF6H2_1",
    "wu_AnnSF6H2_3",
    "wu_SteBF6H2_2",
    "wu_JawRH12H4_1",
    "wu_JawRH12H3_3",
    "wu_JawRH12H3_2",
    "wu_JawRH12H2_1",
    "wu_JawRH12H1_3",
    "wu_NemKH6H2_3",
    "wu_NemKH6H1_3",
    "wu_NemKH6H1_2",
    "wu_NemKH6H1_1",
    "wu_NemKH18H2_3",
    "wu_NemKH12H2_2",
    "wu_NemKH12H1_3",
    "wu_NemKH12H1_2",
    "wu_GeoAH6H1_2",
    "wu_GeoAH18H2_3",
    "wu_GeoAH18H1_2",
    "wu_DavOH12H2_3",
    "wu_PatMH12H2_2",
    # Fiber length is nan
    "wu_IneAF12H2_3",
    "wu_MarSF12H2_1",
    "wu_BenLH6H2_2",
    "wu_BenLH18H2_3",
    "wu_BenLH6H2_3",
    "wu_BenLH18H2_2",  # SRA2
    "wu_BenLH6H2_1",  # SRA2
    "wu_BenLH12H2_3",  # SRA2
    "wu_BenLH18H2_1",  # SRA2
    "wu_BenLH12H2_1",  # SRA2
    "wu_BenLH12H2_2",  # SRA2
    "wu_GatBH12H2_1",  # SRA2
    "wu_GatBH6H2_2",  # SRA2
    "wu_GatBH6H2_3",  # SRA2
    "wu_GatBH12H2_2",  # SRA2
    "wu_GatBH12H2_3",  # SRA2
    "wu_GatBH18H2_1",  # SRA2
    "wu_GatBH18H2_2",  # SRA2
    "wu_GatBH18H2_3",  # SRA2
    "wu_GatBH6H2_1",  # SRA2
    "wu_YoaPH12H2_2",  # SRA2
    "wu_PatMH6H2_2",  # SRA2
    "wu_PatMH12H2_1",  # SRA2
    "wu_PatMH12H2_3",  # SRA2
    "wu_PatMH6H2_1",  # SRA2
    "wu_PatMH6H2_3",  # SRA2
    "wu_PatMH18H2_1",  # SRA2
    "wu_PatMH18H2_2",  # SRA2
    "wu_PatMH18H2_3",  # SRA2
    "wu_PhiIH18H2_2",  # SRA2
    "wu_PhiIH6H2_3",  # SRA2
    "wu_PhiIH18H2_3",  # SRA2
    "wu_PhiIH12H2_2",  # SRA2
]


# append blacklist with verifications
verif_file = conf.project_path / "verification.csv"
try:
    blacklist.extend(
        pd.read_csv(verif_file, index_col=[0]).query("tag > 1")["trial"].tolist()
    )
except FileNotFoundError:
    print(f"{verif_file} not found.")

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")

    already_processed = [
        itrial.stem.replace("_StaticOptimization_activation", "").replace(
            "_StaticOptimization_force", ""
        )
        for itrial in conf.project_path.glob("*/3_static_optimization/*.sto")
    ]

    trials = []
    for ifile in (conf.project_path / iparticipant / "1_inverse_kinematic").glob(
        "*.mot"
    ):
        if ifile.stem not in blacklist and ifile.stem not in already_processed:
            trials.append(ifile)

    if not trials:
        continue

    for imodel in model_names:
        path_kwargs = {
            "model_input": f"{(conf.project_path / iparticipant / '_models' / imodel).resolve()}_scaled_markers.osim",
            "xml_input": f"{(conf.project_path / '_templates' / imodel).resolve()}_so.xml",
            "xml_output": f"{(conf.project_path / iparticipant / '_xml' / imodel).resolve()}_so.xml",
            "xml_forces": f"{(conf.project_path / '_templates' / 'forces_sensor.xml').resolve()}",
            "xml_actuators": f"{(conf.project_path / '_templates' / f'{imodel}_actuators.xml').resolve()}",
            "ext_forces_dir": f"{(conf.project_path / iparticipant / '0_forces').resolve()}",
            "sto_output": f"{(conf.project_path / iparticipant / '3_static_optimization').resolve()}",
        }
        import time

        start = time.time()
        StaticOptimization(
            **path_kwargs, mot_files=trials, prefix=imodel, low_pass=5, multi=False
        )
        print(time.time() - start)
