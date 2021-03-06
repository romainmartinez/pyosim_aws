"""
Muscle analysis
"""
import yaml
from pyosim import Conf
from pyosim import MuscleAnalysis
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
]

# append blacklist with verifications
verif_file = conf.project_path / "verification.csv"
try:
    blacklist.extend(
        pd.read_csv(verif_file, index_col=[0]).query("tag > 1")["trial"].tolist()
    )
except FileNotFoundError:
    print(f"{verif_file} not found.")

for iparticipant in participants[-2:]:
    print(f"\nparticipant: {iparticipant}")

    already_processed = [
        itrial.stem.replace("_MuscleAnalysis_Length", "")
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
            "xml_input": f"{(conf.project_path / '_templates' / imodel).resolve()}_ma.xml",
            "xml_output": f"{(conf.project_path / iparticipant / '_xml' / imodel).resolve()}_ma.xml",
            "xml_forces": f"{(conf.project_path / '_templates' / 'forces_sensor.xml').resolve()}",
            "xml_actuators": f"{(conf.project_path / '_templates' / f'{imodel}_actuators.xml').resolve()}",
            "ext_forces_dir": f"{(conf.project_path / iparticipant / '0_forces').resolve()}",
            "sto_output": f"{(conf.project_path / iparticipant / '4_muscle_analysis').resolve()}",
        }

        MuscleAnalysis(
            **path_kwargs,
            mot_files=trials,
            prefix=imodel,
            low_pass=5,
            remove_empty_files=True,
            multi=True,
            contains=["_FiberVelocity", "MomentArm_shoulder", "_Length"],
        )
