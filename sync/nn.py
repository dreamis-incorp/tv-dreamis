"""Novos Negocios: transforma os cards do Pipefy em NUMEROS AGREGADOS para a TV.

Regra de ouro: nada que identifique terreno, proprietario ou pessoa sai daqui. So contagens, datas de marco e status.
As regras seguem o dashboard de terrenos (ver docs/Dashboard_Terrenos_Guia_Reproducao.md no projeto).
"""
import json, re, unicodedata
from datetime import datetime, timezone, timedelta, date

BRT = timezone(timedelta(hours=-3))
CRM_FASES = ["Triagem de novos terrenos", "Estudo de Viabilidade", "Apresentação e Proposta", "Negociação",
             "Contrato", "Sucesso", "Não foi dessa vez", "Incorporado a projeto"]
PQ_FASES = ["Caixa de entrada", "Prospectando", "Amadurecimento", "Composição de área", "Sucesso", "Não foi dessa vez"]


# ---------- utilitarios (iguais aos do dashboard de terrenos) ----------
def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'\W+', ' ', s).strip()


def day(ts):
    if not ts:
        return ''
    return datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(BRT).strftime('%Y-%m-%d')


def iso(v):
    v = (v or '').strip()
    m = re.match(r'(\d{2})/(\d{2})/(\d{4})', v)
    if m:
        return f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', v)
    return m.group(0) if m else ''


def phidx(names, n):
    k = norm(n)
    for i, x in enumerate(names):
        if norm(x) == k:
            return i
    return None


def fields(c):
    F = {}
    for f in c['fields']:
        v, arr = f['value'], f['array_value']
        if f['field']['type'] in ('connector', 'checklist_vertical', 'checklist_horizontal', 'attachment'):
            try:
                lst = json.loads(v) if v else []
            except Exception:
                lst = [v] if v else []
            F[f['field']['id']] = {'list': lst, 'ids': arr or []}
        else:
            F[f['field']['id']] = (v or '').strip()
    return F


def txt(F, k):
    v = F.get(k)
    if isinstance(v, dict):
        return ', '.join(x.strip() for x in v['list'] if x and x.strip())
    return v or ''


def ids(F, k):
    v = F.get(k)
    return v['ids'] if isinstance(v, dict) else []


def byname(c, label):
    k = norm(label)
    for f in c['fields']:
        if norm(f.get('name') or '') == k:
            return (f.get('value') or '').strip()
    return ''


def hist(c, phase_ids):
    out = []
    for h in c['phases_history']:
        i = phase_ids.get(h['phase']['id'])
        if i is None:
            continue
        out.append([i, day(h['firstTimeIn']), day(h['lastTimeOut'])])
    return out


def first_in(h, i):
    x = sorted(r[1] for r in h if r[0] == i and r[1])
    return x[0] if x else ''


# ---------- leitura dos cards em registros minimos ----------
def read_crm(cards, phase_names):
    pid = {i: phidx(CRM_FASES, n) for i, n in phase_names.items()}
    out = []
    for c in cards:
        ph = pid.get(c['current_phase']['id'])
        if ph is None:
            continue
        F = fields(c)
        h = hist(c, pid)
        p = ids(F, 'projeto_existente_1')
        out.append({'id': c['id'], 'ph': ph, 'cr': day(c['createdAt']), 'h': h, 'parent': p[0] if p else '',
                    'dei': iso(txt(F, 'data_de_envio_da_proposta'))})
    return out


def read_pq(cards, phase_names):
    pid = {i: phidx(PQ_FASES, n) for i, n in phase_names.items()}
    out = []
    for c in cards:
        ph = pid.get(c['current_phase']['id'])
        if ph is None:
            continue
        F = fields(c)
        h = hist(c, pid)
        cur = [x for x in h if x[0] == ph]
        cr = day(c['createdAt'])
        out.append({'id': c['id'], 'ph': ph, 'cr': cr, 'h': h, 'si': cur[-1][1] if cur else cr,
                    'int': txt(F, 'interesse_do_propriet_rio'), 'reu': txt(F, 'houve_reuni_o_presencial'),
                    'ppe': iso(byname(c, 'Pré-proposta enviada em')), 'dre': iso(byname(c, 'Data da reunião'))})
    return out


# ---------- datas ----------
def D(s):
    return date.fromisoformat(s)


def add(s, n):
    return (D(s) + timedelta(days=n)).isoformat()


def br(s):
    return s[8:10] + '/' + s[5:7]


# ---------- placar de metas (porte fiel da secao 00 do dashboard) ----------
def eventos(pq, crm, cfg, hoje):
    start = cfg['inicio']
    ev = {k: [] for k in ('ab', 'int', 'reu', 'prop', 'neg', 'fec')}
    sem_data_reuniao = 0
    for p in pq:
        if p['ppe']:
            ev['ab'].append(p['ppe'])
        if p['int'] in ('Positivo', 'Muito interesse'):
            ev['int'].append(first_in(p['h'], 2) or p['si'] or p['cr'])
        if p['dre']:
            ev['reu'].append(p['dre'])
        elif p['reu'] == 'Sim' and (p['si'] or p['cr']) >= start:
            sem_data_reuniao += 1
    for d in crm:
        if d['dei']:
            ev['prop'].append(d['dei'])
        n = first_in(d['h'], 3)
        if n:
            ev['neg'].append(n)
        c = sorted(x for x in (first_in(d['h'], 4), first_in(d['h'], 5)) if x)
        if c:
            ev['fec'].append(c[0])
    for k in ev:
        ev[k] = sorted(x for x in ev[k] if x and start <= x <= hoje)
    return ev, sem_data_reuniao


def alvos(cfg, k):
    return [[d, m[k]] for d, m in cfg['marcos'] if k in m]


def esperado(cfg, k, dia):
    d0 = cfg['abordagem'][0] if k == 'ab' else cfg['inicio']
    v0 = 0
    for d, v in alvos(cfg, k):
        if dia <= d:
            span = (D(d) - D(d0)).days
            t = 1 if span <= 0 else max(0, min(1, (D(dia) - D(d0)).days / span))
            return v0 + (v - v0) * t
        d0, v0 = d, v
    return v0


def placar(pq, crm, cfg, hoje):
    ev, sem_data = eventos(pq, crm, cfg, hoje)
    meta_sem = cfg['meta_semana']
    ab0, ab1 = cfg['abordagem']
    wd = D(hoje).weekday()
    seg = add(hoje, -wd)
    dom = add(seg, 6)
    uteis = sum(1 for i in range(7) if D(add(seg, i)).weekday() < 5 and add(seg, i) >= hoje)
    na_semana = sum(1 for d in ev['ab'] if seg <= d <= dom)
    ativa = ab0 <= hoje <= ab1
    if na_semana >= meta_sem:
        st_sem = 'ok'
    elif na_semana + uteis * (meta_sem / 5) >= meta_sem:
        st_sem = 'run'
    else:
        st_sem = 'late'
    semanas = []
    s = ab0
    while s <= ab1 and s <= dom:
        s0 = add(s, -D(s).weekday())
        s1 = add(s0, 6)
        semanas.append({'inicio': s0, 'n': sum(1 for d in ev['ab'] if s0 <= d <= s1)})
        s = add(s, 7)
    semana = {'inicio': seg, 'fim': dom, 'feitas': na_semana, 'meta': meta_sem, 'status': st_sem if ativa else 'wait',
              'uteis': uteis, 'ativa': ativa, 'comeca_em': ab0 if hoje < ab0 else ''}

    marcos = []
    for k, rotulo in cfg['rotulos'].items():
        n = len(ev[k])
        al = alvos(cfg, k)
        prox = next((a for a in al if a[0] >= hoje), al[-1])
        fim = al[-1]
        esp = esperado(cfg, k, hoje)
        started = hoje >= (ab0 if k == 'ab' else cfg['inicio'])
        if n >= fim[1]:
            st, msg = 'ok', f'Meta final batida ({fim[1]})'
        elif n >= prox[1]:
            st, msg = 'ok', f'Meta de {br(prox[0])} batida'
        elif not started or esp < 0.5:
            st, msg = 'wait', f'Próxima meta: {prox[1]} até {br(prox[0])}'
        elif n >= int(esp):
            st, msg = 'run', f'No ritmo · faltam {prox[1] - n} até {br(prox[0])}'
        else:
            st, msg = 'late', f'Acelerar · faltam {prox[1] - n} até {br(prox[0])}'
        marcos.append({'k': k, 'rotulo': rotulo, 'feito': n, 'meta_final': fim[1], 'prox_meta': prox[1],
                       'prox_data': prox[0], 'esperado': round(esp, 1), 'status': st, 'msg': msg,
                       'pontos': [{'data': d, 'meta': v} for d, v in al]})
    melhor = max([w['n'] for w in semanas] or [0])
    batidas = sum(1 for w in semanas if w['n'] >= meta_sem)
    seq = 0
    for w in reversed(semanas):
        if w['n'] >= meta_sem:
            seq += 1
        elif w['inicio'] == seg:
            continue  # semana em andamento nao quebra a sequencia
        else:
            break
    return {'semana': semana, 'semanas': semanas, 'marcos': marcos,
            'recordes': {'melhor_semana': melhor, 'semanas_batidas': batidas, 'sequencia': seq},
            'aviso_reuniao_sem_data': sem_data}


# ---------- funil e entrada ----------
def agregados(pq, crm, cfg, hoje):
    idx = {d['id']: d for d in crm}

    def eff(d):
        p = idx.get(d['parent']) if d['parent'] else None
        return p['ph'] if p else d['ph']

    funil_crm = [0] * 7
    for d in crm:
        e = eff(d)
        if e < 7:
            funil_crm[e] += 1
    funil_pq = [0] * 6
    for p in pq:
        funil_pq[p['ph']] += 1

    def ent(lst, n, skip=()):
        lim = add(hoje, -n)
        return sum(1 for x in lst if x['cr'] > lim and x['cr'] not in skip)

    parados = 0
    alertas = cfg['alerta_pq_dias']
    for p in pq:
        if p['ph'] in (0, 1, 2):
            lim = alertas.get(PQ_FASES[p['ph']])
            if lim is not None and (D(hoje) - D(p['si'])).days > lim:
                parados += 1
    mig = tuple(cfg.get('migracao', []))
    return {
        'funil_pq': [{'fase': PQ_FASES[i], 'n': funil_pq[i]} for i in range(6)],
        'funil_crm': [{'fase': CRM_FASES[i], 'n': funil_crm[i]} for i in range(7)],
        'entrada': {'pq_7d': ent(pq, 7), 'pq_30d': ent(pq, 30), 'crm_7d': ent(crm, 7, mig), 'crm_30d': ent(crm, 30, mig)},
        'em_andamento': {'pq': sum(funil_pq[:4]), 'crm': sum(funil_crm[:5])},
        'parados_pq': parados,
    }


def build(pq, crm, cfg, hoje):
    out = {'setor': 'Novos Negócios'}
    out.update(placar(pq, crm, cfg, hoje))
    out.update(agregados(pq, crm, cfg, hoje))
    return out


def load_cfg(path='config/metas.json'):
    """As metas podem vir da variavel de ambiente TV_METAS_JSON (segredo do GitHub), para nao ficarem no codigo."""
    import os
    env = os.environ.get('TV_METAS_JSON', '').strip()
    return json.loads(env) if env else json.load(open(path, encoding='utf-8'))
