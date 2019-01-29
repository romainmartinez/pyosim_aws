"""
Export markers to trc
"""
from pathlib import Path
import yaml
import numpy as np
from pyosim import Conf, Markers3dOsim

aws_conf = yaml.safe_load(open("../conf.yml"))
local_or_distant = "distant" if aws_conf["distant_id"]["enable"] else "local"

conf = Conf(project_path=aws_conf["path"]["project"][local_or_distant])
participants = conf.get_participants_to_process()
conf.check_confs()

markers_labels = conf.get_conf_field(
    participant=participants[0], field=["markers", "targets"]
)

for i, iparticipant in enumerate(participants):
    print(f"\nparticipant #{i}: {iparticipant}")
    directories = conf.get_conf_field(
        participant=iparticipant, field=["markers", "data"]
    )
    assigned = conf.get_conf_field(
        participant=iparticipant, field=["markers", "assigned"]
    )

    for idir in directories:
        print(f"\n\tdirectory: {idir}")

        for itrial in Path(idir).glob("*.c3d"):
            blacklist = False
            # try participant's channel assignment
            for iassign in assigned:

                # special cases -----------------
                if itrial.stem[-2] == "d" and itrial.stem[-1] != "0":
                    blacklist = True
                    break
                elif itrial.stem in ["FabDH6H6_2", "FabDH6H6_3"]:
                    blacklist = True
                    break
                elif itrial.stem[-1] == "0":
                    iassign = [i if n < 43 else "" for n, i in enumerate(iassign)]

                # DEBUG ---------------

                # l = Markers3dOsim.from_c3d(itrial, prefix=":").get_labels
                # [i if i not in l else "" for i in iassign]

                # ---------------------

                nan_idx = [i for i, v in enumerate(iassign) if not v]
                if nan_idx:
                    iassign_without_nans = [i for i in iassign if i]
                else:
                    iassign_without_nans = iassign

                try:
                    markers = Markers3dOsim.from_c3d(
                        itrial, names=iassign_without_nans, prefix=":"
                    )

                    # replace pure zero by nans
                    markers[markers == 0] = np.nan

                    if nan_idx:
                        # if there is any empty assignment, fill the dimension with nan
                        for i in nan_idx:
                            markers = np.insert(markers, i, np.nan, axis=1)
                        print(f"\t{itrial.stem} (NaNs: {nan_idx})")
                    else:
                        print(f"\t{itrial.stem}")

                    # check if dimensions are ok
                    if not markers.shape[1] == len(iassign):
                        raise ValueError("Wrong dimensions")
                    break
                except IndexError:
                    print("WARNING")
                    markers = []

            if not blacklist:
                markers.get_labels = markers_labels
                trc_filename = f"{conf.project_path / iparticipant / '0_markers' / itrial.stem}.trc"
                markers.to_trc(filename=trc_filename)
