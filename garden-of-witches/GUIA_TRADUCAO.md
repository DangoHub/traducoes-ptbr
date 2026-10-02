# Guia de localização PT-BR — Garden of Witches

Jogo: roguelite de ação com bruxas, estilo fofo/cômico, com momentos dramáticos. A protagonista é a bruxa **Sil**. As bruxas fazem uma "festa do chá" (Tea Party) periódica para manter Nahatra adormecida e o Jardim (Garden) protegido. Há muito humor, provocação entre amigas e personalidades marcantes.

## Princípios (baseados em guias de localização PT-BR, ex.: Microsoft PT-BR Style Guide, LocalizeDirect, Gest Experts)
1. **Localize, não traduza ao pé da letra.** Entenda a intenção da fala e reescreva como um brasileiro falaria naturalmente. Pode reordenar, dividir ou juntar frases dentro da mesma linha.
2. **Português do Brasil**, nunca de Portugal. Use "você" (não "tu" conjugado à lusitana). Evite regionalismos fortes; gírias leves e coloquialismo são bem-vindos nos diálogos ("tá", "pra", "né", "beleza", "nossa", "caramba", "ué") quando combinarem com a personagem.
3. **Preserve a voz de cada personagem**: a sarcástica continua sarcástica, a fofa continua fofa, a bêbada continua enrolada ("HIC!"). Onomatopeias: adapte (Pfft → Pff, Bwahahaha → Buahahaha, Eek → Ai!/Eita!, Ouch → Ai!, Huh? → Hã?/Ué?, Hmm → Hum, Phew → Ufa).
4. **Humor e trocadilhos**: recrie um equivalente em português em vez de traduzir literalmente.
5. **UI**: textos curtos, claros e escaneáveis. Botões e títulos com no máximo ~30% a mais que o inglês. Use maiúscula só na primeira palavra em títulos/botões (estilo frase), exceto nomes próprios e termos de jogo do glossário (que mantêm a capitalização do glossário).
6. **Gênero**: Sil e a maioria das personagens são mulheres (bruxas). Ao se dirigir ao jogador use formas neutras quando possível; se impossível, use feminino (a jogadora controla a Sil).
7. Pontuação brasileira: "?!" e "!!" podem ficar como no original; reticências "..." mantidas; aspas curvas ou retas como no original.

## REGRAS TÉCNICAS (OBRIGATÓRIAS — quebrar isso trava ou estraga o jogo)
- **Nunca altere** nada entre chaves `{...}` — ex.: `{$Weapon_Damage_More:0.##%}`, `{|$Weapon_Radius_More|:0.##%}`, `{$n:0}`, `{$a}`. Copie exatamente, caractere por caractere. Pode mudar a posição na frase.
- **Nunca altere tags** `<...>` (ex.: `<style=glitchy>`, `</style>`, `<color=...>`, `<br>`). Traduza só o texto entre elas.
- **Crases** `` ` `` marcam palavras-chave destacadas. Mantenha o MESMO número de crases (sempre em pares) e coloque-as em volta do termo traduzido: `` `Scissors` `` → `` `Tesoura` ``.
- Mantenha quebras de linha (`\n` reais dentro do texto) aproximadamente nos mesmos lugares; o número de quebras deve ser igual.
- Colchetes como `[......]` ou `[...!!]` devem ser mantidos.
- Texto que for só `...`, `???`, números ou símbolos: copie igual.
- Não deixe nenhuma linha sem tradução.

## Glossário (use SEMPRE estes termos)

### Personagens e lugares (nomes próprios NÃO se traduzem)
Sil, Fiena, Abigail, Rims, Berry, Rims & Berry, Chloe, Nahatra, Bazira, Shasha, Mary, Maydel, Canele, Kiki, Pipi, Lulu, Mimi — manter.
| EN | PT-BR |
|---|---|
| Conservator | Conservador(a) — use "Conservadora" se o contexto indicar mulher |
| Contaminated Seed / Parasitic Seed | Semente Contaminada |
| Garden / the garden | Jardim / o jardim |
| Tea Party / tea party | Festa do Chá / festa do chá |
| witch / witches | bruxa / bruxas |
| Swamp Witch | Bruxa do Pântano |
| Jewel Witch | Bruxa das Joias |
| Mirror Witch | Bruxa do Espelho |
| The Missing Witch | A Bruxa Desaparecida |
| Lapis Market | Mercado Lápis |
| nightmare(s) | pesadelo(s) |
| swamp | pântano |
| desert | deserto |
| jungle | selva |
| farm | fazenda |
| mirror world | mundo do espelho |

### Modos e menus
| EN | PT-BR |
|---|---|
| Chapter | Capítulo |
| Epilogue | Epílogo |
| Main Story | História Principal |
| Challenge Mode | Modo Desafio |
| Challenge Run | Desafio |
| Endgame Content | Conteúdo Final |
| Recommended Level | Nível Recomendado |
| Unlocked | Desbloqueado(a) |
| Upgrade | Aprimoramento / Aprimorar |
| Level | Nível |
| Settings | Configurações |

### Combate e atributos
| EN | PT-BR |
|---|---|
| DMG / Damage | Dano |
| All DMG | Todo o Dano |
| Critical / Crit | Crítico |
| Critical DMG | Dano Crítico |
| Critical Attack | Ataque Crítico |
| Crit Threshold | Limite de Crítico |
| Guaranteed Crit | Crítico Garantido |
| Attack SPD | Vel. de Ataque |
| Move SPD | Vel. de Movimento |
| Cooldown / CD | Recarga |
| Cooldown Skill | Habilidade com Recarga |
| Combo Count | Nº de Combos |
| Combo | Combo |
| Radius | Raio |
| Range | Alcance |
| Duration | Duração |
| Cast / Cast Time | Conjurar / Tempo de Conjuração |
| Charge | Carga (substantivo) / carregar (verbo) |
| Charge Acceleration | Carga Acelerada |
| Channeling | Canalização |
| Projectile | Projétil |
| Ammo | Munição |
| Stack / Max Stack | Acúmulo / Acúmulo Máx. |
| Gauge | Medidor |
| Blood Gauge | Medidor de Sangue |
| HP | PV |
| Revive | Reviver |
| Invincible | Invencível |
| Buff / Debuff | Bônus / Penalidade |
| Battle / Battles | Batalha / Batalhas |
| Battle Rewards / Rewards | Recompensas de Batalha / Recompensas |
| Attribute(s) (Trait) | Atributo(s) |
| Curse | Maldição |
| Relic | Relíquia |
| Weapon | Arma |
| Spell (Magic) | Feitiço |
| Special Skill | Habilidade Especial |
| Witchcraft | Bruxaria |
| Summon | Invocação (subst.) / invocar (verbo) |
| Doll (Familiar) | Boneca |
| Small Doll / Large Doll / Phantom Doll | Boneca Pequena / Boneca Grande / Boneca Fantasma |
| Needle | Agulha |
| Thread | Linha |
| Crow | Corvo |
| Flower | Flor |
| Dash | Arrancada |
| Sharpness | Afiação |
| Burn | Queimadura |
| Swiftness | Agilidade |
| Ambush | Emboscada |
| Ambush Potency | Potência de Emboscada |
| Counter | Contra-ataque |
| Counter Potency | Potência de Contra-ataque |
| Power Boost | Fortalecimento |
| Spell Rampage | Fúria Mágica |
| Mark | Marca |

### Armas
Scissors → Tesoura; Giant Scissors → Tesoura Gigante; Magic Scissors → Tesoura Mágica; Broken Scissors → Tesoura Quebrada; Singing Scissors → Tesoura Cantante; Lapis Scissors → Tesoura Lápis.

### Feitiços
Gem Shards → Estilhaços de Gema; Slash → Corte Ceifador; Ambush → Emboscada; Counter → Contra-ataque; Summon Doll → Invocar Boneca; Sewing Wheel → Roda de Costura; Rush → Investida; Butterfly Walk → Passo de Borboleta; Shadow Surge → Onda Sombria; Blood Marble → Esfera de Sangue; Fireball → Bola de Fogo.

### Habilidades especiais
Swamp Echo → Eco do Pântano; Swamp Breath → Sopro do Pântano; Swamp Flow → Fluxo do Pântano; Broken Dream → Sonho Partido.

### Hashtags (manter o #, sem espaços)
#Buff → #Bônus; #Debuff → #Penalidade; #Weapon → #Arma; #Spell → #Feitiço; #CooldownSkill → #HabilidadeComRecarga; #Witchcraft → #Bruxaria; #Cast → #Conjuração; #Charge → #Carga; #Channeling → #Canalização; #Attack → #Ataque; #Projectile → #Projétil; #Needle → #Agulha; #Summon → #Invocação; #Doll → #Boneca; #Flower → #Flor; #Crow → #Corvo; #Combo → #Combo; #Duration → #Duração; #SpecialSkill → #HabilidadeEspecial.

### Relíquias e joias
Traduza os nomes de relíquias/joias de forma natural e evocativa (ex.: Ritual Hammer → Martelo Ritualístico, Empty Hourglass → Ampulheta Vazia, Pocket Monster → Monstrinho de Bolso, Dreamcatcher → Filtro dos Sonhos, Cursed Doll "Kiki" → Boneca Amaldiçoada "Kiki", Broken X → X Quebrado(a), Jeweled X → X com Joias / X Cravejado(a), Cat-Sigil Key → Chave do Selo do Gato).
