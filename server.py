#!/usr/bin/env python3
"""
Servidor de desarrollo para Interletras.
Sirve archivos estáticos + /api/remove-word para eliminar palabras
del banco de forma permanente (modifica data/bank.json y data/bank.js).

Uso:
    python3 server.py          # puerto 8765
    python3 server.py 9000     # puerto custom
"""
import http.server
import json
import os
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
BASE = Path(__file__).parent
BANK_JSON = BASE / 'data' / 'bank.json'
BANK_JS   = BASE / 'data' / 'bank.js'


def remove_from_bank(word: str) -> bool:
    if not BANK_JSON.exists():
        return False
    bank = json.loads(BANK_JSON.read_text(encoding='utf-8'))
    if word not in bank:
        return False
    del bank[word]
    compact = json.dumps(bank, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    BANK_JSON.write_text(compact, encoding='utf-8')
    BANK_JS.write_text('window.CRUCIGRAMA_BANK=' + compact + ';', encoding='utf-8')
    return True


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors(200)

    def do_POST(self):
        if self.path != '/api/remove-word':
            self._json(404, {'error': 'not found'})
            return
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
            word = str(body.get('word', '')).strip().upper()
        except Exception:
            self._json(400, {'error': 'invalid json'})
            return
        if not word:
            self._json(400, {'error': 'missing word'})
            return
        removed = remove_from_bank(word)
        print(f'[banco] {"eliminada" if removed else "no encontrada"}: {word}')
        self._json(200, {'ok': True, 'removed': removed})

    def _cors(self, code):
        self.send_response(code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if self.path and self.path.startswith('/api/'):
            return  # ya lo imprime remove_from_bank
        super().log_message(fmt, *args)


if __name__ == '__main__':
    os.chdir(BASE)
    with http.server.ThreadingHTTPServer(('', PORT), Handler) as httpd:
        print(f'Interletras → http://localhost:{PORT}/')
        httpd.serve_forever()
