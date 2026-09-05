import json
import struct
import sys
import zlib


def pack_sts(json_path):
  with open(json_path, "r", encoding="utf-8") as f:
    doc = json.load(f)

  
  header_prefix = bytes.fromhex(doc["header_hex"])[0:1]
  records = doc["entries"]

  raw = bytearray()
  
  raw.extend(struct.pack("<I", len(records)))

  for item in records:
    
    name_bytes = (item["name"] + "\0").encode("utf-8")
    raw.extend(struct.pack("<I", len(name_bytes)))
    raw.extend(name_bytes)

    t_name = item["type"]
    val = item["value"]

    if t_name == "float":
      raw.append(1)  # Тип 1: float
      raw.extend(struct.pack("<f", float(val)))
    elif t_name == "string":
      raw.append(2)  # Тип 2: string
      val_bytes = (str(val) + "\0").encode("utf-8")
      raw.extend(struct.pack("<I", len(val_bytes)))
      raw.extend(val_bytes)
    elif t_name == "bool":
      raw.append(3)  # Тип 3: bool
      raw.append(1 if val else 0)
    else:
      raise ValueError(f"Неизвестный тип: {t_name}")

  
  tail_hex = doc.get("tail_hex", "")
  if tail_hex:
    raw.extend(bytes.fromhex(tail_hex))

  
  compressed = zlib.compress(raw, level=6)

  
  final_header = header_prefix + len(raw).to_bytes(4, byteorder="big")

  return final_header + compressed


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Запуск: python packer_fixed.py <файл.sts.json>")
    sys.exit(1)

  json_file = sys.argv[1]
  final_bytes = pack_sts(json_file)

  output_name = "Default.sts"
  with open(output_name, "wb") as f:
    f.write(final_bytes)

  print(f"[OK] Готово! Сохранено как {output_name}")
  