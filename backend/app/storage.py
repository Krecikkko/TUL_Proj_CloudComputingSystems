import os, re, uuid, asyncio
from pathlib import Path

LOCAL_ROOT = "/srv/file-ops/data"
SAFE = re.compile(r"[^A-Za-z0-9._-]+")

def safe_name(name: str) -> str:
    n = SAFE.sub("_", name).strip("._") or "file"
    return n[:255]

def build_rel_path(user_id: int, file_id: int, logical_name: str) -> str:
    # without version number
    return f"user/{user_id}/file/{file_id}/{safe_name(logical_name)}"

def _abs_under_root(rel: str) -> str:
    root = os.path.abspath(LOCAL_ROOT)
    path = os.path.abspath(os.path.join(root, rel))
    if not path.startswith(root):
        raise ValueError("path traversal")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    return path


async def save_upload_stream(upload_file, dest_rel: str) -> int:
    final_path = _abs_under_root(dest_rel)
    tmp_path = final_path + f".{uuid.uuid4().hex}.part"
    size = 0
    loop = asyncio.get_running_loop()
    with open(tmp_path, "wb") as f:
        while True:
            chunk = await upload_file.read(1024 * 1024)  # 1 MiB
            if not chunk: break
            size += len(chunk)
            await loop.run_in_executor(None, f.write, chunk)
    os.replace(tmp_path, final_path)
    return size