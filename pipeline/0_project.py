import os
import shutil

from pathlib import Path

from pyoviz import FieldsAssignment
from pyosim import Conf, Project

import yaml
conf = yaml.safe_load(open('../conf.yml'))

# ACTUAL PARTICIPANT TO PROCESS #
participant_to_do = 5

# create Project object
project = Project(path=conf['path']['project'])

project.update_participants(participant_to_do)

# Create a Conf object
conf = Conf(project_path=PROJECT_PATH)

# Check if all participants have a configuration file and update it in the project_sample's configuration file
conf.check_confs(participant_to_do)

# add some data path in participants' conf file
participants = conf.get_participants_to_process()
d = {}
for iparticipant in participants:
    pseudo_in_path = (
            iparticipant[0].upper() + iparticipant[1:-1] + iparticipant[-1].upper()
    )
    trials = f"{LOCAL_DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/trials"
    score = f"{LOCAL_DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/MODEL2"
    mvc = f"{LOCAL_MVC_PARENT_PATH}/{pseudo_in_path}"

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
for ikind, itarget in targets.items():
    for iparticipant in participants:
        fields = FieldsAssignment(
            directory=conf.get_conf_field(iparticipant, field=[ikind, "data"]),
            targets=itarget,
            kind=ikind,
        )
        conf.add_conf_field({iparticipant: fields.output})

actual_participant = participants[0]
pseudo_in_path = (
        actual_participant[0].upper()
        + actual_participant[1:-1]
        + actual_participant[-1].upper()
)
trials_local = f"{LOCAL_DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/trials/"
score_local = f"{LOCAL_DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/MODEL2/"
mvc_local = f"{LOCAL_MVC_PARENT_PATH}/{pseudo_in_path}/"
trials_distant = f"{DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/"
score_distant = f"{DATA_PARENT_PATH}/IRSST_{pseudo_in_path}d/"
mvc_distant = f"{MVC_PARENT_PATH}/"

if run_analyses_on_distant_computer:
    # CHANGE PATHS SO THE DISTANT JSON HAS A VALID FILE
    filename = conf.get_conf_path(actual_participant)
    file = open(filename, "r")
    data = json.load(file)
    file.close()
    data["conf_file"] = [
        f"{BASE_PROJECT_DISTANT}results/{actual_participant}/_conf.json/"
    ]
    data["emg"]["data"] = [
        f"{trials_distant}trials/",
        f"{mvc_distant}{pseudo_in_path}/",
    ]
    data["analogs"]["data"] = [f"{trials_distant}trials/"]
    data["markers"]["data"] = [f"{trials_distant}trials/", f"{score_distant}MODEL2/"]

    # data.update(d)
    file = open(filename, "w+")
    json.dump(data, file)
    file.close()

    # Do the same for the other conf file
    conf.project_conf.loc[
        participant_to_do, "conf_file"
    ] = f"{BASE_PROJECT_DISTANT}results/{actual_participant}/_conf.json"
    conf.project_conf.to_csv(conf.conf_path, index=False)

    # Call the script that does the interface with distant computer
    os.system(
        f"./ceinms_runner.sh {trials_local} {score_local} {mvc_local} {trials_distant} {score_distant} "
        f"{mvc_distant} {distant_ip} {pem_file_path} {BASE_PROJECT_DISTANT} log_{actual_participant}.log {debug}"
    )
else:
    os.system(f"cp -r _models results")
    os.system(f"cp -r _templates results")
