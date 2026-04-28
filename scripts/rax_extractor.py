import sys
import os
import struct

def find_all(data, pattern):
    off = 0
    res = []
    while True:
        off = data.find(pattern, off)
        if off == -1:
            return res
        res.append(off)
        off += 1

def read_string(data, off):
    end = off
    while end < len(data) and data[end] != 0:
        end += 1
    return data[off:end].decode("ascii", errors="ignore")

def scan_txr(data):
    entries = []

    for off in find_all(data, b"TXR\x00"):
        name = read_string(data, off + 0x10)

        entries.append({
            "offset": off,
            "name": name if ".txr" in name else f"txr_{off:08X}.bin"
        })

    return sorted(entries, key=lambda x: x["offset"])

def extract(data, entries, outdir):
    os.makedirs(outdir, exist_ok=True)

    for i in range(len(entries)):
        start = entries[i]["offset"]

        if i + 1 < len(entries):
            end = entries[i+1]["offset"]
        else:
            end = len(data)

        chunk = data[start:end]

        name = entries[i]["name"].replace("/", "_")
        path = os.path.join(outdir, name)

        with open(path, "wb") as f:
            f.write(chunk)

        print(f"[+] {name} -> {len(chunk)} bytes")

def run(file):
    with open(file, "rb") as f:
        data = f.read()

    print("[*] Scanning TXR...")
    entries = scan_txr(data)

    print(f"[+] Found {len(entries)} TXR")

    extract(data, entries, file + "_real")

if __name__ == "__main__":
    run(sys.argv[1])
