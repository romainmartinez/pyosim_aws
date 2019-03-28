"""
Create and update project
"""
import yaml
from pyoviz import FieldsAssignment
from pyosim import Conf, Project

aws_conf = yaml.safe_load(open("../conf_experts_novices.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

# create Project object
project = Project(path=aws_conf["path"]["project"][local_or_distant])
project.update_participants()

# Create a Conf object
conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])

# Check if all participants have a configuration file and update it in the project_sample's configuration file
conf.check_confs()

# add some data path in participants' conf file
participants = conf.get_participants_to_process()
d = {}
for iparticipant in participants:
    lat = "d" if conf.get_conf_field(iparticipant, ["laterality"]) == 'd' else "g"

    trials = f"{aws_conf['path']['data'][local_or_distant]}/irssten_{iparticipant}{lat}/trials"
    score = f"{aws_conf['path']['data'][local_or_distant]}/irssten_{iparticipant}{lat}/MODEL1000"
    mvc = f"{aws_conf['path']['mvc'][local_or_distant]}/irssten_{iparticipant}{lat}/mvc"

    d.update(
        {
            iparticipant: {
                "emg": {"data": [trials, mvc]},
                "analogs": {"data": [trials]},
                "markers": {"data": [trials, score]},
            }
        }
    )
conf.add_conf_field(d)

# assign channel fields to targets fields
for ikind, itarget in aws_conf["assignment"].items():
    previous = []

    for iparticipant in participants:
        print(f"\t{iparticipant} - {ikind}")
        if True or "assigned" not in conf.get_conf_field(iparticipant, [ikind]):
            fields = FieldsAssignment(
                directory=conf.get_conf_field(iparticipant, field=[ikind, "data"]),
                targets=itarget,
                kind=ikind,
                prefix=":",
                previous=previous,
            )
            print("\t\tdone")
            conf.add_conf_field({iparticipant: fields.output})

            for iass in fields.output[ikind]["assigned"]:
                if iass not in previous:
                    previous.append(iass)
