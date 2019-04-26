"""
Scaling
"""
import yaml
from pyosim import Conf
from pyosim import Scale

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
conf.check_confs()
participants = conf.get_participants_to_process()

model_names = ["wu"]
WU_MASS_FACTOR = 24.385 / 68.2

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")
    pseudo_in_path = (
        iparticipant[0].upper() + iparticipant[1:-1] + iparticipant[-1].upper()
    )
    static_path = f"{conf.project_path / iparticipant / '0_markers' / 'IRSST_'}{pseudo_in_path}d0.trc"
    mass = conf.get_conf_field(iparticipant, ["mass"])
    height = conf.get_conf_field(iparticipant, ["height"])

    for imodel in model_names:
        if imodel[:2] == "wu":
            # mass of the upper limb + torso
            mass = mass * WU_MASS_FACTOR

        path_kwargs = {
            "model_input": f"{conf.project_path / '_models' / imodel}.osim",
            "model_output": f"{conf.project_path / iparticipant / '_models' / imodel}_scaled.osim",
            "xml_input": f"{conf.project_path / '_templates' / imodel}_scaling.xml",
            "xml_output": f"{conf.project_path / iparticipant / '_xml' / imodel}_scaled.xml",
            "static_path": static_path,
            "add_model": f"{conf.project_path / '_models' / 'box.osim'}",
        }

        Scale(**path_kwargs, mass=mass, height=height * 10, remove_unused=False)
