import os, re, uuid, asyncio
from pathlib import Path
import aiofiles
import hashlib

LOCAL_ROOT = "/srv/file-ops/data"
SAFE = re.compile(r"[^A-Za-z0-9._-]+")

def safe_name(name: str) -> str:
    n = SAFE.sub("_", name).strip("._") or "file"
    return n[:255]

def build_rel_path(user_id: int, file_id: int, logical_name: str, version_number: int) -> str:
    """Tworzy relatywną ścieżkę uwzględniającą ID użytkownika, ID pliku oraz numer wersji."""
    # Structure: user/<userID>/file/<fileId>/v<version_number>/<safe_logical_name>
    safe_logical_name = safe_name(logical_name)
    return f"user/{user_id}/file/{file_id}/v{version_number}/{safe_logical_name}" #

def _abs_under_root(rel: str) -> str:
    root = os.path.abspath(LOCAL_ROOT)
    path = os.path.abspath(os.path.join(root, rel))
    if not path.startswith(root):
        raise ValueError("path traversal")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    return path


async def save_upload_stream(upload_file, dest_rel: str) -> tuple[int, str]: # Zmieniono typ zwracany
    final_path = _abs_under_root(dest_rel)
    tmp_path = final_path + f".{uuid.uuid4().hex}.part"
    size = 0
    hasher = hashlib.sha256() # Inicjalizacja hashera

    await upload_file.seek(0) # Upewnij się, że zaczynamy czytać od początku

    async with aiofiles.open(tmp_path, "wb") as f:
        while True:
            chunk = await upload_file.read(1024 * 1024) # 1 MB chunks
            if not chunk: break
            size += len(chunk)
            hasher.update(chunk) # Aktualizacja sumy kontrolnej
            await f.write(chunk)
    
    os.replace(tmp_path, final_path)
    checksum = hasher.hexdigest()
    return size, checksum