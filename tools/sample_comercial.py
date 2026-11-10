"""Numeros FICTICIOS do Comercial, so para desenhar os slides. Serao trocados pela leitura real do CRM do Comercial."""

def build(hoje):
    def fr(c, a, v, s, mc, ma, mv, ms):
        return {'cadastros': c, 'agendados': a, 'visitas': v, 'vendas': s,
                'meta': {'cadastros': mc, 'agendados': ma, 'visitas': mv, 'vendas': ms}}
    return {'exemplo': True, 'mes': 'Novembro/2026', 'parcial_ate': hoje[8:10] + '/' + hoje[5:7],
            'kpis': {'cadastros': {'v': 14, 'ant': 31}, 'agendados': {'v': 11, 'ant': 24}, 'visitas': {'v': 9, 'ant': 20}, 'vendas': {'v': 1, 'ant': 2}},
            'comparecimento': 79.5, 'qualificacao': 100.0,
            'frentes': {'house': fr(6, 5, 4, 1, 20, 14, 12, 3), 'plataforma': fr(8, 6, 5, 0, 30, 18, 14, 3)},
            'meta_conjunta': {'vendas': {'feito': 1, 'meta': 6}, 'visitas': {'feito': 9, 'meta': 26}}}
