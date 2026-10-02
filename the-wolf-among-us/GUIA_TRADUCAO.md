# Guia de tradução PT-BR — The Wolf Among Us

## Tom e registro

- Noir urbano, anos 80, Nova York. Diálogo seco, cínico, cansado. Frases curtas quando o original é curto.
- Português brasileiro natural de diálogo, **não literal**. Reescreva a ideia como um brasileiro falaria.
- Coloquial é bem-vindo na fala: "tá", "pra", "tô", "né", "cê" (com moderação), "a gente". Narração/menus/fablespedia: português padrão.
- Use "você" por padrão. Nada de "tu" com verbo na 2ª pessoa, nada de português de Portugal.
- Palavrão é parte da obra: traduza com força equivalente, sem suavizar nem exagerar.
  - fuck/fucking → porra, caralho, puta merda, foder, desgraçado (conforme o contexto)
  - shit → merda; bullshit → papo furado / conversa fiada / mentira
  - bloody (britânico, Toad/Woodsman) → maldito, porra, desgraçado
  - asshole → babaca, cuzão; bitch → vadia, piranha (conforme o insulto); bastard → desgraçado, filho da mãe
- Toad fala com sotaque cockney ("mate", "innit", "bleedin'"): em PT-BR use fala popular informal ("cara", "meu chapa", "mano" não), sem inventar sotaque regional.
- Gírias/expressões idiomáticas: equivalente brasileiro ("piece of cake" → "moleza"; "cut it out" → "para com isso").

## Regras técnicas (OBRIGATÓRIAS)

1. **Não altere nada entre chaves `{...}`** (tags de animação, ex.: `{NormalA}`, `{flustereda}`, `{body-StandA}`). Copie idêntico, mesma quantidade, e mantenha cada tag perto da mesma parte da frase.
2. **Não traduza colchetes `[...]` que acompanham uma fala** (notas de direção, ex.: `[annoyed] What?`, `[pickup1]`, `[beat]`). Copie idêntico.
   **EXCEÇÃO:** quando a fala INTEIRA é um único colchete (opção de ação do jogador, ex.: `[Choke him]`, `[Leave him be]`, `[Remain silent]`), ela aparece na tela: **traduza o conteúdo e mantenha os colchetes** → `[Enforcá-lo]`, `[Deixar ele em paz]`, `[Ficar calado]`. Tags `{...}` dentro dela continuam idênticas.
3. Mantenha **o mesmo número de quebras de linha** (`\n`) da fala original.
4. Mantenha marcadores técnicos como `<<ID...`, `<<DATE`, `STUB`, `###` exatamente como estão (pode traduzir o texto em volta).
5. Use apenas caracteres do Windows-1252: acentos do português, aspas “ ” ‘ ’, travessão —, reticências … são permitidos. **Não use** emojis nem caracteres fora disso.
6. Respostas de escolha (opções do jogador) e textos de menu devem ser **curtos** — no máximo uns 30% mais longos que o inglês. Ex.: "Hey." → "Ei."; "Lie." → "Mentir."; "[Remain silent]"/"..." → igual.
7. Opções no formato de ação curtas: use infinitivo ou imperativo curto, ex.: "Grab him" → "Agarrar ele" (prefira "Agarrá-lo" se couber), "Look at the body" → "Olhar o corpo".
8. Se a fala for só `...`, `???`, um nome próprio ou um número, devolva igual.
9. Textos de desenvolvimento (anotações de roteiro em caixa alta, "STUB", instruções) também devem ser traduzidos, mantendo marcadores.

## Glossário (Fábulas — padrão da edição brasileira dos quadrinhos)

| Inglês | PT-BR |
|---|---|
| Fables / a Fable | Fábulas / uma Fábula |
| Fabletown | Cidade das Fábulas |
| Mundy / Mundies | mundano / mundanos |
| the Homelands | as Terras Natais |
| the Farm | a Fazenda |
| glamour | glamour (o feitiço de disfarce) |
| the Business Office | o Escritório |
| the Woodlands (prédio) | o Woodlands |
| the Book (registro) | o Livro |
| Sheriff | Xerife |
| Deputy Mayor | Vice-prefeito / Vice-prefeita |
| the Big Bad Wolf | o Lobo Mau |
| Snow White / Snow | Branca de Neve / Branca |
| Bigby / Bigby Wolf | Bigby / Bigby Lobo |
| Ichabod Crane / Crane | Ichabod Crane / Crane |
| The Woodsman | o Lenhador |
| Mr. Toad / Toad / TJ | Sr. Sapo / Sapo / TJ |
| Beauty / the Beast | Bela / Fera |
| Bluebeard | Barba Azul |
| The Crooked Man | o Homem Torto |
| Tweedle Dee / Tweedle Dum / the Tweedles | Tweedle Dee / Tweedle Dum / os Tweedles |
| Georgie Porgie | Georgie Porgie |
| Bloody Mary | Bloody Mary |
| Jersey Devil | Diabo de Jersey |
| Tiny Tim | Pequeno Tim |
| Little Mermaid | Pequena Sereia |
| Flycatcher | Papa-Moscas |
| Bufkin | Bufkin |
| Colin (porquinho) | Colin |
| Three Little Pigs | os Três Porquinhos |
| Magic Mirror / Mirror, mirror... | Espelho Mágico / Espelho, espelho meu... |
| Prince Lawrence | Príncipe Lawrence |
| Prince Charming | Príncipe Encantado |
| Cinderella | Cinderela |
| Jack (Jack Horner) | Jack |
| Grendel, Holly, Nerissa, Faith, Lily, Vivian, Gren, Greenleaf, Hans, Kelsey, Swineheart, Johann, Dee, Dum | manter |
| Pudding & Pie / Trip Trap (bares) | Pudding & Pie / Trip Trap |
| Lucky Pawn (loja) | Lucky Pawn |
| witch / witching well | bruxa / Poço das Bruxas |
| Thirteenth Floor | Décimo Terceiro Andar |
| ribbon | fita |
| the Crooked Man's men | os capangas do Homem Torto |

Nomes de personagens em CAIXA ALTA no campo "who" são só referência de quem fala — **não traduza** esse campo.
