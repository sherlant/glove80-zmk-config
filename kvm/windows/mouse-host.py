"""Switch a Logitech HID++ 2.0 device to another Easy-Switch host.

Usage: pythonw mouse-host.py <host 1-3> [device name substring]
Requires: pip install hidapi
"""
import sys

import hid

LOGITECH_VID = 0x046D
LONG_REPORT = 0x11
SWID = 0x0A
FEAT_DEVICE_NAME = 0x0005
FEAT_CHANGE_HOST = 0x1814
# Receiver slots (Unifying / Bolt) then 0xFF for a direct Bluetooth link
DEVICE_INDEXES = [1, 2, 3, 4, 5, 6, 0xFF]


def long_collections():
    """HID++ long-report collections: 0xFF00/2 behind a receiver, 0xFF43/0x0202 over BT."""
    for d in hid.enumerate(LOGITECH_VID, 0):
        if (d["usage_page"], d["usage"]) in ((0xFF00, 0x0002), (0xFF43, 0x0202)):
            yield d["path"]


def request(dev, idx, feat_idx, fn, params=b""):
    msg = bytes([LONG_REPORT, idx, feat_idx, (fn << 4) | SWID]) + params
    dev.write(msg.ljust(20, b"\x00"))
    for _ in range(20):
        r = dev.read(20, 200)
        if not r:
            return None
        if r[0] == LONG_REPORT and r[1] == idx and r[2] == feat_idx and r[3] == (fn << 4) | SWID:
            return bytes(r[4:])
        if r[2] == 0xFF and r[1] == idx:  # HID++ 2.0 error
            return None
    return None


def feature_index(dev, idx, feature):
    r = request(dev, idx, 0x00, 0, feature.to_bytes(2, "big"))
    return r[0] if r and r[0] else None


def device_name(dev, idx):
    fi = feature_index(dev, idx, FEAT_DEVICE_NAME)
    if fi is None:
        return ""
    r = request(dev, idx, fi, 0)
    length = r[0] if r else 0
    name = b""
    while len(name) < length:
        r = request(dev, idx, fi, 1, bytes([len(name)]))
        if not r:
            break
        name += r[: length - len(name)]
    return name.decode(errors="replace")


def main():
    host = int(sys.argv[1])
    wanted = sys.argv[2] if len(sys.argv) > 2 else "MX Master 3"
    for path in long_collections():
        dev = hid.device()
        try:
            dev.open_path(path)
        except OSError:
            continue
        try:
            for idx in DEVICE_INDEXES:
                if wanted.lower() not in device_name(dev, idx).lower():
                    continue
                fi = feature_index(dev, idx, FEAT_CHANGE_HOST)
                if fi is None:
                    continue
                # setCurrentHost (fn 1), 0-based host index; the device leaves without answering
                request(dev, idx, fi, 1, bytes([host - 1]))
                return 0
        finally:
            dev.close()
    print(f"{wanted} not found", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
