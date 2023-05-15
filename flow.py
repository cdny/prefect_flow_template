

from prefect import flow, task, get_run_logger

from etlcore.Blocks.KeyVault import KeyVault

from tasks.read_config import read_flow_config


azure_key_vault_block = KeyVault.load("key-vault")

# Large Tasks should go in the /tasks folder and be imported

@flow
def pipeline():
    logging = get_run_logger()
    config = read_flow_config()
    secrets = azure_key_vault_block.get_secrets()

    logging.info(config, secrets)

    return True


if __name__ == "__main__":

    pipeline()
