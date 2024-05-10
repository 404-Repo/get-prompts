import base64
import copy

import bittensor as bt
from substrateinterface import Keypair


class Metagraph:
    def __init__(self, config: bt.config) -> None:
        self.config = copy.deepcopy(config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = bt.metagraph(netuid=self.config.netuid, network=self.subtensor.network, sync=False)
        self.metagraph.sync(subtensor=self.subtensor)

    def verify_signature(self, hotkey: str, nonce: int, signature: str) -> bool:
        uid = self._get_neuron_uid(hotkey)
        if uid is None:
            bt.logging.error(f"{hotkey} is not registered")
            return False

        if (
            hotkey != "5E7eSeRr2aHzCV7SkY4a2Pi5NXHrU4anZz3phEQgn4HCen2B"  # subnet owner
            and self.metagraph.S[uid].item() < self.config.min_stake_to_set_weights
        ):
            bt.logging.error(f"{hotkey} is not a validator. Stake: {self.metagraph.S[uid].item()}")
            return False

        # TODO: check nonce

        # signature = base64.b64encode(dendrite.keypair.sign(message)).decode(encoding="utf-8")

        keypair = Keypair(ss58_address=hotkey)
        message = f"{nonce}{hotkey}"
        return bool(keypair.verify(message, base64.b64decode(signature.encode(encoding="utf-8"))))

    def _get_neuron_uid(self, hotkey: str) -> int | None:
        for neuron in self.metagraph.neurons:
            if neuron.hotkey == hotkey:
                return int(neuron.uid)

        return None
