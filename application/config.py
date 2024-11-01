import argparse

import bittensor as bt


def read_config() -> bt.config:
    parser = argparse.ArgumentParser()
    bt.logging.add_args(parser)
    bt.subtensor.add_args(parser)

    parser.add_argument("--netuid", type=int, help="Subnet netuid", default=17)
    parser.add_argument("--port", type=int, help="Service port", default=80)
    parser.add_argument("--api-key", type=str, help="API-KEY to auth prompt generators.", default="")
    parser.add_argument(
        "--resources",
        type=str,
        help="Folder with prompts. Used to load default_prompts and backup actual prompts.",
        default="resources",
    )
    parser.add_argument(
        "--backup_interval", type=int, help="Time interval to save new dataset to a file.", default=60 * 60
    )
    parser.add_argument(
        "--sufficient_batch_size", type=int, help="Number of prompts to return to validators.", default=100000
    )
    parser.add_argument(
        "--min_stake_to_set_weights",
        type=int,
        help="Minimal required stake to set weights.",
        default=1,
    )
    
    # GCP PostgreSQL settings
    parser.add_argument(
        "--pg_host",
        type=str,
        help="PostgreSQL host",
        required=True
    )
    parser.add_argument(
        "--pg_port",
        type=int,
        help="PostgreSQL port",
        default=5432
    )
    parser.add_argument(
        "--pg_database",
        type=str,
        help="PostgreSQL database name",
        required=True
    )
    parser.add_argument(
        "--pg_user",
        type=str,
        help="PostgreSQL user",
        required=True
    )
    parser.add_argument(
        "--pg_password",
        type=str,
        help="PostgreSQL password",
        required=True
    )

    return bt.config(parser)


config = read_config()
print(config)
