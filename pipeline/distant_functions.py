import yaml
import os
import argparse


class Distant:
    def __init__(self):
        self.aws_conf = yaml.safe_load(open("./conf.yml"))

    def copy_local_to_distant(self):
        print("Copying local project to distant computer...")
        command = self.copy(
            from_dir=self.aws_conf["path"]["project"]["local"], to_dir="~"
        )
        print(command)
        os.system(command)
        print("Done.")

    def copy(self, from_dir, to_dir):
        return f'scp -r -i {self.aws_conf["distant_id"]["pem"]} {from_dir} {self.aws_conf["distant_id"]["id"]}:{to_dir}'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--function", default="copy_local_to_distant")
    fonction_called = parser.parse_args().function

    distant = Distant()

    if fonction_called == "copy_local_to_distant":
        distant.copy_local_to_distant()
