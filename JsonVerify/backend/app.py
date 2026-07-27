# -*- coding: utf-8 -*-

import json
import os
import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from utils import estimate_bytes

app = FastAPI()

# Configuration CORS pour autoriser le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELES ====================

class FileCheckRequest(BaseModel):
    filename: str
    data: list

class DirCheckRequest(BaseModel):
    dir_path: str

class VerifyResult(BaseModel):
    total: int
    ok: int
    errors: int
    skipped: int
    error_ids: List[str]
    logs: List[str]
    github_text: Optional[str] = None

# ==================== ETAT GLOBAL ====================

current_json_data = []
current_file_path = ""
current_error_ids = []
current_dir = ""

# ==================== ENDPOINTS ====================

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/load")
def load_json(request: FileCheckRequest):
    global current_json_data, current_file_path
    try:
        current_json_data = request.data
        current_file_path = request.filename
        return {
            "success": True,
            "filename": request.filename,
            "count": len(current_json_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify")
def verify():
    global current_json_data, current_error_ids

    if not current_json_data:
        raise HTTPException(status_code=400, detail="Aucun fichier charge")

    current_error_ids = []
    total = len(current_json_data)
    ok_cnt = 0
    err_cnt = 0
    skip_cnt = 0
    logs = []

    for d in current_json_data:
        nom = d.get("nom_fr", "")
        if not nom:
            nom = d.get("nom_orig", "")
        nom = nom.strip()

        texte = d.get("texte_fr", "").strip()
        limit = d.get("data_size", 8) - 8

        if not texte:
            skip_cnt += 1
            continue

        if nom:
            content = '"' + nom + "\n" + texte + "\n"
        else:
            content = texte

        size = estimate_bytes(content)

        if size == -1 or size > limit:
            err_cnt += 1
            current_error_ids.append(str(d['id']))
            tag = "CRASH" if size == -1 else "ERROR"
            if size != -1:
                excess_bytes = size - limit
                excess_chars = excess_bytes // 2
                max_chars = limit // 2
                logs.append(f"{tag} ID {d['id']} : +{excess_bytes} bytes (+{excess_chars} chars en trop) | Max: ~{max_chars} chars")
            else:
                logs.append(f"{tag} ID {d['id']} : Format tag invalide")
        else:
            ok_cnt += 1
            logs.append(f"OK ID {d['id']} : {size}/{limit} bytes")

    github_text = None
    if current_error_ids:
        filename = os.path.basename(current_file_path)
        ids_str = ", ".join([f"`{id_}`" for id_ in current_error_ids])
        github_text = (
            f"### Script affecte\n* `{filename}`\n\n"
            f"### ID des phrases affectees\n"
            f"Les IDs suivants presentent des longueurs excessives :\n> {ids_str}\n\n---\n"
            f"### Solution possible\n* **Action :** Rendre les phrases plus courtes."
        )

    return {
        "total": total,
        "ok": ok_cnt,
        "errors": err_cnt,
        "skipped": skip_cnt,
        "error_ids": current_error_ids,
        "logs": logs,
        "github_text": github_text
    }

@app.post("/api/process_directory")
def process_directory(request: DirCheckRequest):
    global current_dir
    current_dir = request.dir_path

    json_files = []
    for root, _, files in os.walk(request.dir_path):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))

    results = []
    global_errors = 0
    global_ok = 0
    output_base = os.path.join(request.dir_path, "VERIFICATION_OUTPUT")

    for file_path in json_files:
        filename = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, request.dir_path)
        file_slug = rel_path.replace(".json", "").replace(os.sep, "_")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            results.append({
                "file": rel_path,
                "status": "error",
                "message": f"JSON invalide: {e}"
            })
            continue

        local_error_ids = []
        logs = []
        for d in data:
            nom = d.get("nom_fr", "")
            if not nom:
                nom = d.get("nom_orig", "")
            nom = nom.strip()
            texte = d.get("texte_fr", "").strip()
            limit = d.get("data_size", 8) - 8

            if not texte:
                continue

            if nom:
                content = '"' + nom + "\n" + texte + "\n"
            else:
                content = texte

            size = estimate_bytes(content)

            if size == -1 or size > limit:
                local_error_ids.append(str(d['id']))
                tag = "CRASH" if size == -1 else "ERROR"
                if size != -1:
                    excess_bytes = size - limit
                    excess_chars = excess_bytes // 2
                    max_chars = limit // 2
                    logs.append(f"{tag} ID {d['id']} : +{excess_bytes} bytes (+{excess_chars} chars en trop)")
                else:
                    logs.append(f"{tag} ID {d['id']} : Format tag invalide")
            else:
                logs.append(f"OK ID {d['id']} : {size}/{limit} bytes")

        if local_error_ids:
            global_errors += len(local_error_ids)
            file_output_dir = os.path.join(output_base, os.path.dirname(rel_path), file_slug)
            os.makedirs(file_output_dir, exist_ok=True)

            log_path = os.path.join(file_output_dir, f"logs_{file_slug}.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(logs))

            ids_str = ", ".join([f"`{id_}`" for id_ in local_error_ids])
            github_text = (
                f"### Script affecte\n* `{filename}`\n\n"
                f"### ID des phrases affectees\n"
                f"> {ids_str}"
            )
            github_path = os.path.join(file_output_dir, f"github_{file_slug}.txt")
            with open(github_path, "w", encoding="utf-8") as f:
                f.write(github_text)

            results.append({
                "file": rel_path,
                "status": "error",
                "error_count": len(local_error_ids),
                "logs": logs
            })
        else:
            global_ok += 1
            results.append({
                "file": rel_path,
                "status": "ok",
                "logs": logs
            })

    return {
        "total_files": len(json_files),
        "ok_files": global_ok,
        "error_files": global_errors,
        "results": results,
        "output_dir": output_base
    }

@app.get("/api/github")
def get_github_text():
    if not current_error_ids:
        raise HTTPException(status_code=400, detail="Aucune erreur a signaler")
    filename = os.path.basename(current_file_path)
    ids_str = ", ".join([f"`{id_}`" for id_ in current_error_ids])
    return {
        "text": (
            f"### Script affecte\n* `{filename}`\n\n"
            f"### ID des phrases affectees\n"
            f"Les IDs suivants presentent des longueurs excessives :\n> {ids_str}\n\n---\n"
            f"### Solution possible\n* **Action :** Rendre les phrases plus courtes."
        )
    }

# ==================== LANCEMENT ====================

if __name__ == "__main__":
    import webbrowser
    # Ouvre le frontend sur localhost
    webbrowser.open("http://localhost:5173")
    # Écoute sur localhost pour éviter les problèmes de pare-feu
    uvicorn.run(app, host="localhost", port=8000)