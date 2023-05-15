import json
from prefect import task, variables

@task
def read_flow_config():

    server_environment = variables.get("server_environment", default="development")

    f = open("config.json")
    return json.load(f)["flow_data"][server_environment]