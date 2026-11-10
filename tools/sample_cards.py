"""Cards FICTICIOS no formato da API do Pipefy, so para testar a TV sem acessar o Pipefy.
Nenhum nome real: os titulos sao 'Terreno 001' etc."""
import random
from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))
CRM_PH = {'344403188': 'Triagem de novos terrenos', '344464499': 'Estudo de Viabilidade', '343968259': 'Apresentação e Proposta',
          '343968260': 'Negociação', '343968263': 'Contrato', '343968261': 'Sucesso', '343968262': 'Não foi dessa vez',
          '344474594': 'Incorporado a projeto'}
PQ_PH = {'343961287': 'Caixa de entrada', '343961288': 'Prospectando', '343961369': 'Amadurecimento',
         '343961368': 'Composição de área', '343961289': 'Sucesso', '343961360': 'Não foi dessa vez'}


def ts(d, h=12):
    return datetime(d.year, d.month, d.day, h, 0, tzinfo=BRT).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def br(d):
    return d.strftime('%d/%m/%Y')


def make(hoje, seed=7):
    rnd = random.Random(seed)
    H = datetime.strptime(hoje, '%Y-%m-%d').date()
    crm_ids, pq_ids = list(CRM_PH), list(PQ_PH)

    def hist(ids, path, start, end_cur=True):
        out, d = [], start
        for k, pid in enumerate(path):
            nxt = d + timedelta(days=rnd.randint(2, 12))
            last = k == len(path) - 1
            if nxt > H:
                nxt = H
            out.append({'phase': {'id': pid}, 'firstTimeIn': ts(d), 'lastTimeOut': None if last else ts(nxt)})
            d = nxt
        return out

    pq = []
    dist = [14, 30, 12, 4, 8, 22]
    n = 0
    for fi, cnt in enumerate(dist):
        for _ in range(cnt):
            n += 1
            start = H - timedelta(days=rnd.randint(1, 80))
            path = pq_ids[:fi + 1] if fi < 5 else pq_ids[:3] + [pq_ids[5]]
            h = hist(pq_ids, path, start)
            flds = []
            if fi >= 1 and rnd.random() < .45:
                d = max(start + timedelta(days=rnd.randint(0, 20)), H - timedelta(days=rnd.randint(0, 19)))
                if d >= datetime(2026, 10, 22).date() and d <= H:
                    flds.append({'name': 'Pré-proposta enviada em', 'field': {'id': 'x1', 'type': 'date'}, 'value': br(d), 'array_value': None})
            if fi >= 2:
                flds.append({'name': 'Interesse do proprietário', 'field': {'id': 'interesse_do_propriet_rio', 'type': 'select'},
                             'value': rnd.choice(['Positivo', 'Muito interesse', 'Inconclusivo', 'Sem interesse']), 'array_value': None})
                if rnd.random() < .6:
                    d = H - timedelta(days=rnd.randint(0, 25))
                    if d >= datetime(2026, 10, 15).date():
                        flds.append({'name': 'Data da reunião', 'field': {'id': 'x2', 'type': 'date'}, 'value': br(d), 'array_value': None})
            pq.append({'id': f'pq{n}', 'title': f'Terreno {n:03d}', 'createdAt': ts(start), 'due_date': None, 'done': False,
                       'current_phase': {'id': path[-1], 'name': PQ_PH[path[-1]]}, 'fields': flds, 'phases_history': h})
    crm = []
    cdist = [4, 3, 3, 2, 1, 1, 3]
    n = 0
    for fi, cnt in enumerate(cdist):
        for _ in range(cnt):
            n += 1
            start = H - timedelta(days=rnd.randint(1, 80))
            path = crm_ids[:fi + 1] if fi < 6 else crm_ids[:2] + [crm_ids[6]]
            h = hist(crm_ids, path, start)
            flds = []
            if fi >= 2 and rnd.random() < .7:
                d = H - timedelta(days=rnd.randint(1, 18))
                flds.append({'name': 'Data de envio da proposta', 'field': {'id': 'data_de_envio_da_proposta', 'type': 'date'}, 'value': br(d), 'array_value': None})
            crm.append({'id': f'crm{n}', 'title': f'Terreno CRM {n:03d}', 'createdAt': ts(start), 'due_date': None, 'done': False,
                        'current_phase': {'id': path[-1], 'name': CRM_PH[path[-1]]}, 'fields': flds, 'phases_history': h})
    return crm, pq
