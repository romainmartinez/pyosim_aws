"""
Static optimization
"""
import yaml
from pyosim import Conf
from pyosim import StaticOptimization

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

model_names = ["wu"]  # , 'das']

for i, iparticipant in enumerate(["sarc"]):
    print(f"\nparticipant #{i}: {iparticipant}")

    trials = [
        ifile
        for ifile in (conf.project_path / iparticipant / "1_inverse_kinematic").glob(
            "*.mot"
        )
    ]

    for imodel in model_names:
        path_kwargs = {
            "model_input": f"{(conf.project_path / iparticipant / '_models' / imodel).resolve()}_scaled_markers.osim",
            "xml_input": f"{(conf.project_path / '_templates' / imodel).resolve()}_so.xml",
            "xml_output": f"{(conf.project_path / iparticipant / '_xml' / imodel).resolve()}_so.xml",
            "xml_forces": f"{(conf.project_path / '_templates' / 'forces_sensor.xml').resolve()}",
            "xml_actuators": f"{(conf.project_path / '_templates' / f'{imodel}_actuators.xml').resolve()}",
            "ext_forces_dir": f"{(conf.project_path / iparticipant / '0_forces').resolve()}",
            "sto_output": f"{(conf.project_path / iparticipant / '3_static_optimization').resolve()}",
        }

        StaticOptimization(
            **path_kwargs, mot_files=trials, prefix=imodel, low_pass=5, multi=True
        )
