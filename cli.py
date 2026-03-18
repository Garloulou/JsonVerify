import sys
import json

from utils import estimate_bytes

class CLI:
    def __init__(self):
        self.results = {}

    def process_file(self, file):
        with open(file, 'r') as f:
            self.results[file] = {}
            content = f.read()
            try:
                json_content = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON in file {file}: {e}")
                self.results[file]['ok'] = 0
                self.results[file]['error_cnt'] = 0
                self.results[file]['skip'] = 0
                self.results[file]['errors'] = [f"JSON parsing error: {e}"]
                return

            self.process_json(json_content, file)

    def process_json(self, json, name):
        ok_cnt = err_cnt = skip_cnt = 0
        self.results[name]['errors'] = []

        for idx, d in enumerate(json, 1):
            nom   = d.get("nom_fr",   "").strip()
            texte = d.get("texte_fr", "").strip()
            limit = d.get("data_size", 8) - 8

            if not nom or not texte:
                skip_cnt += 1
                continue

            size = estimate_bytes('"' + nom + "\n" + texte + "\n")

            if size == -1 or size > limit:
                err_cnt += 1

                if size != -1:
                    excess_bytes = size - limit
                    excess_chars = excess_bytes // 2
                    max_chars = limit // 2
                    msg = f"ID {d['id']} : +{excess_bytes} bytes (+{excess_chars} chars en trop) | Max: ~{max_chars} chars"
                    self.results[name]['errors'].append(msg)
            else:
                ok_cnt += 1

        self.results[name]['ok'] = ok_cnt
        self.results[name]['error_cnt'] = err_cnt
        self.results[name]['skip'] = skip_cnt

    def export(self, asMarkdown=False):
        if asMarkdown:
            print("| File | OK | ERROR | SKIP |")
            print("|------|----|-------|------|")
            for name, stats in self.results.items():
                print(f"| {name} | {stats['ok']} | {stats['error_cnt']} | {stats['skip']} |")

                print("\n")
                if (stats['errors']):
                    print("| **Errors** |")
                    print("| --- |")
                    for error in stats['errors']:
                        print(f"| - {error} |")
                    print("\n")
            return

        for idx, (name, stats) in enumerate(self.results.items(), 1):
            print(f"{name}: {stats['ok']} OK, {stats['error_cnt']} ERROR, {stats['skip']} SKIP")

            if (stats['errors']): print("========== ERROR ==========")
            for error in stats['errors']:
                print(f"  - {error}" )

    def hasErrors(self):
        return any(stats['error_cnt'] > 0 for stats in self.results.values())

def main(args)-> int:
    markdown = False
    if '--markdown' in args:
        args.remove('--markdown')
        markdown = True

    files = args

    if not files:
        print("Usage: python cli.py <file1> <file2> ...")
        return 1

    cli = CLI()

    for file in files:
        cli.process_file(file)

    cli.export(markdown)

    return 1 if cli.hasErrors() else 0

args = sys.argv
args = args[1:]

if __name__ == "__main__":
    result = main(args)
    sys.exit(result)
