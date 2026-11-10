"""Incorporacao: Personalizacao TAU e Homologacao de Fornecedores (agregados apenas)."""
from nn import norm
from leitura import ler, mes, entre, D


def _dias(a, b):
    return (D(b) - D(a)).days if a and b else None


def build(tau_cards, hom_cards, cfg, hoje):
    I = cfg['incorporacao']
    ini, fim, pini, pfim, nome = mes(hoje)
    # Personalizacao
    t = ler(tau_cards); TC = I['tau']; fin, trav = norm(TC['final']), norm(TC['travado'])
    por = {}
    for c in t:
        por[c['fase']] = por.get(c['fase'], 0) + 1
    ativos = [c for c in t if c['fase'] not in (fin, trav)]
    etapas = [{'etapa': e, 'n': por.get(norm(e), 0)} for e in TC.get('etapas', [])]
    fechados = [c for c in t if c['fase'] == fin]
    ciclos = [x for x in (_dias(c['criado'], c['hist'].get(fin)) for c in fechados) if x is not None]
    tau = {'ativos': len(ativos), 'travados': por.get(trav, 0),
           'atrasados': sum(1 for c in ativos if c['due'] and c['due'] < hoje),
           'contratos': len(fechados), 'contratos_mes': sum(entre(c['hist'].get(fin), ini, fim) for c in t),
           'ciclo_medio_dias': round(sum(ciclos) / len(ciclos)) if ciclos else None, 'etapas': etapas}
    # Homologacao
    hc = ler(hom_cards); HC = I['homologacao']; hf = norm(HC['final'])
    hom = {'funil': [{'fase': f, 'n': sum(1 for c in hc if c['fase'] == norm(f))} for f in HC['fases']],
           'homologados_mes': sum(entre(c['hist'].get(hf), ini, fim) for c in hc),
           'homologados_mes_ant': sum(entre(c['hist'].get(hf), pini, pfim) for c in hc)}
    return {'mes': nome, 'tau': tau, 'homologacao': hom}
