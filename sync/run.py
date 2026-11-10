"""Uso:
  python3 sync/run.py                -> le o Pipefy (PIPEFY_TOKEN) e grava site/data.enc.json
  python3 sync/run.py --sample       -> usa cards ficticios (teste, sem Pipefy)
Variaveis: TV_PASSWORD (minimo 8 caracteres), PIPEFY_TOKEN, TV_HOJE (opcional, aaaa-mm-dd, para testes)."""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
import nn
from lock import encrypt

sample = '--sample' in sys.argv
pw = os.environ.get('TV_PASSWORD', '')
if len(pw) < 8:
    sys.exit('ERRO: TV_PASSWORD ausente ou curta; nada foi gerado')
now = datetime.now(nn.BRT)
hoje = os.environ.get('TV_HOJE') or now.strftime('%Y-%m-%d')
cfg = nn.load_cfg('config/metas.json')

if sample:
    from tools.sample_cards import make, CRM_PH, PQ_PH
    ccards, pcards = make(hoje)
    cph, pph = CRM_PH, PQ_PH
else:
    import pipefy
    cph, pph = pipefy.phases(pipefy.PIPE_CRM), pipefy.phases(pipefy.PIPE_PQ)
    ccards, pcards = pipefy.cards(pipefy.PIPE_CRM), pipefy.cards(pipefy.PIPE_PQ)

crm, pq = nn.read_crm(ccards, cph), nn.read_pq(pcards, pph)
if not sample and (len(crm) < 5 or len(pq) < 20):
    sys.exit(f'ERRO: poucos cards lidos (crm {len(crm)}, pq {len(pq)}); nada foi publicado')

data = {'gerado_em': now.strftime('%Y-%m-%dT%H:%M'), 'hoje': hoje, 'exemplo': sample,
        'novos_negocios': nn.build(pq, crm, cfg, hoje), 'comercial': None}

# Comercial: entra quando o codigo de leitura do CRM comercial for integrado (ver docs).
try:
    import comercial
    data['comercial'] = comercial.build(hoje, sample)
except ImportError:
    if sample:
        from tools.sample_comercial import build as _b
        data['comercial'] = _b(hoje)

salt = open('config/salt.txt').read().strip()
os.makedirs('site', exist_ok=True)
json.dump(encrypt(data, pw, salt), open('site/data.enc.json', 'w'))
if sample and os.environ.get('TV_DEBUG_JSON'):
    json.dump(data, open(os.environ['TV_DEBUG_JSON'], 'w'), ensure_ascii=False, indent=1)
print(f'ok crm {len(crm)} pq {len(pq)} em {now:%d/%m/%Y %H:%M}' + (' (EXEMPLO)' if sample else ''))
