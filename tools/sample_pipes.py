"""Cards FICTICIOS no formato leve do Pipefy para Comercial, Incorporacao e Marketing. Servem para testar o codigo real sem acessar o Pipefy."""
import random
from datetime import datetime, timedelta, timezone

BRT = timezone(timedelta(hours=-3))


def ts(d):
    return datetime(d.year, d.month, d.day, 12, 0, tzinfo=BRT).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def card(created, phase, path, fields=None, labels=(), due=None):
    return {'id': 'x', 'createdAt': ts(created), 'due_date': ts(due) if due else None, 'done': False,
            'current_phase': {'id': '1', 'name': phase}, 'labels': [{'name': l} for l in labels],
            'fields': [{'name': k, 'value': v} for k, v in (fields or {}).items()],
            'phases_history': [{'phase': {'id': '1', 'name': n}, 'firstTimeIn': ts(d), 'lastTimeOut': None} for n, d in path]}


def make(hoje, seed=11):
    r = random.Random(seed)
    H = datetime.strptime(hoje, '%Y-%m-%d').date()
    br = lambda d, h='14:00': d.strftime('%d/%m/%Y ') + h

    com = []
    origens = ['Mídia Off', 'Meta', 'Indicação', 'Evento', 'Plataforma de imobiliárias', 'Clube em exposição']
    for i in range(140):
        cr = H - timedelta(days=r.randint(0, 65)); path = [('Cadastro', cr)]; f = {}
        f['Por onde veio o cliente'] = r.choice(origens) if r.random() > .06 else ''
        if r.random() > .05:
            f['Produto Dreamis de interesse'] = r.choice(['Tauá', 'EZA'])
        fase = 'Cadastro'; x = r.random()
        if x > .35:
            fase = 'Lead Pré-Qualificado'; path.append((fase, cr + timedelta(days=1)))
        if x > .6:
            ag = cr + timedelta(days=r.randint(2, 8)); f['Data e hora do atendimento agendado'] = br(ag)
            fase = 'Atendimento Agendado' if ag > H else 'Pós Atendimento'
            if ag <= H and r.random() > .2:
                f['Data e hora do atendimendo realizado'] = br(ag); path.append(('Pós Atendimento', ag))
            elif ag <= H:
                fase = 'Follow Up'
        if x > .93 and 'Data e hora do atendimendo realizado' in f:
            fase = 'Concluído'; path.append((fase, min(H, cr + timedelta(days=20))))
        lab = [r.choice(['alessandro', 'karina', 'arthur', 'raquel']), r.choice(['tauá', 'eza'])]
        com.append(card(cr, fase, path, f, lab))

    tau = []
    et = ["1.Jantar Briefing", "2.Validação de layout TAKT", "3.Layout apartamento", "4.Validação de oramento preliminar TAKT",
          "5.Orçamento Preliminar", "6.Renders e Imagens", "7.Projeto Executivo", "8.Sucesso ! Contrato assinado"]
    for i in range(15):
        cr = H - timedelta(days=r.randint(5, 120)); k = r.choice([0, 0, 0, 2, 2, 2, 2, 2, 4, 4, 4, 4, 7, 7, 8])
        fase = et[k] if k < 8 else 'Dificuldade em avançar no processo'
        path = [(et[j], cr + timedelta(days=j * 6)) for j in range(min(k, 7) + 1)]
        due = H + timedelta(days=r.randint(-8, 10))
        tau.append(card(cr, fase, path, due=due))
    hom = []
    for i in range(30):
        cr = H - timedelta(days=r.randint(1, 90)); fase = r.choice(['Caixa de entrada', 'Fazendo', 'Fazendo', 'Projeto Teste', 'Homologado', 'Homologado'])
        path = [(fase, cr)]
        hom.append(card(cr, fase, path))
    redes = []
    for i in range(72):
        cr = H - timedelta(days=r.randint(0, 100)); fase = r.choice(['Caixa de ideias', 'Planejamento', 'Produção', 'Publicação', 'Performance'] + ['Concluído'] * 12)
        path = [(fase, cr + timedelta(days=r.randint(1, 20)) if fase == 'Concluído' else cr)]
        path = [(n, min(d, H)) for n, d in path]
        if fase == 'Concluído':
            path.append(('Publicação', min(H, path[0][1] - timedelta(days=2))))
        redes.append(card(cr, fase, path))
    ges = []
    for i in range(31):
        cr = H - timedelta(days=r.randint(0, 60)); fase = r.choice(['Radar', 'Fazendo', 'Em Produção', 'Concluído', 'Concluído', 'Alinhamento Necerrário'])
        ges.append(card(cr, fase, [(fase, min(H, cr + timedelta(days=r.randint(0, 15))))]))
    off = [card(H - timedelta(days=r.randint(1, 90)), f, [(f, H)]) for f in ['RADAR'] * 10 + ['QUALIFICAÇÃO'] * 5 + ['CONTRATO'] * 9 + ['ATIVO'] * 10 + ['CONCLUÍDO'] * 7]
    return {'com': com, 'tau': tau, 'hom': hom, 'redes': redes, 'ges': ges, 'off': off}
