import { QuestSteps } from '@/components/ui/QuestSteps/QuestSteps';
import { Section } from '@/components/ui/Section/Section';
import { installSteps } from '@/data/homeContent';
import styles from './InstallSection.module.css';

export function InstallSection() {
  return (
    <Section id="instalar" tag="02" title="Quest: instalar a tradução">
      <QuestSteps steps={installSteps} />
      <div className={styles.sideQuest}>
        <h3>🎮 Side quest: Steam Deck</h3>
        <p>
          Baixe o zip <b>Steam Deck / Linux</b> do jogo e vá para o <b>Modo Desktop</b> (botão Steam → Ligar/Desligar → Mudar para a área de
          trabalho). Clique com o botão direito no zip → <b>Extrair aqui</b>, abra a pasta e dê dois cliques em <code>Instalar.sh</code> →{' '}
          <b>Executar</b>. O jogo é achado sozinho, na memória interna ou no cartão SD. Depois é só voltar ao Modo de Jogo. Para remover,
          rode o <code>Instalar.sh</code> de novo e escolha <b>Desinstalar</b>.
        </p>
      </div>
    </Section>
  );
}
