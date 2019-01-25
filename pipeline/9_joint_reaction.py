"""
Joint reaction
"""
import yaml
from pyosim import Conf
from pyosim import JointReaction

aws_conf = yaml.safe_load(open("./conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

model_names = ["wu"]

for iparticipant in participants:
    print(f"\nparticipant: {iparticipant}")

    trials = [
        ifile
        for ifile in (conf.project_path / iparticipant / "1_inverse_kinematic").glob(
            "*.mot"
        )
    ]

    for imodel in model_names:
        path_kwargs = {
            "model_input": f"{(conf.project_path / iparticipant / '_models' / imodel).resolve()}_scaled_markers.osim",
            "xml_input": f"{(conf.project_path / '_templates' / imodel).resolve()}_jr.xml",
            "xml_output": f"{(conf.project_path / iparticipant / '_xml' / imodel).resolve()}_jr.xml",
            "xml_actuators": f"{(conf.project_path / '_templates' / f'{imodel}_actuators.xml').resolve()}",
            "muscle_forces_dir": f"{(conf.project_path / iparticipant / '3_static_optimization').resolve()}",
            "sto_output": f"{(conf.project_path / iparticipant / '5_joint_reaction_force').resolve()}",
            "enforce_analysis": True,
        }

        JointReaction(
            **path_kwargs,
            mot_files=trials,
            prefix=imodel,
            low_pass=5,
            remove_empty_files=True,
            multi=True,
        )
