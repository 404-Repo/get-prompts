from pydantic import BaseModel


class MetagraphData(BaseModel):
    hotkey: str
    nonce: int
    signature: str
