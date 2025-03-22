import base64
import copy

import bittensor as bt
from bittensor_wallet import Keypair
from main.exceptions import InvalidSignatureException


class MetagraphManager:
    def __init__(self, config: bt.config) -> None:
        print("Metagraph init")
        self.config = copy.deepcopy(config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = bt.metagraph(netuid=self.config.netuid, network=self.subtensor.network, sync=False)
        self.metagraph.sync(subtensor=self.subtensor)
        print("Metagraph init done")

    def verify_signature(self, hotkey: str, nonce: int, signature: str) -> None:
        uid = self._get_neuron_uid(hotkey)
        if uid is None:
            err = f"{hotkey} is not registered"
            bt.logging.error(err)
            raise InvalidSignatureException(err)

        if (
            # todo To env
            hotkey != "5E7eSeRr2aHzCV7SkY4a2Pi5NXHrU4anZz3phEQgn4HCen2B"  # subnet owner
            and self.metagraph.S[uid].item() < self.config.min_stake_to_set_weights
        ):
            err = f"{hotkey} is not a validator. Stake: {self.metagraph.S[uid].item()}"
            bt.logging.error(err)
            raise InvalidSignatureException(err)

        # TODO: check nonce

        # signature = base64.b64encode(dendrite.keypair.sign(message)).decode(encoding="utf-8")

        keypair = Keypair(ss58_address=hotkey)
        message = f"{nonce}{hotkey}"
        result = bool(keypair.verify(message, base64.b64decode(signature.encode(encoding="utf-8"))))
        if not result:
            raise InvalidSignatureException("signature verification failed.")

    def _get_neuron_uid(self, hotkey: str) -> int | None:
        for neuron in self.metagraph.neurons:
            if neuron.hotkey == hotkey:
                return int(neuron.uid)

        return None
