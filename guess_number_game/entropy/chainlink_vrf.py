"""Chainlink VRF adapter: reads a fulfilled random word from a chain over JSON-RPC.

Chainlink VRF has no public REST endpoint — the randomness lives on-chain — so
this adapter calls a VRF consumer contract through `eth_call`. Point it at your
own node and consumer with the environment variables below.
"""

import os

from .. import transport
from .base import RandomSource
from .mapping import pick_from_bytes

RPC_ENV = "GUESSGAME_VRF_RPC"
CONTRACT_ENV = "GUESSGAME_VRF_TO"
CALLDATA_ENV = "GUESSGAME_VRF_DATA"


class ChainlinkVrfSource(RandomSource):
    key = "chainlink"
    labels = {"zh": "Chainlink VRF", "en": "Chainlink VRF"}

    def __init__(self, rpc_url=None, contract=None, calldata=None, environ=None):
        env = os.environ if environ is None else environ
        self._rpc_url = rpc_url or env.get(RPC_ENV)
        self._contract = contract or env.get(CONTRACT_ENV)
        self._calldata = calldata or env.get(CALLDATA_ENV, "0x")

    def fetch(self, minimum, maximum, deadline):
        if not self._rpc_url or not self._contract:
            raise ValueError(
                "Chainlink VRF needs {rpc} and {contract}".format(
                    rpc=RPC_ENV, contract=CONTRACT_ENV
                )
            )
        response = transport.post_json(
            self._rpc_url,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_call",
                "params": [
                    {"to": self._contract, "data": self._calldata},
                    "latest",
                ],
            },
            deadline,
        )
        result = response.get("result")
        if not result or result == "0x":
            raise ValueError("Chainlink VRF returned no random word")
        return pick_from_bytes(bytes.fromhex(result[2:]), minimum, maximum)
