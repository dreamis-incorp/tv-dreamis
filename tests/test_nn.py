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
