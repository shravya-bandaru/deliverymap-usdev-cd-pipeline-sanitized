import yaml
import click
from pprint import pprint
import sys


def to_camel_case(variable: str):
    camel_case = "".join(x.capitalize() for x in variable.lower().split("_"))
    return camel_case[0].lower() + camel_case[1:]


@click.command()
@click.option("--service-name", default="concourse-api")
@click.option(
    "--manifest",
    default="C:\\Users\\ktrujillo003\\Documents\\DevOps\\adv\\administration\\scripts\\python\\utilities\\deployment.yaml",
)
def main(service_name, manifest):

    with open(manifest, "r") as manifest:
        try:
            data = yaml.load(manifest, Loader=yaml.FullLoader)
            containers = list(data["spec"]["template"]["spec"]["containers"])
            print(containers)
            app: list = list(
                filter(lambda filter: filter["name"] == service_name, containers)
            )
            app = dict(app[0])
            print(app)
            envs = list(filter(lambda filter: "valueFrom" in filter.keys(), app["env"]))
            print(envs)
            secrets = list(
                filter(
                    lambda filter: "secretKeyRef" in filter["valueFrom"].keys(), envs
                )
            )
            list_secret_name = list()
            print(secrets)
            for secret in secrets:
                list_secret_name.append(
                    to_camel_case(secret["valueFrom"]["secretKeyRef"]["key"])
                )
            print(
                f'##vso[task.setvariable variable=APP_SECRETS]{str.join(",",list_secret_name)}'
            )

        except yaml.YAMLError as exc:
            if hasattr(exc, "problem_mark"):
                mark = exc.problem_mark
                print(f"Error position: ({mark.line+1}, {mark.column+1})")
                sys.exit(1)


if __name__ == "__main__":
    main()
