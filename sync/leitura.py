"""Leitura generica de cards (formato 'leve') e utilitarios de periodo. So datas, fases, etiquetas e campos. Nada de titulo/nome de cliente."""
import calendar
from datetime import datetime, timedelta
from nn import norm, day, iso


def ler(cards):
    out = []
    for c in cards:
        h = {}
        for x in c.get('phases_history') or []:
            n = norm(x['phase'].get('name') or '')
            d = day(x['firstTimeIn'])
            if d and (n not in h or d < h[n]):
                h[n] = d
        F, raw = {}, {}
        for f in c.get('fields') or []:
            k = norm(f.get('name') or '')
            v = (f.get('value') or '').strip()
            if k and v:
                F[k] = v
        out.append({'criado': day(c['createdAt']), 'fase': norm(c['current_phase'].get('name') or ''),
                    'hist': h, 'F': F, 'labels': [norm(l['name']) for l in (c.get('labels') or [])],
                    'due': iso(c.get('due_date') or ''), 'done': bool(c.get('done'))})
    return out


def D(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


def mes(hoje):
    """Retorna (inicio_mes, hoje, inicio_mes_anterior, mesmo_dia_no_mes_anterior, nome do mes)."""
    h = D(hoje)
    ini = h.replace(day=1)
    pf = ini - timedelta(days=1)
    pini = pf.replace(day=1)
    pfim = pini + timedelta(days=min(h.day, calendar.monthrange(pini.year, pini.month)[1]) - 1)
    nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    f = lambda d: d.strftime('%Y-%m-%d')
    return f(ini), f(h), f(pini), f(pfim), f'{nomes[h.month - 1]}/{h.year}'


def entre(d, a, b):
    return bool(d) and a <= d <= b


def tem(c, nome):
    return norm(nome) in c['hist']
