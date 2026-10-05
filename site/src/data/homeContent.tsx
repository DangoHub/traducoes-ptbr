import type { Achievement, FaqItem, Step } from '@/models/content';
import { ISSUES_URL } from '@/utils/links';
import { publishedGames } from './games';

export const heroStats = [
  { value: String(publishedGames.length), label: 'jogos traduzidos' },
  { value: '39 mil+', label: 'falas traduzidas' },
  { value: 'R$ 0', label: 'pra sempre' },
];

export const heroDialogue = [
  { speaker: '???', line: 'A gente tem plano B pro plano B!' },
  { speaker: '???', line: 'Acho que essa festa do chá não é bem a praia da Nahatra.' },
];

export const installSteps: Step[] = [
  {
    title: 'Feche o jogo',
    description: 'O instalador precisa mexer nos arquivos do jogo, então ele não pode estar aberto.',
  },
  {
    title: 'Baixe e extraia o zip',
    description: (
      <>
        Clique com o botão direito no zip → <b>Extrair tudo...</b>, abra a pasta <code>Traducao_PTBR_...</code> e execute o programa. Não
        precisa de administrador. Se o Windows mostrar <em>"O Windows protegeu o computador"</em>, clique em{' '}
        <b>Mais informações → Executar assim mesmo</b>. Veja na seção de segurança por que esse aviso aparece.
      </>
    ),
  },
  {
    title: 'Clique em "Instalar tradução"',
    description: (
      <>
        O jogo é encontrado sozinho pela Steam. Se não for, use <b>Procurar...</b> e aponte a pasta do jogo.
      </>
    ),
  },
  {
    title: 'Jogue!',
    description: (
      <>
        Para voltar ao original: abra o instalador e clique em <b>Desinstalar</b>, ou use <b>Verificar integridade dos arquivos</b> na
        Steam.
      </>
    ),
  },
];

export const achievements: Achievement[] = [
  {
    icon: '📜',
    title: 'Código 100% aberto',
    description: 'O instalador e todas as traduções estão no GitHub. Dá para ler cada linha antes de rodar.',
  },
  {
    icon: '🤖',
    title: 'Build automático no GitHub',
    description:
      'Os executáveis são gerados pelo GitHub Actions direto do código público, não no PC de alguém. O log de cada build fica visível.',
  },
  {
    icon: '🔏',
    title: 'Atestação de origem',
    description: 'Cada arquivo recebe uma atestação assinada (Sigstore) que prova de qual commit e de qual build ele saiu.',
  },
  {
    icon: '#️⃣',
    title: 'Hash SHA-256',
    description: 'Toda versão publica o SHA-256 dos arquivos. Se um byte mudar, o hash muda.',
  },
  {
    icon: '🛡️',
    title: 'Análise no VirusTotal',
    description: 'Os arquivos são enviados ao VirusTotal (mais de 60 antivírus) e o link do resultado fica nas notas da versão.',
  },
  {
    icon: '↩️',
    title: 'Desinstalação limpa',
    description: 'Nada é apagado. O instalador guarda um backup e a desinstalação devolve o jogo ao original, byte a byte.',
  },
];

export const supportPerks = [
  '☕ 1 café = mais umas mil falas traduzidas antes de dormir',
  '🛠️ Mantém as traduções vivas quando o jogo recebe patch (e quebra tudo)',
  '🎮 Teste no Windows e no Steam Deck, porque "na minha máquina funciona" não basta',
  '🔏 Ajuda a pagar o certificado digital, pro Windows parar de olhar torto pro instalador',
];

export const homeFaq: FaqItem[] = [
  {
    question: 'Preciso ter o jogo original?',
    answer:
      'Sim. A tradução só substitui os textos e não inclui nenhum arquivo do jogo. Funciona com a versão da Steam indicada em cada card.',
  },
  {
    question: 'O jogo atualizou e a tradução sumiu. E agora?',
    answer: 'Rode o instalador de novo. Se a atualização trouxe texto novo, ele aparece em inglês até sair uma versão nova da tradução.',
  },
  {
    question: 'Funciona no Steam Deck?',
    answer: (
      <>
        Sim! Cada jogo tem um zip <b>Steam Deck / Linux</b> com o instalador <code>Instalar.sh</code>. Ele roda no Modo Desktop, não precisa
        instalar nada (o SteamOS já traz tudo que ele usa) e acha o jogo na memória interna ou no cartão SD.
      </>
    ),
  },
  {
    question: 'Por que no Garden of Witches eu escolho "English"?',
    answer: 'O jogo não tem opção de português, então a tradução ocupa o lugar do inglês.',
  },
  {
    question: 'Algumas falas do The Wolf Among Us estão sem legenda.',
    answer: 'Isso acontece no jogo original: cerca de 756 falas (como as de "Anteriormente em...") só têm áudio, sem texto, até em inglês.',
  },
  {
    question: 'Achei um erro de tradução. Como aviso?',
    answer: (
      <>
        Abra uma{' '}
        <a href={ISSUES_URL} target="_blank" rel="noopener noreferrer">
          issue no GitHub
        </a>{' '}
        com um print ou o texto da fala.
      </>
    ),
  },
  {
    question: 'Isso é pirataria?',
    answer: 'Não. É uma tradução de fãs, sem fins lucrativos, que exige o jogo comprado. Nenhum arquivo do jogo é distribuído.',
  },
];
