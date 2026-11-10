"""Leitura dos pipes de Novos Negocios no Pipefy (somente leitura).
O token vem da variavel de ambiente PIPEFY_TOKEN (segredo do GitHub Actions). Nunca escreva o token em arquivo."""
import json, os, time, urllib.request

URL = 'https://api.pipefy.com/graphql'
PIPE_CRM, PIPE_PQ = '307294251', '307293098'


def q(query, var=None, tries=3):
    token = os.environ.get('PIPEFY_TOKEN', '')
    if not token:
        raise RuntimeError('PIPEFY_TOKEN ausente')
    body = json.dumps({'query': query, 'variables': var or {}}).encode()
    for t in range(tries):
        try:
            req = urllib.request.Request(URL, body, {'Content-Type': 'application/json',
                                                     'Authorization': 'Bearer ' + token})
            r = json.load(urllib.request.urlopen(req, timeout=90))
            if r.get('errors'):
                raise RuntimeError(json.dumps(r['errors'])[:500])
            return r['data']
        except Exception:
            if t == tries - 1:
                raise
            time.sleep(3 * (t + 1))


CARDS = '''query($p:ID!,$a:String){allCards(pipeId:$p,first:50,after:$a){pageInfo{hasNextPage endCursor}
 edges{node{id title createdAt due_date done current_phase{id name}
 fields{name field{id type} value array_value}
 phases_history{phase{id} firstTimeIn lastTimeOut}}}}}'''


def cards(pipe):
    out, a = [], None
    while True:
        d = q(CARDS, {'p': pipe, 'a': a})['allCards']
        out += [e['node'] for e in d['edges']]
        if not d['pageInfo']['hasNextPage']:
            return out
        a = d['pageInfo']['endCursor']


def phases(pipe):
    return {x['id']: x['name'] for x in q('query($p:ID!){pipe(id:$p){phases{id name}}}', {'p': pipe})['pipe']['phases']}
