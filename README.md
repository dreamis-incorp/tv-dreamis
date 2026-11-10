# TV Dreamis (Gamificação)

Página para a TV da sala do time: slides rotativos com os números de cada setor, atualizados sozinhos (4x/dia, seg a sex) por GitHub Actions. Leitura somente-leitura no Pipefy. Os dados vão **criptografados** (AES-GCM) e só abrem com a senha da TV.

## Estrutura
- `site/` página da TV (HTML estático)
- `sync/` leitura do Pipefy, cálculo do placar, criptografia (`run.py` é o ponto de entrada)
- `config/metas.json` metas provisórias (plano de outubro; Daniel define as oficiais)
- `tools/` dados de exemplo e script de screenshots; `tests/` testes da lógica de metas
- `.github/workflows/update.yml` agenda e publicação no Pages

## Configuração (uma vez)
1. Suba todos os arquivos para o repositório `tv-dreamis` da organização `dreamis-incorp`.
2. Em **Settings > Secrets and variables > Actions**, crie:
   - `PIPEFY_TOKEN` (token pessoal do Pipefy, leitura; nunca cole em chat)
   - `TV_PASSWORD` (senha da TV, mínimo 8 caracteres)
   - `TV_METAS_JSON` (opcional: conteúdo de `config/metas.json`, para as metas não ficarem no código)
3. Em **Settings > Pages**, escolha Source = GitHub Actions (plano gratuito de organização pode exigir repositório público; os dados continuam criptografados).
4. Em **Actions > Atualizar TV Dreamis > Run workflow**, rode primeiro com "exemplo" marcado para testar, depois sem.
5. Na TV, abra `https://SUA-URL-DO-PAGES/#s=SENHA` (a senha vai no link, depois do `#`, e some da barra ao abrir). Salve como favorito/página inicial e deixe em tela cheia (F11). Não circule esse link.
6. Tela na vertical: se o aparelho não girar a imagem, use `?giro=90` (ou 270) antes do `#`: `https://URL/?giro=90#s=SENHA`.

Layout: 1080x1920 (vertical), um slide por setor (Novos Negócios, Comercial), 25 s cada.

## Pendências
- Comercial: aguardando o código de extração do Ale; hoje usa dados de exemplo (faixa "DADOS DE EXEMPLO").
- Metas oficiais (Daniel). Validar cores/fontes com o brandbook.
