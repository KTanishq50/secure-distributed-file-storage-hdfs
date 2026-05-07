import os

def split_file(path, chunk_size, out_dir):
    chunks = []
    name = os.path.basename(path)

    os.makedirs(out_dir, exist_ok=True)

    with open(path, "rb") as f:
        i = 0
        while True:
            data = f.read(chunk_size)
            if not data:
                break

            chunk_name = f"{name}_part{i}"
            chunk_path = os.path.join(out_dir, chunk_name)

            with open(chunk_path, "wb") as cf:
                cf.write(data)

            chunks.append(chunk_path)
            i += 1

    return chunks


def merge_chunks(paths, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "wb") as outfile:
        for p in paths:
            with open(p, "rb") as cf:
                outfile.write(cf.read())

    return out_path