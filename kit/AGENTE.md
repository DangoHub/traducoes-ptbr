# Regras do subagente tradutor (vale para todos os jogos)

Você recebe lotes prontos. Não explore o repositório nem a pasta do jogo: tudo o que precisa está
neste arquivo, no `GUIA_TRADUCAO.md` do jogo e nos lotes.

## Entrada: `chunks/<lote>.json`

Lista de itens, na ordem em que aparecem no jogo:

```json
{"k": "1", "cena": "FF_PrisonArrival_Fiend_2", "quem": "Jenna (F)", "en": "Oh look, a bad guy."}
{"k": "2", "quem": "Fiend (F)", "en": "Clothes."}
{"k": "3", "tipo": "escolha", "en": "Put on the rags."}
```

- `k`: chave do item. É o que você devolve.
- `cena`: aparece no primeiro item de cada conversa ou tela. Os itens seguintes, sem `cena`,
  pertencem à mesma conversa, até surgir outra `cena`. Use o contexto da conversa inteira.
- `quem`: quem fala. `(F)` = feminino e `(M)` = masculino. Use isso para a concordância:
  "I'm tired" dito por `(F)` vira "Tô cansada". Sem `quem`, deduza pelo contexto.
- `tipo`: quando não é fala comum. `escolha` = opção que o jogador clica, que deve ser curta.
  Outros tipos, como `nome de item` ou `texto do diario`, só descrevem onde o texto aparece.
- `en`: o texto a traduzir.

## Saída: `out/<lote>.json`

Um único objeto JSON, em UTF-8, com **todas** as chaves do lote e nada além delas:

```json
{"1": "Olha só, um vilão.", "2": "Roupas.", "3": "Vestir os trapos."}
```

Grave o arquivo inteiro de uma vez. Depois rode `python -m kit validar <jogo> <lote>` na raiz do
repositório e corrija até aparecer **0 erros**. Os avisos, como escolha longa ou texto igual ao inglês,
são para você conferir. Se estiver certo, pode deixar.

## Regras que o validador cobra

1. **Tags idênticas e na mesma quantidade:** `<i>`, `</color>`, `<color=perversion>`, `<b>`, `{0}`,
   `#TableNum#` e similares. Mantenha cada tag em volta do mesmo trecho de sentido. Nunca traduza o que
   está dentro de uma tag.
2. **O mesmo número de quebras de linha (`\n`)** do original.
3. **Nunca deixe um item vazio.** Se o texto for só `...`, um nome ou uma onomatopeia, devolva igual
   ou adaptado, como em "Ugh..." → "Argh...".

## Regras de qualidade

- **Português do Brasil natural, não literal.** Reescreva a ideia como um brasileiro diria. Use
  "você", nunca "tu" com verbo na 2ª pessoa nem português de Portugal.
- **Coloquial na fala** ("tô", "pra", "tá", "a gente") e **português padrão** em menus, itens e
  descrições.
- **Mantenha o tamanho próximo do original**, porque o texto aparece em caixas com espaço limitado.
  Escolhas e botões devem ter no máximo uns 30% a mais de caracteres que o inglês.
- **Preserve o estilo da fala:** gaguejos ("B-But" → "M-Mas"), alongamentos ("Yesss" → "Simmm"),
  `~`, `..~`, risadas ("ehehe"), reticências e travessões, tudo como no original.
- **Nomes próprios ficam como estão,** salvo se o glossário do jogo disser o contrário.
- **Consistência:** a mesma frase ou o mesmo termo recebe a mesma tradução dentro do lote e de acordo
  com o glossário.
- **Não junte, não divida e não reordene itens.** Um `k` corresponde a uma tradução.
- **Dúvidas de glossário:** escolha a melhor opção, siga em frente e cite a dúvida na resposta final,
  em no máximo 5 linhas.
