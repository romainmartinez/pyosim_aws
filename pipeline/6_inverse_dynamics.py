"""
Inverse dynamics
"""

import yaml
from pyosim import Conf
from pyosim import InverseDynamics

aws_conf = yaml.safe_load(open("./conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

model_names = ["wu"]

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant: {iparticipant}")

    # ignore some trials
    blacklist_suffix = "0"
    trials = [
        ifile
        for ifile in (conf.project_path / iparticipant / "1_inverse_kinematic").glob(
            "*.mot"
        )
        if not ifile.stem.endswith(blacklist_suffix)
    ]

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
