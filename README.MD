# Prefect Flow Template



## The Boiler Plate
This repository is the template (starting point) for creating a new Prefect 2 flow. Currently this is version 1

## Naming Conventions

### Repository Name
The name for the flow repository should follow this convention:

`flow_[NAME]_[ORG]`

Where NAME is the name of the flow and ORG is the organization to which it belongs.

The options for ORG are:

- mso
- cdny
- php

## The `config.json` file

The following is the required format for the `config.json` file:

```
{
    "template_version": 1,
    "flow_name": "",
    "deployments": [
        {
            "name": "main",
            "schedule": "0 7 * * 1",
            "description": "",
            "tags": [],
            "parameters": {}
        }
    ],
    "description": "",
    "tags": [
        ""
    ],
    "deploy_to_database": "",
    "flow_data": {
        "production": {},
        "development": {}
    }
}
```

The `flow_data` section, although it requires the `production` and `development` objects, those object can be customized for the specific flow. Any custom data should be document in the 

## Getting started

### Login in Prefect
Once the dev container is up, login to prefect cloud (inside the container):

1. Run `login to prefect cloud`
2. Choose `Login with browser` and follow the promps
3. Choose a worspace to work in (choose your local workspace if you're running from your local machine)

### Run your flow
Once connected to Prefect Cloud, run the flow with:

`python flow.py`

In order to debug a flow, using breakpoints, use Visual Studio Code's debugger and select the `Prefect: Run Flow` option.

### Tags
The following tags are legal:

- cdny
- php
- mso
- internal 
- report

If tags need to be added to this list, let's discuss.

## Flow Specific Items
This section is to document specifics for the flow, including custom data, custom parameters, etc.

### `config.json`
Add required data, and explain what it's used for below
```
"flow_data": {
    "production": {},
    "development": {}
} 
```

## TO DO
- [ ] Document what the keys in the `config.json` file mean
- [ ] Migrate Database Objects for the Flow during deployment
- [ ] When the flow is run locally, add a name to the flow so it's not just "pipeline"
- [ ] Make the schedule a deployment optional
