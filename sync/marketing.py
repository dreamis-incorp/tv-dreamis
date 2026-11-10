"""Marketing: entregas (Redes Sociais, gestao, mídia off-line) + leads por origem vindos do Comercial."""
from nn import norm
from leitura import ler, mes, entre


def build(redes_cards, gestao_cards, off_cards, comercial, cfg, hoje):
    M = cfg['marketing']
    ini, fim, pini, pfim, nome = mes(hoje)
    r = ler(redes_cards); R = M['redes']; rf = R['fases']
    conc, pub = norm(rf[-1]), norm('Publicação')
    redes = {'funil': [{'fase': f, 'n': sum(1 for c in r if c['fase'] == norm(f))} for f in rf],
             'concluidos_mes': sum(entre(c['hist'].get(conc), ini, fim) for c in r),
             'concluidos_ant': sum(entre(c['hist'].get(conc), pini, pfim) for c in r),
             'publicados_mes': sum(entre(c['hist'].get(pub), ini, fim) for c in r)}
    g = ler(gestao_cards); G = M['gestao']; andam = {norm(x) for x in G['andamento']}; gf = norm(G['final'])
    gestao = {'em_andamento': sum(1 for c in g if c['fase'] in andam),
              'concluidas_mes': sum(entre(c['hist'].get(gf), ini, fim) for c in g),
              'concluidas_ant': sum(entre(c['hist'].get(gf), pini, pfim) for c in g)}
    o = ler(off_cards)
    off = [{'fase': f, 'n': sum(1 for c in o if c['fase'] == norm(f))} for f in M['offline']['fases']]
    return {'mes': nome, 'redes': redes, 'gestao': gestao, 'offline': off,
            'origem': (comercial or {}).get('origem') or [], 'cadastros_mes': ((comercial or {}).get('kpis') or {}).get('cadastros', {}).get('v')}
