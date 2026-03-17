import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading

BG_DEEP    = "#0d0808"
BG_PANEL   = "#140a0a"
BG_CARD    = "#1c0f0f"
BG_HOVER   = "#261414"
BORDER     = "#3a1818"
BORDER_LIT = "#7a2020"

NEON_BLUE  = "#c0392b"
NEON_GREEN = "#e8c49a"
NEON_RED   = "#ff4444"
NEON_AMBER = "#d4813a"
NEON_PURP  = "#c97fb5"
DIM_TEXT   = "#4a2a2a"
MID_TEXT   = "#8a5a5a"
BRIGHT_TEXT= "#f0ddd0"

FONT_MONO  = ("JetBrains Mono", 10) if os.name == "nt" else ("Consolas", 10)
FONT_TITLE = ("Segoe UI", 22, "bold") if os.name == "nt" else ("DejaVu Sans", 18, "bold")
FONT_LABEL = ("Segoe UI", 9) if os.name == "nt" else ("DejaVu Sans", 9)
FONT_BTN   = ("Segoe UI", 9, "bold") if os.name == "nt" else ("DejaVu Sans", 9, "bold")


def make_btn(parent, text, command, accent=NEON_BLUE):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=BG_CARD, fg=accent, activebackground=BG_HOVER,
        activeforeground=accent, font=FONT_BTN,
        relief="flat", bd=0, padx=14, pady=7,
        cursor="hand2"
    )
    btn.config(highlightthickness=1, highlightbackground=BORDER, highlightcolor=accent)

    def on_enter(e):
        btn.config(bg=BG_HOVER, highlightbackground=accent)
    def on_leave(e):
        btn.config(bg=BG_CARD, highlightbackground=BORDER)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_separator(parent):
    return tk.Frame(parent, bg=BORDER, height=1)


class ProgressBar(tk.Canvas):
    def __init__(self, parent, width=400, height=6, color=NEON_BLUE, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=BG_PANEL, highlightthickness=0, **kwargs)
        self._color = color
        self._total_width = width
        self._height = height
        self._pct = 0.0
        self._draw()

    def _draw(self):
        self.delete("all")
        self.create_rectangle(0, 0, self._total_width, self._height, fill=BORDER, outline="")
        w = int(self._total_width * self._pct)
        if w > 0:
            self.create_rectangle(0, 0, w, self._height, fill=self._color, outline="")
            self.create_rectangle(max(0, w-8), 0, w, self._height, fill=BRIGHT_TEXT, outline="")

    def set(self, pct):
        self._pct = max(0.0, min(1.0, pct))
        self._draw()


class JsonVerify:
    def __init__(self, root):
        self.root = root
        self.root.title("JsonVerify")
        self.root.geometry("1060x740")
        self.root.configure(bg=BG_DEEP)
        self.root.resizable(True, True)

        self.json_data = []
        self.file_path = ""
        self.error_ids = []

        self._build_ui()

    def _build_ui(self):
        title_bar = tk.Frame(self.root, bg=BG_DEEP)
        title_bar.pack(fill="x", padx=24, pady=(18, 4))

        tk.Label(title_bar, text="JsonVerify", font=FONT_TITLE, fg=BRIGHT_TEXT, bg=BG_DEEP).pack(side="left")
        tk.Label(title_bar, text="  v2.0 By Garloulou", font=FONT_LABEL, fg=DIM_TEXT, bg=BG_DEEP).pack(side="left", pady=(8, 0))
        tk.Button(
            title_bar, text="GitHub", font=FONT_LABEL,
            bg=BG_DEEP, fg=DIM_TEXT, activebackground=BG_HOVER,
            activeforeground=BRIGHT_TEXT, relief="flat", bd=0,
            padx=8, pady=4, cursor="hand2",
            command=lambda: __import__("webbrowser").open("https://github.com/chenetulipe/P2-FR-IS-PSP")
        ).pack(side="left", padx=(10, 0), pady=(8, 0))

        make_separator(self.root).pack(fill="x", padx=24, pady=(6, 14))

        ctrl = tk.Frame(self.root, bg=BG_PANEL, padx=16, pady=14)
        ctrl.pack(fill="x", padx=24)
        ctrl.configure(highlightthickness=1, highlightbackground=BORDER)

        left = tk.Frame(ctrl, bg=BG_PANEL)
        left.pack(side="left", fill="y")

        tk.Label(left, text="FICHIER UNIQUE", font=(FONT_LABEL[0], 7, "bold"),
                 fg=DIM_TEXT, bg=BG_PANEL).pack(anchor="w")

        row1 = tk.Frame(left, bg=BG_PANEL)
        row1.pack(anchor="w", pady=(6, 0))

        self.btn_load = make_btn(row1, "Charger JSON", self.load_json, NEON_BLUE)
        self.btn_load.pack(side="left", padx=(0, 8))

        self.btn_verify = make_btn(row1, "Verifier", self.run_verification_ui, NEON_GREEN)
        self.btn_verify.pack(side="left", padx=(0, 8))

        self.btn_github = make_btn(row1, "Copier Issue GitHub", self.copy_github_issue, NEON_PURP)
        self.btn_github.pack(side="left")
        self.btn_github.config(state="disabled", fg=DIM_TEXT)

        tk.Frame(ctrl, bg=BORDER, width=1).pack(side="left", fill="y", padx=20, pady=4)

        right = tk.Frame(ctrl, bg=BG_PANEL)
        right.pack(side="left", fill="y")

        tk.Label(right, text="MODE DOSSIER", font=(FONT_LABEL[0], 7, "bold"),
                 fg=DIM_TEXT, bg=BG_PANEL).pack(anchor="w")

        self.btn_dir = make_btn(right, "Verifier un dossier entier", self.process_directory, NEON_AMBER)
        self.btn_dir.pack(anchor="w", pady=(6, 0))

        status_row = tk.Frame(self.root, bg=BG_DEEP)
        status_row.pack(fill="x", padx=24, pady=(10, 0))

        self.status_dot = tk.Label(status_row, text="●", fg=DIM_TEXT, bg=BG_DEEP, font=("Segoe UI", 10))
        self.status_dot.pack(side="left")
        self.status_label = tk.Label(status_row, text="  En attente d'un fichier...",
                                      fg=MID_TEXT, bg=BG_DEEP, font=FONT_LABEL)
        self.status_label.pack(side="left")

        stats_row = tk.Frame(self.root, bg=BG_DEEP)
        stats_row.pack(fill="x", padx=24, pady=(6, 0))

        self.stat_total = self._make_stat(stats_row, "DIALOGUES",    "-", NEON_BLUE)
        self.stat_ok    = self._make_stat(stats_row, "OK",           "-", NEON_GREEN)
        self.stat_err   = self._make_stat(stats_row, "ERREURS",      "-", NEON_RED)
        self.stat_skip  = self._make_stat(stats_row, "NON TRADUITS", "-", DIM_TEXT)

        self.progress = ProgressBar(self.root, height=3, color=NEON_BLUE)
        self.progress.pack(fill="x", padx=24, pady=(10, 0))

        make_separator(self.root).pack(fill="x", padx=24, pady=(6, 0))

        log_frame = tk.Frame(self.root, bg=BG_DEEP)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        tk.Label(log_frame, text="CONSOLE OUTPUT", font=(FONT_LABEL[0], 7, "bold"),
                 fg=DIM_TEXT, bg=BG_DEEP).pack(anchor="w", pady=(8, 4))

        self.log_area = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD,
            bg=BG_CARD, fg=BRIGHT_TEXT,
            font=FONT_MONO,
            relief="flat", bd=0,
            insertbackground=NEON_BLUE,
            selectbackground=BORDER_LIT,
            padx=14, pady=10
        )
        self.log_area.configure(highlightthickness=1, highlightbackground=BORDER)
        self.log_area.pack(fill="both", expand=True)

        self.log_area.tag_config("error",   foreground=NEON_RED)
        self.log_area.tag_config("crash",   foreground=NEON_RED, background="#2a0808")
        self.log_area.tag_config("warning", foreground=NEON_AMBER)
        self.log_area.tag_config("success", foreground=NEON_GREEN)
        self.log_area.tag_config("info",    foreground=NEON_BLUE)
        self.log_area.tag_config("file",    foreground=BRIGHT_TEXT, font=(FONT_MONO[0], FONT_MONO[1], "bold"))
        self.log_area.tag_config("dim",     foreground=DIM_TEXT)

    def _make_stat(self, parent, label, value, color):
        card = tk.Frame(parent, bg=BG_CARD, padx=12, pady=6)
        card.configure(highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="left", padx=(0, 8))
        val_lbl = tk.Label(card, text=value, fg=color, bg=BG_CARD,
                           font=(FONT_LABEL[0], 16, "bold"))
        val_lbl.pack()
        tk.Label(card, text=label, fg=DIM_TEXT, bg=BG_CARD,
                 font=(FONT_LABEL[0], 7)).pack()
        return val_lbl

    def log(self, message, tag=None):
        self.log_area.insert(tk.END, message + "\n", tag or "")
        self.log_area.see(tk.END)
        self.root.update_idletasks()

    def set_status(self, text, color=MID_TEXT, dot=DIM_TEXT):
        self.status_label.config(text=f"  {text}", fg=color)
        self.status_dot.config(fg=dot)

    def estimate_bytes(self, text):
        repls = [('é','Ğ'),('è','ò'),('ê','¿'),('ô','Æ'),('É','Ņ'),
                 ('È','Ũ'),('Î','£'),('Ô','ō'),('Û','ĵ'),('œ','ë'),('Œ','Ǩ')]
        for old, new in repls:
            text = text.replace(old, new)

        CTRL_TAGS = ["[SP]","\n","[E1]","[E2]","[E3]","[E4]","[1205]","[001E]",
                     "[1432]","[0014]","[0002]","[0010]","[NULL]"]
        count = 0
        i = 0
        while i < len(text):
            if text[i] == '[':
                if ']' not in text[i:]: return -1
                end = text.index(']', i)
                tag = text[i:end+1]
                if tag == "[NULL]":
                    i = end + 1
                    continue
                found = (tag in CTRL_TAGS) or (tag.startswith("[U+") and len(tag)==8) or (len(tag)==6)
                count += 2 if found else len(tag[1:-1]) * 2
                i = end + 1
            else:
                count += 2
                i += 1
        return count

    def generate_github_text(self, filename, error_ids):
        ids_str = ", ".join([f"`{id_}`" for id_ in error_ids])
        return (
            f"### 📂 Script affecte\n* `{filename}`\n\n"
            f"### ⚠️ ID des phrases affectees\n"
            f"Les IDs suivants presentent des longueurs excessives :\n> {ids_str}\n\n---\n"
            f"### 🛠️ Solution possible\n* **Action :** Rendre les phrases plus courtes."
        )

    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path: return
        self.file_path = path
        with open(path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)

        name = os.path.basename(path)
        self.set_status(f"{name}  -  {len(self.json_data)} dialogues charges", NEON_BLUE, NEON_BLUE)
        self.btn_github.config(state="disabled", fg=DIM_TEXT)
        self.progress.set(0)
        self._reset_stats()

        self.log_area.delete('1.0', tk.END)
        self.log(f"Fichier charge : {name}", "info")
        self.log(f"{len(self.json_data)} entrees detectees\n", "info")

    def run_verification_ui(self):
        if not self.json_data:
            self.set_status("Aucun fichier charge.", NEON_AMBER, NEON_AMBER)
            return
        self.log_area.delete('1.0', tk.END)
        self.btn_verify.config(state="disabled")
        self.btn_github.config(state="disabled", fg=DIM_TEXT)
        threading.Thread(target=self._do_verification, daemon=True).start()

    def _do_verification(self):
        self.error_ids = []
        total    = len(self.json_data)
        ok_cnt   = 0
        err_cnt  = 0
        skip_cnt = 0

        self.log(f"Verification en cours sur {total} entrees...\n", "info")

        for idx, d in enumerate(self.json_data, 1):
            nom   = d.get("nom_fr",   "").strip()
            texte = d.get("texte_fr", "").strip()
            limit = d.get("data_size", 8) - 8

            if not nom or not texte:
                skip_cnt += 1
                self.progress.set(idx / total)
                continue

            size = self.estimate_bytes('"' + nom + "\n" + texte + "\n")

            if size == -1 or size > limit:
                err_cnt += 1
                self.error_ids.append(str(d['id']))
                tag   = "crash" if size == -1 else "error"
                label = "💀 CRASH" if size == -1 else "🔴 TROP LONG"
                self.log(f"{label} ID {d['id']} : {size}/{limit} bytes", tag)
            else:
                ok_cnt += 1

            self.progress.set(idx / total)
            self._update_stats(total, ok_cnt, err_cnt, skip_cnt)

        self.log("")
        if err_cnt == 0:
            if ok_cnt > 0:
                self.log("🟢 Tout est traduit et a la bonne taille !", "success")
            self.set_status("Verification terminee - aucune erreur.", NEON_GREEN, NEON_GREEN)
        else:
            self.set_status(f"{err_cnt} erreur(s) - rapport GitHub disponible.", NEON_RED, NEON_RED)
            self.root.after(0, lambda: self.btn_github.config(state="normal", fg=NEON_PURP))

        self._update_stats(total, ok_cnt, err_cnt, skip_cnt)
        self.root.after(0, lambda: self.btn_verify.config(state="normal"))

    def run_verification(self, silent=False):
        if not self.json_data: return ""
        if not silent: self.log_area.delete('1.0', tk.END)

        self.error_ids = []
        logs = ""

        for d in self.json_data:
            nom   = d.get("nom_fr",   "").strip()
            texte = d.get("texte_fr", "").strip()
            limit = d.get("data_size", 8) - 8

            if not nom or not texte: continue

            size = self.estimate_bytes('"' + nom + "\n" + texte + "\n")

            if size == -1 or size > limit:
                self.error_ids.append(str(d['id']))
                label = "💀 CRASH" if size == -1 else "🔴 TROP LONG"
                msg   = f"{label} ID {d['id']} : {size}/{limit} bytes"
                logs += msg + "\n"
                if not silent: self.log(msg, "error")
            else:
                logs += f"✅ OK ID {d['id']} : {size}/{limit} bytes\n"

        if not silent:
            if self.error_ids:
                self.btn_github.config(state="normal", fg=NEON_PURP)
            elif logs:
                self.log("🟢 Tout est traduit et a la bonne taille !", "success")

        return logs

    def process_directory(self):
            dir_path = filedialog.askdirectory()
            if not dir_path: return

            output_base = os.path.join(dir_path, "VERIFICATION_OUTPUT")
            self.log_area.delete('1.0', tk.END)
            self._reset_stats()

            json_files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
            total_files = len(json_files)

            self.log(f"Mode Dossier : {dir_path}", "info")
            self.log(f"{total_files} fichier(s) JSON trouve(s)\n", "info")

            if total_files == 0:
                self.set_status("Aucun fichier JSON trouve.", NEON_AMBER, NEON_AMBER)
                return

            global_errors = 0
            global_ok     = 0

            for i, filename in enumerate(json_files, 1):
                file_full_path = os.path.join(dir_path, filename)
                file_slug = filename.replace(".json", "")

                with open(file_full_path, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)

                logs = self.run_verification(silent=True)
                self.progress.set(i / total_files)

                # Si on a des logs, cela signifie que le fichier a été traduit et analysé
                if logs and logs.strip():
                    
                    # S'il y a des erreurs détectées
                    if self.error_ids:
                        self.log(f"[{i}/{total_files}] {filename}", "dim")
                        global_errors += len(self.error_ids)
                        
                        # 🔴 CRÉATION DES FICHIERS UNIQUEMENT POUR LES ERREURS
                        file_output_dir = os.path.join(output_base, file_slug)
                        os.makedirs(file_output_dir, exist_ok=True)

                        log_path = os.path.join(file_output_dir, f"logs_{file_slug}.txt")
                        with open(log_path, "w", encoding="utf-8") as f:
                            f.write(logs)

                        github_text = self.generate_github_text(filename, self.error_ids)
                        github_path = os.path.join(file_output_dir, f"github_{file_slug}.txt")
                        with open(github_path, "w", encoding="utf-8") as f:
                            f.write(github_text)
                            
                        self.log(f"  🔴 {len(self.error_ids)} erreur(s) — consulter logs_{file_slug}.txt", "error")
                    
                    # S'il n'y a pas d'erreur
                    else:
                        # 🟢 LOG CONSOLE SEULEMENT (Pas de création de fichier)
                        self.log(f"[{i}/{total_files}] {filename}", "dim")
                        global_ok += 1
                        self.log("  🟢 OK", "success")
                        
                # Si `logs` est vide (fichier non traduit), on ne fait rien (pas de else).

            self.log(f"\n{global_ok}/{total_files} fichiers valides", "success")
            if global_errors:
                self.log(f"{global_errors} erreur(s) au total", "error")
            self.log(f"Rapports : {output_base}", "info")

            self.set_status(
                f"Termine - {global_ok} OK, {global_errors} erreur(s)",
                NEON_GREEN if global_errors == 0 else NEON_AMBER,
                NEON_GREEN if global_errors == 0 else NEON_AMBER
            )
            messagebox.showinfo("JsonVerify", f"Verification terminee !\n{global_ok}/{total_files} fichiers OK.")

    def copy_github_issue(self):
        if self.error_ids:
            txt = self.generate_github_text(os.path.basename(self.file_path), self.error_ids)
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.set_status("Issue GitHub copiee dans le presse-papier.", NEON_PURP, NEON_PURP)

    def _reset_stats(self):
        for lbl in (self.stat_total, self.stat_ok, self.stat_err, self.stat_skip):
            lbl.config(text="-")

    def _update_stats(self, total, ok, err, skip):
        def _do():
            self.stat_total.config(text=str(total))
            self.stat_ok.config(text=str(ok))
            self.stat_err.config(text=str(err))
            self.stat_skip.config(text=str(skip))
        self.root.after(0, _do)


if __name__ == "__main__":
    root = tk.Tk()
    app  = JsonVerify(root)
    root.mainloop()
