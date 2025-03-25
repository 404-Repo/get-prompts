import argparse

import bittensor as bt


def read_config() -> bt.config:
    parser = argparse.ArgumentParser()
    bt.logging.add_args(parser)
    bt.subtensor.add_args(parser)

    parser.add_argument("--netuid", type=int, help="Subnet netuid", default=17)
    parser.add_argument("--port", type=int, help="Service port", default=8093)
    parser.add_argument("--api-key", type=str, help="API-KEY to auth prompt generators.", default="")
    parser.add_argument(
        "--default_text_prompt_file",
        type=str,
        help="File with default text prompts.",
        default="resources/texts/default_prompts.txt",
    )
    parser.add_argument(
        "--default_image_prompt_dir",
        type=str,
        help="Folder with image prompts.",
        default="resources/images/default",
    )
    parser.add_argument(
        "--text_prompt_batch_size", type=int, help="Number of text prompts to return to validators.", default=100000
    )
    parser.add_argument(
        "--text_prompt_storage_size",
        type=int,
        help="Number of text prompts to save in memory for valiators.",
        default=100000,
    )
    parser.add_argument(
        "--image_prompt_batch_size", type=int, help="Number of image prompts to return to validators.", default=2500
    )
    parser.add_argument(
        "--submitted_image_prompt_buffer_size",
        type=int,
        help="Number of submitted image prompts to save in memory.",
        default=10000,
    )
    parser.add_argument(
        "--min_stake_to_set_weights",
        type=int,
        help="Minimal required stake to set weights.",
        default=10000,
    )
    parser.add_argument(
        "--image_prompt_chunk_size",
        type=int,
        help="Chunk size used to send image files.",
        default=1024 * 1024,
    )

    return bt.config(parser)


# todo Handle config in pydantic object and create bt.config from it.
config = read_config()


# application
# default parameter for
