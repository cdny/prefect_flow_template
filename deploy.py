import json, os, traceback, subprocess, sys

from prefect.deployments import Deployment
from prefect.filesystems import Azure
from prefect.server.schemas.schedules import CronSchedule

from flow import pipeline

# Which enviroment are we deploying to
try:
    environment = sys.argv[1]
    if environment not in ["production", "development"]:
        raise IndexError
except IndexError:
    print("Which work queue are you deploying to? (production/development)")
    exit()


# Get config file and parse it
f = open("config.json")
config = json.load(f)

# Set up ENV variables for deployment
subprocess.run(
    ["echo", f"DATABASE={config['deploy_to_database']}",">>","$GITHUB_ENV"], 
    ["echo", f"WORK_QUEUE={environment}", ">>","$GITHUB_ENV"]
)

az_block = Azure.load("flow-storage")
migrate_database = False

for deployment in config["deployments"]:
    # Assume there is only one deployment
    deployment_name = "main"
    path = config["flow_name"]

    # However, if there is more than one deployment...
    if len(config["deployments"]) > 1:
        deployment_name = deployment["name"]
        path = f'{config["flow_name"]}/{deployment["name"]}'

    print(f"Deploying {deployment_name} to {path}...", end='')

    try:
        d = Deployment.build_from_flow(
            flow=pipeline.with_options(name=config["flow_name"]),
            name=deployment_name,
            description=f"{config['description']} - {deployment['description']}",
            tags=config["tags"] + deployment["tags"],
            parameters=deployment["parameters"],
            work_queue_name=environment,
            work_pool_name=f"{environment}-work-pool",
            apply=True,
            storage=az_block,
            path=path,
            schedule=(
                CronSchedule(cron=deployment["schedule"], timezone="America/New_York")
            ),
            is_schedule_active=True,
        )
    except:
        print("FAILED!")
        print("Probably because of this:")
        traceback.print_exc()
        exit()
    else:
        print("SUCCESS!")
        if "sql_deploy_to" in config:
            migrate_database = True
    
    # TO DO
    # Migrate Database
    # if migrate == True:
    #     url = os.getenv("DATABASE_URL")
    #     username = os.getenv("DATABASE_USERNAME")
    #     password = os.getenv("DATABASE_PASSWORD")

    #     cmd_str = f"docker run --rm -v sql:/flyway/sql flyway/flyway -url=jdbc:{url} -user={username} -password={password} migrate"
    #     subprocess.run(cmd_str, shell=True)

    
