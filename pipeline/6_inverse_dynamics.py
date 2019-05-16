"""
Inverse dynamics
"""
import yaml
from pyosim import Conf
from pyosim import InverseDynamics

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

    trials = list(
        filter(
            None,
            [
                ifile if ifile.stem not in blacklist else ""
                for ifile in (
                    conf.project_path / iparticipant / "1_inverse_kinematic"
                ).glob("*.mot")
            ],
        )
    )

    for imodel in model_names:
        path_kwargs = {
            "model_input": f"{conf.project_path / iparticipant / '_models' / imodel}_scaled_markers.osim",
            "xml_input": f"{conf.project_path / '_templates' / imodel}_id.xml",
            "xml_output": f"{conf.project_path / iparticipant / '_xml' / imodel}_id.xml",
            "xml_forces": f"{conf.project_path / '_templates'}/forces_sensor.xml",
            "forces_dir": f"{conf.project_path / iparticipant / '0_forces'}",
            "sto_output": f"{(conf.project_path / iparticipant / '2_inverse_dynamic').resolve()}",
        }

        InverseDynamics(
            **path_kwargs, mot_files=trials, prefix=imodel, low_pass=10, multi=True
        )
