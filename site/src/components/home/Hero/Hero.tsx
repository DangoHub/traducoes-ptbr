import { Button } from '@/components/ui/Button/Button';
import { Highlight } from '@/components/ui/Highlight/Highlight';
import { heroDialogue, heroStats } from '@/data/homeContent';
import { REPOSITORY_URL } from '@/utils/links';
import styles from './Hero.module.css';

export function Hero() {
  return (
    <section id="inicio" className={styles.hero}>
      <div>
        <p className={styles.eyebrow}>{'// fan translations PT-BR'}</p>
        <h1 className={styles.title}>
          Jogue em <Highlight>português</Highlight>.
          <br />
          De graça.
        </h1>
        <p className={styles.lead}>
          Traduções feitas por fãs, com cuidado de localização: nada de tradução literal, cada personagem com seu jeito de falar. Instalador
          com um clique, desinstalação limpa e código 100% aberto.
        </p>
        <div className={styles.actions}>
          <Button variant="start" href="#jogos">
            ▶ PRESS START
          </Button>
          <Button variant="ghost" href={REPOSITORY_URL} external>
            Ver código no GitHub
          </Button>
        </div>
        <ul className={styles.stats}>
          {heroStats.map((stat) => (
            <li key={stat.label}>
              <strong>{stat.value}</strong>
              <span>{stat.label}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className={styles.art} aria-hidden="true">
        <div className={styles.window}>
          <div className={styles.windowBar}>
            <span />
            <span />
            <span />
          </div>
          {heroDialogue.map(({ speaker, line }) => (
            <p key={line} className={styles.line}>
              <b>{speaker}:</b> {line}
            </p>
          ))}
          <p className={styles.choice}>
            &gt; Continuar<span className={styles.caret}>_</span>
          </p>
        </div>
      </div>
    </section>
  );
}
