"""Comercial: leitura do pipe Dreamis CRM (agregados apenas). Regras em config/pipes.json (ajustaveis sem mexer no codigo)."""
from datetime import timedelta
from nn import norm, iso
from leitura import ler, mes, entre, D


def build(cards, cfg, hoje):
    C = cfg['comercial']; ph, cp = C['fases'], C['campos']
    cs = ler(cards)
    nf = {k: norm(v) for k, v in ph.items()}
    nc = {k: norm(v) for k, v in cp.items()}

    def ev_agendado(c):
        return c['hist'].get(nf['agendado']) or iso(c['F'].get(nc['agendado'], ''))

    def ev_visita(c):
        return iso(c['F'].get(nc['realizado'], '')) or c['hist'].get(nf['visita'], '')

    def ev_venda(c):
        d = c['hist'].get(nf['venda'], '')
        if not d and c['F'].get(nc['fechado'], '').lower().startswith('sim'):
            d = c['hist'].get(norm('Negociação'), '') or c['criado']
        return d

    ini, fim, pini, pfim, nome = mes(hoje)
    fr = {k: [norm(x) for x in v] for k, v in C['frentes'].items()}

    def conta(lst, a, b):
        return {'cadastros': sum(entre(c['criado'], a, b) for c in lst),
                'agendados': sum(entre(ev_agendado(c), a, b) for c in lst),
                'visitas': sum(entre(ev_visita(c), a, b) for c in lst),
                'vendas': sum(entre(ev_venda(c), a, b) for c in lst)}

    cur, ant = conta(cs, ini, fim), conta(cs, pini, pfim)
    kpis = {k: {'v': cur[k], 'ant': ant[k]} for k in cur}

    # comparecimento: dos atendimentos agendados nos ultimos 90 dias (ate ontem), quantos tem visita realizada
    h = D(hoje)
    a90, ontem = (h - timedelta(days=90)).strftime('%Y-%m-%d'), (h - timedelta(days=1)).strftime('%Y-%m-%d')
    ag = [c for c in cs if entre(ev_agendado(c), a90, ontem)]
    comp = round(100 * sum(1 for c in ag if ev_visita(c)) / len(ag), 1) if ag else None

    cad = [c for c in cs if entre(c['criado'], ini, fim)]
    qual = round(100 * sum(1 for c in cad if c['F'].get(nc['produto'])) / len(cad), 1) if cad else None

    def da_frente(c, toks):
        return any(t == l or t in l for l in c['labels'] for t in toks)

    frentes = {k: conta([c for c in cs if da_frente(c, toks)], ini, fim) for k, toks in fr.items()}
    sem = [c for c in cs if not any(da_frente(c, t) for t in fr.values()) and entre(c['criado'], ini, fim)]

    # origem dos cadastros do mes e quantos deles ja tiveram visita
    og = {}
    for c in cad:
        o = c['F'].get(nc['origem'], '').strip() or 'Não informado'
        r = og.setdefault(norm(o), {'origem': o, 'cadastros': 0, 'visitas': 0})
        r['cadastros'] += 1
        r['visitas'] += 1 if ev_visita(c) else 0
    origem = sorted(og.values(), key=lambda r: -r['cadastros'])
    top = origem[:C.get('origem_top', 5)]
    if len(origem) > len(top):
        rest = origem[len(top):]
        top.append({'origem': 'Outras', 'cadastros': sum(r['cadastros'] for r in rest), 'visitas': sum(r['visitas'] for r in rest)})

    funil = [{'fase': f, 'n': sum(1 for c in cs if c['fase'] == norm(f))} for f in C['funil']]
    return {'mes': nome, 'parcial_ate': hoje[8:10] + '/' + hoje[5:7], 'kpis': kpis, 'comparecimento': comp, 'qualificacao': qual,
            'frentes': frentes, 'sem_frente_cadastros': len(sem), 'origem': top, 'funil': funil, 'metas': C.get('metas')}
