import json, os, traceback, sys

import inquirer

from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule
from prefect.infrastructure.container import DockerContainer, ImagePullPolicy

from flow import pipeline


# Which enviroment are we deploying to
valid_environments = ["local", "development", "production"]


class DeploymentEnvironmentException(Exception):
    "Raised when the deployment environment is not specified or cannot be found"
    pass


# Helper Functions
def notEnvironment(env):
    return env not in valid_environments


def replace_line_breaks_with_spaces(file_path):
    with open(file_path, "r") as file:
        content = file.read()
        content = content.replace("\n", " ")
        return content


try:
    environment = sys.argv[1]
    if notEnvironment(environment):
        raise IndexError
except IndexError:
    environment = os.getenv("DEPLOY_ENVIRONMENT")
    if notEnvironment(environment):
        question = [
            inquirer.List(
                "environment",
                message="Which workspace are you deploying to? (production/development/local)",
                choices=[*valid_environments, "none"],
            ),
        ]

        answer = inquirer.prompt(question)

        environment = answer["environment"]

        if environment == "none":
            print("Deployment cancelled.")
            exit()


# Get config file and parse it
f = open("config.json")
config = json.load(f)

az_block = Azure.load("flow-storage")

# Let's deploy it/them
for deployment in config["deployments"]:
    # Assume there is only one deployment
    deployment_name = "main"
    path = config["flow_name"]

    # However, if there is more than one deployment...
    if len(config["deployments"]) > 1:
        deployment_name = deployment["name"]
        path = f'{config["flow_name"]}/{deployment["name"]}'

    print(
        f"Deploying {deployment_name} to {path if environment != 'local' else environment}...",
        end="",
    )

    try:
        docker_block_name = (
            f'{config["flow_name"]}-{deployment_name}'.replace(" ", "-")
            .replace("_", "-")
            .lower()
        )
        docker_container_block = DockerContainer(
            name=docker_block_name,
            image="prefect_with_unixodbc:latest",
            auto_remove=True,
            # We want to always use our local image, so we NEVER pull it
            image_pull_policy=ImagePullPolicy.NEVER,
            env={
                "EXTRA_PIP_PACKAGES": f"adlfs {replace_line_breaks_with_spaces('requirements.txt')}"
            },
        )

        docker_container_block.save(docker_block_name, overwrite=True)

        # Don't set a schedule if there is none, or if this is NOT production
        if (
            "schedule" not in deployment
            or deployment["schedule"] == ""
            or environment != "production"
        ):
            deployment["schedule"] = None
        else:
            deployment["schedule"] = CronSchedule(cron=deployment["schedule"])

        d = Deployment.build_from_flow(
            flow=pipeline.with_options(name=config["flow_name"]),
            name=deployment_name,
            description=f"{config['description']} - {deployment['description']}",
            tags=config["tags"] + deployment["tags"],
            parameters=deployment["parameters"],
            work_queue_name="default",
            work_pool_name="default-agent-pool",
            apply=True,
            storage=az_block,
            path=path,
            schedule=deployment["schedule"],
            is_schedule_active=True
            if environment == "production" or deployment["schedule"] != None
            else False,
            infrastructure=docker_container_block,
        )

    except:
        print("FAILED!")
        print("Probably because of this:")
        traceback.print_exc()
        exit()
    else:
        print("SUCCESS!")
