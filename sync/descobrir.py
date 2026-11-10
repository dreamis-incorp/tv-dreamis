"""Lista a ESTRUTURA dos pipes que o token enxerga (nome, fases, campos). Nao le nenhum card nem dado de cliente.
Uso: python3 sync/descobrir.py   (precisa de PIPEFY_TOKEN)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from pipefy import q

def main():
    try:
        orgs = q('{organizations{id name pipes{id name}}}')['organizations']
    except Exception as e:
        print('ERRO ao listar organizacoes:', str(e)[:300]); return
    for o in orgs:
        print(f"\n=== ORGANIZACAO {o['name']} ({o['id']}) | {len(o['pipes'])} pipes")
        for p in o['pipes']:
            try:
                d = q('query($p:ID!){pipe(id:$p){name cards_count phases{name cards_count fields{label type}} start_form_fields{label type}}}', {'p': p['id']})['pipe']
            except Exception as e:
                print(f"\n--- PIPE {p['name']} ({p['id']}): sem acesso ({str(e)[:120]})"); continue
            print(f"\n--- PIPE {d['name']} ({p['id']}) | cards: {d.get('cards_count')}")
            print('  Formulario inicial:', '; '.join(f"{f['label']} [{f['type']}]" for f in d['start_form_fields']) or '-')
            for ph in d['phases']:
                print(f"  Fase: {ph['name']} ({ph.get('cards_count')})")
                if ph['fields']:
                    print('     campos:', '; '.join(f"{f['label']} [{f['type']}]" for f in ph['fields']))

main()
