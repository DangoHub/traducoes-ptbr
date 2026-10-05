# Regras do subagente tradutor (vale para todos os jogos)

Você recebe lotes prontos e este arquivo de contexto, que traz as regras e os trechos do guia do jogo que
valem para os seus textos. Não explore o repositório nem a pasta do jogo.

## Entrada: `chunks/<lote>.json`

Lista de itens, um por linha, na ordem em que aparecem no jogo:

```json
{"k": "1", "cena": "FF_PrisonArrival_Fiend_2", "quem": "Jenna (F)", "en": "Oh look, a bad guy."}
{"quem": "Fiend (F)", "en": "Clothes.", "pt": "Roupas."}
{"k": "2", "tipo": "escolha", "en": "Put on the rags.", "rascunho": "Vestir os trapo", "erro": "..."}
```

- `k`: chave do item. É o que você devolve.
- **Item sem `k`** é referência: uma fala já aprovada da mesma conversa, com a tradução em `pt`. Use para
  manter tom, tratamento e continuidade. Não devolva e não altere.
- `cena`: aparece no primeiro item de cada conversa ou tela. Os itens seguintes, sem `cena`,
  pertencem à mesma conversa, até surgir outra `cena`. Use o contexto da conversa inteira.
- `quem`: quem fala. `(F)` = feminino e `(M)` = masculino. Use isso para a concordância:
  "I'm tired" dito por `(F)` vira "Tô cansada". Sem `quem`, deduza pelo contexto.
- `tipo`: quando não é fala comum. `escolha` = opção que o jogador clica, que deve ser curta.
  Outros tipos, como `nome de item` ou `texto do diario`, só descrevem onde o texto aparece.
- `en`: o texto a traduzir.
- `rascunho` e `erro`: tradução anterior que falhou na validação, e o motivo. Corrija o rascunho em vez
  de traduzir do zero.

## Saída: `out/<lote>.json`

Um único objeto JSON, em UTF-8, com as chaves `k` do lote e nada além delas:

```json
{"1": "Olha só, um vilão.", "2": "Vestir os trapos."}
```

Grave o arquivo inteiro de uma vez. Valide uma vez, como o prompt indica. Se houver erro, corrija só os
itens apontados e valide de novo no máximo uma vez: o que sobrar vira um pacote de correção. Os avisos,
como escolha longa ou texto igual ao inglês, não exigem ação.

## Regras que o validador cobra

1. **Tags idênticas, na mesma quantidade e bem aninhadas:** `<i>`, `</color>`, `<color=perversion>`,
   `<b>`, `{0}`, `#TableNum#` e similares. Mantenha cada tag em volta do mesmo trecho de sentido, abra e
   feche na ordem certa (`<b><i>x</i></b>`, nunca `<b><i>x</b></i>`) e nunca traduza o que está dentro
   de uma tag.
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
- **Nomes próprios ficam como estão,** salvo se o guia do jogo disser o contrário.
- **Consistência:** termos do glossário, nomes, itens, menus e botões recebem sempre a mesma tradução.
  Em diálogo, a mesma frase pode variar conforme quem fala, a intenção e a cena ("Really?" pode ser
  espanto, ironia ou dúvida).
- **Não junte, não divida e não reordene itens.** Um `k` corresponde a uma tradução.
- **Dúvidas de glossário:** escolha a melhor opção, siga em frente e cite a dúvida na resposta final,
  em no máximo 5 linhas.
