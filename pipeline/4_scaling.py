"""
Scaling
"""
import yaml
from pyosim import Conf
from pyosim import Scale

aws_conf = yaml.safe_load(open("../conf_experts_novices.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
conf.check_confs()
participants = conf.get_participants_to_process()

model_names = ["wu"]
WU_MASS_FACTOR = 24.385 / 68.2

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")
    lat = "d" if conf.get_conf_field(iparticipant, ["laterality"]) == 'd' else "g"
    static_path = f"{conf.project_path / iparticipant / '0_markers' / 'irssten_'}{iparticipant}{lat}0.trc"
    mass = conf.get_conf_field(iparticipant, ["mass"])
    height = conf.get_conf_field(iparticipant, ["height"])

    for imodel in model_names:
        if imodel[:2] == "wu":
            # mass of the upper limb + torso
            mass = mass * WU_MASS_FACTOR
            # TODO: mass scaling should be verified

        path_kwargs = {
            "model_input": f"{conf.project_path / '_models' / imodel}.osim",
            "model_output": f"{conf.project_path / iparticipant / '_models' / imodel}_scaled.osim",
            "xml_input": f"{conf.project_path / '_templates' / imodel}_scaling.xml",
            "xml_output": f"{conf.project_path / iparticipant / '_xml' / imodel}_scaled.xml",
            "static_path": static_path,
            "add_model": f"{conf.project_path / '_models' / 'box.osim'}",
        }

        Scale(**path_kwargs, mass=mass, height=height * 10, remove_unused=False)
        # TODO: get total squared error + marker error + max
