import yaml
import os
import argparse
from pathlib import Path


class Distant:
    def __init__(self):
        self.aws_conf = yaml.safe_load(open("./conf.yml"))

    def copy_local_to_distant(self):
        command = self.copy(
            from_dir=self.aws_conf["path"]["project"]["local"],
            to_dir=f'{self.aws_conf["distant_id"]["id"]}:{Path(self.aws_conf["path"]["project"]["distant"]).parent}',
        )
        print(command)
        os.system(command)

    def copy_distant_to_local(self):
        command = self.copy(
            from_dir=f'{self.aws_conf["distant_id"]["id"]}:{self.aws_conf["path"]["project"]["distant"]}',
            to_dir=Path(self.aws_conf["path"]["project"]["local"]).parent,
        )
        print(command)
        os.system(command)

    def copy(self, from_dir, to_dir):
        # f'scp -r -i {self.aws_conf["distant_id"]["pem"]} {from_dir} {to_dir}'
        return f'rsync -avz -e "ssh -i {self.aws_conf["distant_id"]["pem"]}" {from_dir} {to_dir} --delete'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--function")
    fonction_called = parser.parse_args().function

    distant = Distant()

    if fonction_called == "copy_local_to_distant":
        distant.copy_local_to_distant()
    elif fonction_called == "copy_distant_to_local":
        distant.copy_distant_to_local()
