"""Read the multihash digest out of a base32 CIDv1 (the CURBy beacon value)."""

import base64
import binascii


def _read_varint(data, offset):
    """Read one unsigned LEB128 varint, returning (value, next offset)."""
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7


def digest(cid):
    """Return the multihash digest of a base32 CIDv1."""
    if not cid.startswith("b"):
        raise ValueError("unsupported CID multibase")
    payload = cid[1:].upper()
    payload += "=" * (-len(payload) % 8)
    try:
        raw = base64.b32decode(payload)
        version, offset = _read_varint(raw, 0)
        _, offset = _read_varint(raw, offset)  # multicodec
        _, offset = _read_varint(raw, offset)  # multihash function code
        length, offset = _read_varint(raw, offset)
    except (IndexError, binascii.Error) as cause:
        raise ValueError("malformed CID") from cause
    if version != 1:
        raise ValueError("unsupported CID version")
    value = raw[offset:offset + length]
    if length == 0 or len(value) != length:
        raise ValueError("malformed multihash digest")
    return value
