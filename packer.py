import json
import struct
import sys
import zlib

DEFAULT_HEADER = bytes.fromhex("02db030000")


def pack_sts(json_path, output_sts):
    with open(json_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    entries = doc.get("entries", [])
    raw = bytearray()
    raw += struct.pack("<I", len(entries))

    for e in entries:
        name_bytes = str(e["name"]).encode("utf-8") + b"\x00"
        raw += struct.pack("<I", len(name_bytes))
        raw += name_bytes

        typ = e["type"]
        val = e.get("value")

        if typ == "float":
            raw += b"\x01"
            raw += struct.pack("<f", float(val))
        elif typ == "string":
            str_bytes = str(val).encode("utf-8") + b"\x00"
            raw += b"\x02"
            raw += struct.pack("<I", len(str_bytes))
            raw += str_bytes
        elif typ == "bool":
            raw += b"\x03"
            raw += b"\x01" if bool(val) else b"\x00"

    header_hex = doc.get("header_hex")
    header = bytes.fromhex(header_hex) if header_hex else DEFAULT_HEADER
    compressed = zlib.compress(bytes(raw), level=9)

    with open(output_sts, "wb") as f:
        f.write(header + compressed)

    print(f"ГОТОВО! Запаковано {len(entries)} записей в:\n{output_sts}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Запуск: python packer.py /путь/к/файлу.json")
        sys.exit(1)

    json_file = sys.argv[1]
    out_sts = (
        json_file[:-5] if json_file.endswith(".json") else json_file + ".sts"
    )
    pack_sts(json_file, out_sts)
    