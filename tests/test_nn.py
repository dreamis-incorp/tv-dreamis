"""Testes rapidos da logica de metas. Rodar: python3 tests/test_nn.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sync'))
import nn
cfg = nn.load_cfg(os.path.join(os.path.dirname(__file__), '..', 'config', 'metas.json'))

# esperado: interpolacao linear entre marcos (abordados: 22/10 -> 30/11 = 110)
assert nn.esperado(cfg, 'ab', '2026-10-22') == 0
assert round(nn.esperado(cfg, 'ab', '2026-11-30')) == 110
mid = nn.esperado(cfg, 'ab', '2026-11-10')           # 19 de 39 dias
assert 50 < mid < 60, mid
assert nn.esperado(cfg, 'ab', '2027-12-01') == 200   # depois do ultimo marco da metrica

def pq(ppe_dates, hoje):
    return [{'id': str(i), 'ph': 1, 'cr': '2026-10-01', 'h': [], 'si': '2026-10-01', 'int': '', 'reu': '', 'ppe': d, 'dre': ''} for i, d in enumerate(ppe_dates)]

# semana: segunda 09/11 a domingo 15/11; hoje = terca 10/11
p = nn.placar(pq(['2026-11-09'] * 7, '2026-11-10'), [], cfg, '2026-11-10')
assert p['semana']['feitas'] == 7 and p['semana']['status'] == 'run', p['semana']
p = nn.placar(pq(['2026-11-09'] * 20, '2026-11-10'), [], cfg, '2026-11-10')
assert p['semana']['status'] == 'ok'
p = nn.placar(pq([], '2026-11-13'), [], cfg, '2026-11-13')   # sexta, nada feito: nao da mais para bater
assert p['semana']['status'] == 'late', p['semana']
# antes da abordagem comecar
p = nn.placar([], [], cfg, '2026-10-20')
assert p['semana']['ativa'] is False and p['semana']['comeca_em'] == '2026-10-22'
# eventos anteriores ao inicio do plano nao contam
p = nn.placar(pq(['2026-10-01'], '2026-11-10'), [], cfg, '2026-11-10')
assert [m for m in p['marcos'] if m['k'] == 'ab'][0]['feito'] == 0
print('ok: todos os testes passaram')

# ---- Comercial / Incorporacao / Marketing (cards ficticios com a mesma forma do Pipefy) ----
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from tools.sample_pipes import make, card
from datetime import date, timedelta
import comercial, incorporacao, marketing
PC = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'config', 'pipes.json'), encoding='utf-8'))
H = '2026-11-10'
d = date(2026, 11, 10)
mk = lambda **k: card(d - timedelta(days=k.pop('ago', 1)), k.pop('fase', 'Cadastro'), k.pop('path', [('Cadastro', d)]), k.pop('fields', {}), k.pop('labels', ()))
cards = [
    mk(labels=['Alessandro'], fields={'Produto Dreamis de interesse': 'Tauá', 'Por onde veio o cliente': 'Meta'}),
    mk(labels=['Arthur'], fields={'Por onde veio o cliente': 'Meta', 'Data e hora do atendimento agendado': '12/11/2026 10:00'}),
    mk(labels=['Kharina'], fields={'Data e hora do atendimento agendado': '05/11/2026 10:00', 'Data e hora do atendimendo realizado': '05/11/2026 10:30'}),
    mk(ago=40, labels=['Raquel']),   # cadastrado no mes anterior
]
r = comercial.build(cards, PC, H)
assert r['kpis']['cadastros']['v'] == 3 and r['kpis']['cadastros']['ant'] == 1, r['kpis']
assert r['kpis']['agendados']['v'] == 1 and r['kpis']['visitas']['v'] == 1, r['kpis']
assert r['frentes']['house']['cadastros'] == 2 and r['frentes']['plataforma']['cadastros'] == 1, r['frentes']
assert r['origem'][0]['origem'] == 'Meta' and r['origem'][0]['cadastros'] == 2
assert round(r['qualificacao']) == 33
X = make(H)
inc = incorporacao.build(X['tau'], X['hom'], PC, H); mkt = marketing.build(X['redes'], X['ges'], X['off'], r, PC, H)
assert inc['tau']['ativos'] + inc['tau']['contratos'] + inc['tau']['travados'] == 15
assert len(mkt['redes']['funil']) == 6 and mkt['offline'][3]['n'] == 10
print('ok: Comercial, Incorporacao e Marketing')
