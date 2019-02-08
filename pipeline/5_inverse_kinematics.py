"""
Inverse Kinematics
"""
import yaml
from pyosim import Conf
from pyosim import InverseKinematics

aws_conf = yaml.safe_load(open("./conf_experts_novices.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

model_names = ["wu"]
offset = 0.05  # take .5 second before and after onsets

# take only trials containing...
subset = "H2"

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")

    trials = [
        ifile
        for ifile in (conf.project_path / iparticipant / "0_markers").glob("*.trc")
        if subset in ifile.stem
    ]
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
            **path_kwargs, trc_files=trials, onsets=onsets, prefix=imodel, multi=True
        )
