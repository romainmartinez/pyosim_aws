from pathlib import Path

# Path ----------------------
PROJECT_PATH = Path("project_sample")
CONF_TEMPLATE = PROJECT_PATH / "_conf.csv"
MODELS_PATH = PROJECT_PATH / "_models"
TEMPLATES_PATH = PROJECT_PATH / "_templates"

DATA_PATH = {
    "local": "/home/laboratoire/mnt/F/Data/Shoulder/RAW",
    "distant": "/home/ubuntu/data/RAW",
}
MVC_PATH = {
    "local": "/home/laboratoire/mnt/E/Projet_MVC/data/C3D_original_files/irsst_hf",
    "distant": "/home/ubuntu/data/mvc",
}

CALIBRATION_MATRIX = PROJECT_PATH / "forces_calibration_matrix.csv"

# Distant ID ----------------
ID = "ec2-34-212-104-202.us-west-2.compute.amazonaws.com"
PEM = "~/.ssh/bimec29-kinesio.pem"

# Variables -----------------
ASSIGNMENT = {
    "emg": [
        "deltant",
        "deltmed",
        "deltpost",
        "biceps",
        "triceps",
        "uptrap",
        "lotrap",
        "serratus",
        "ssp",
        "isp",
        "subs",
        "pect",
        "latissimus",
    ],
    "analogs": ["Fx", "Fy", "Fz", "Mx", "My", "Mz"],
    "markers": [
        "ASISl",
        "ASISr",
        "PSISl",
        "PSISr",
        "STER",
        "STERl",
        "STERr",
        "T1",
        "T10",
        "XIPH",
        "CLAVm",
        "CLAVl",
        "CLAV_ant",
        "CLAV_post",
        "CLAV_SC",
        "ACRO_tip",
        "SCAP_AA",
        "SCAPl",
        "SCAPm",
        "SCAP_CP",
        "SCAP_RS",
        "SCAP_SA",
        "SCAP_IA",
        "CLAV_AC",
        "DELT",
        "ARMl",
        "ARMm",
        "ARMp_up",
        "ARMp_do",
        "EPICl",
        "EPICm",
        "LARMm",
        "LARMl",
        "LARM_elb",
        "LARM_ant",
        "STYLr",
        "STYLr_up",
        "STYLu",
        "WRIST",
        "INDEX",
        "LASTC",
        "MEDH",
        "LATH",
        "boite_gauche_ext",
        "boite_gauche_int",
        "boite_droite_int",
        "boite_droite_ext",
        "boite_avant_gauche",
        "boite_avant_droit",
        "boite_arriere_droit",
        "boite_arriere_gauche",
    ],
}
