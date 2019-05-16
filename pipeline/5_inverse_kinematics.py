"""
Inverse Kinematics
"""
import yaml
from pyosim import Conf
from pyosim import InverseKinematics

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

# [[i, p] for i, p in enumerate(participants)]

model_names = ["wu"]
offset = 0.05  # take .5 second before and after onsets

# take only trials containing...
subset = "H2"
for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")

    already_processed = [
        itrial.stem for itrial in conf.project_path.glob("*/1_inverse_kinematic/*.mot")
    ]

    trials = []
    for ifile in (conf.project_path / iparticipant / "0_markers").glob("*.trc"):
        if (
            subset in ifile.stem
            and f"{model_names[0]}_{ifile.stem}" not in already_processed
        ):
            trials.append(ifile)

    if not trials:
        continue

    onsets = conf.get_conf_field(iparticipant, ["onset"])
    onsets = {
        key: [values[0] - offset, values[1] + offset] for key, values in onsets.items()
    }

    for imodel in model_names:
        path_kwargs = {
            "model_input": f"{conf.project_path / iparticipant / '_models' / imodel}_scaled_markers.osim",
            "xml_input": f"{conf.project_path / '_templates' / imodel}_ik.xml",
            "xml_output": f"{conf.project_path / iparticipant / '_xml' / imodel}_ik.xml",
            "mot_output": f"{conf.project_path / iparticipant / '1_inverse_kinematic'}",
        }

        InverseKinematics(
            **path_kwargs, trc_files=trials, onsets=onsets, prefix=imodel, multi=False
        )
