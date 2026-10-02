# Como verificar os instaladores

Você não precisa confiar na nossa palavra. Cada arquivo publicado pode ser conferido de quatro formas.

## 1. Código aberto

Tudo o que o instalador faz está em `projetos/<jogo>/src/`. As traduções estão em
`projetos/<jogo>/src/traducao_ptbr.json`. O `.zip` de cada release traz uma cópia desse código na pasta `fonte/`.

## 2. Build feito pelo GitHub, não no PC de alguém

Os arquivos das releases são gerados pelo workflow
[`release.yml`](.github/workflows/release.yml) numa máquina limpa do GitHub Actions. As notas de cada
release linkam o commit exato e o log completo do build.

## 3. Hash SHA-256

Cada release traz o arquivo `SHA256SUMS.txt` e a mesma lista nas notas. No PowerShell:

```powershell
Get-FileHash .\Instalador_Traducao_PTBR_The_Wolf_Among_Us.exe -Algorithm SHA256
```

O valor tem que ser idêntico ao publicado. Se não for, não execute o arquivo.

## 4. Atestação de origem (Sigstore)

Prova criptograficamente que o arquivo saiu do workflow deste repositório, em qual commit. Precisa do
[GitHub CLI](https://cli.github.com/):

```powershell
gh attestation verify .\Instalador_Traducao_PTBR_The_Wolf_Among_Us.exe --repo DangoHub/traducoes-ptbr
```

## 5. VirusTotal

Quando o secret `VT_API_KEY` está configurado, o workflow envia o `.exe` e o `.zip` ao
[VirusTotal](https://www.virustotal.com/) e coloca o link da análise nas notas da release.

## Por que o Windows ou o antivírus reclamam?

- **SmartScreen ("O Windows protegeu o computador"):** o instalador ainda não tem assinatura digital
  (certificado de code signing). O aviso some com a reputação do arquivo ou com um certificado.
- **Falso positivo de antivírus:** o instalador é empacotado com o PyInstaller. Como ele é muito usado,
  inclusive por quem faz malware, alguns antivírus marcam qualquer programa feito com ele. É um problema
  conhecido ([PyInstaller e antivírus](https://github.com/pyinstaller/pyinstaller/blob/develop/.github/ISSUE_TEMPLATE/antivirus.md)).
  Use as verificações acima. Se encontrar um falso positivo, abra uma issue com o link do VirusTotal.

## O que o instalador mexe no seu PC

- **Garden of Witches:** acrescenta o texto traduzido ao final do `resources.assets` e guarda um backup
  em `Garden of Witches_Data/ptbr_mod_backup.json`. Desinstalar devolve o arquivo byte a byte ao original.
- **The Wolf Among Us:** não altera nenhum arquivo original; só cria arquivos `*PTBR*` na pasta `Pack`.
  Desinstalar apaga esses arquivos.

Nenhum dos dois acessa a internet, coleta dados ou roda em segundo plano. Fora da pasta do jogo, a única
coisa que eles fazem é ler (sem alterar) o registro do Windows para descobrir onde a Steam está instalada.
