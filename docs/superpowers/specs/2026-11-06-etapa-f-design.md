# Etapa F — Integração e validação final

## Intenção

Concluir a etapa F sobre a versão integrada em `origin/dev`, preservando as entregas válidas locais e deixando a aplicação pronta para a validação final antes do merge em `main`.

## Objetivos

- Usar `origin/dev` (`a4e9eff`) como fonte das implementações de veículos, vagas, permanências e dashboard.
- Incorporar a migration que cria as vagas A01–A10 para carros e B01–B05 para motos.
- Incorporar o middleware CORS, inclusive respostas `OPTIONS` com HTTP 204.
- Substituir os testes que esperam HTTP 501 por testes dos CRUDs, filtros, conflitos e regras de permanência.
- Corrigir IDs inválidos para retornarem erro controlado, sem HTTP 500.
- Impedir que a edição comum de uma vaga ocupada a transforme implicitamente em livre.
- Validar configuração Django, migrations, suíte automatizada e execução via Docker Compose.

## Não objetivos

- Não fazer o merge de `dev` em `main` nesta etapa.
- Não redesenhar o frontend nem alterar o contrato público já utilizado por ele.
- Não substituir Django, SQLite, Nginx ou a estrutura Docker existente.

## Restrições

- O trabalho local não commitado da `feature/tarefa-f` deve ser preservado até que a nova base esteja validada.
- A aplicação deve continuar aceitando URLs com e sem barra final.
- A persistência SQLite deve continuar no volume Docker configurado.
- Datas permanecem em ISO 8601 e valores monetários são calculados com `Decimal`.

## Abordagens consideradas

1. **Base limpa em `origin/dev` e reaplicação seletiva da etapa F (escolhida):** reduz conflitos e evita carregar os placeholders locais que ainda retornam 501.
2. **Merge direto na árvore de trabalho atual:** preservaria a disposição atual do índice, mas criaria conflitos nos arquivos modificados simultaneamente e aumentaria o risco de integrar testes obsoletos.

## Desenho escolhido

A versão de `origin/dev` será materializada em uma área de trabalho Git isolada. Sobre ela serão reaplicados migration e CORS, e a suíte será reescrita segundo o comportamento final. Cada correção funcional será conduzida por teste de regressão. A árvore original permanecerá intocada como cópia de segurança até a validação.

## Critérios de conclusão

- Nenhum endpoint final retorna 501.
- Banco novo recebe exatamente as 15 vagas iniciais.
- CRUDs e filtros retornam os códigos HTTP acordados.
- Entrada e saída preservam a consistência entre permanência e vaga.
- IDs inválidos retornam HTTP 400 e recursos inexistentes retornam HTTP 404.
- CORS e `OPTIONS` funcionam em respostas normais e de erro.
- Toda a suíte automatizada passa.
- `docker compose config` é válido e, com o daemon disponível, build, subida, roteiro de entrada/saída e reinício persistente são validados.

