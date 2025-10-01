import argparse

import bittensor as bt


def read_config() -> bt.config:
    parser = argparse.ArgumentParser()
    bt.logging.add_args(parser)
    bt.subtensor.add_args(parser)

    parser.add_argument("--netuid", type=int, help="Subnet netuid", default=17)
    parser.add_argument(
        "--min_stake_to_set_weights",
        type=int,
        help="Minimal required stake to set weights.",
        default=10000,
    )

    return bt.config(parser)
