import json
import struct
import sys
import zlib


def unpack_sts(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 7:
        raise ValueError("Файл слишком короткий")
    prefix = data[:5]
    if data[5] != 0x78:
        raise ValueError("Не найден zlib заголовок (0x78)")
    raw = zlib.decompress(data[5:])

    off = 0
    count = struct.unpack_from("<I", raw, off)[0]
    off += 4
    records = []

    for i in range(count):
        name_len = struct.unpack_from("<I", raw, off)[0]
        off += 4
        name_raw = raw[off : off + name_len]
        off += name_len
        name = name_raw[:-1].decode("utf-8", errors="replace")

        typ = raw[off]
        off += 1

        if typ == 1:
            val = struct.unpack_from("<f", raw, off)[0]
            off += 4
            t_name = "float"
        elif typ == 2:
            val_len = struct.unpack_from("<I", raw, off)[0]
            off += 4
            val_raw = raw[off : off + val_len]
            off += val_len
            val = val_raw[:-1].decode("utf-8", errors="replace")
            t_name = "string"
        elif typ == "bool" or typ == 3:
            val = bool(raw[off])
            off += 1
            t_name = "bool"
        else:
            raise ValueError(f"Неизвестный тип {typ}")

        records.append({"name": name, "type": t_name, "value": val})

    # Захватываем всё, что осталось после записей
    tail_bytes = raw[off:]
    tail_hex = tail_bytes.hex() if tail_bytes else ""

    return prefix.hex(), records, tail_hex


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Запуск: python unpacker.py /путь/к/файлу.sts")
        sys.exit(1)

    sts_file = sys.argv[1]
    prefix_hex, records, tail_hex = unpack_sts(sts_file)

    out_json = sts_file + ".json"
    doc = {
        "format": "ShiVa3D STS",
        "header_hex": prefix_hex,
        "tail_hex": tail_hex,
        "entries": records,
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"ГОТОВО! Распаковано {len(records)} записей в:\n{out_json}")
    