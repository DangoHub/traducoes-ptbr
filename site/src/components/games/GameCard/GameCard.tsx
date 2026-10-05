import type { Game } from '@/models/game';
import { Button } from '@/components/ui/Button/Button';
import { cx } from '@/utils/classNames';
import { ProgressBar } from '../ProgressBar/ProgressBar';
import styles from './GameCard.module.css';

export function GameCard({ game }: { game: Game }) {
  const { release } = game;
  return (
    <article className={styles.card}>
      <div className={styles.cover}>
        <img src={game.coverUrl} alt={`Capa de ${game.title}`} loading="lazy" />
        <span className={cx(styles.badge, styles[game.badge.tone])}>{game.badge.label}</span>
      </div>
      <div className={styles.body}>
        <h3 className={styles.title}>{game.title}</h3>
        <p className={styles.meta}>
          {game.studio} · Steam build <code>{game.steamBuild}</code>
        </p>
        <p>{game.description}</p>
        <div className={styles.progress}>
          {game.progress.map((item) => (
            <ProgressBar key={item.label} {...item} />
          ))}
        </div>
        <div className={styles.actions}>
          {release ? (
            <>
              <Button variant="download" href={release.windowsUrl} grow>
                ⬇ Windows (.zip)
              </Button>
              <Button variant="deck" href={release.linuxUrl} grow>
                🎮 Steam Deck / Linux
              </Button>
            </>
          ) : (
            <Button disabled>⏳ Download em breve</Button>
          )}
        </div>
        {release && (
          <>
            <Button variant="virusTotal" href={release.virusTotalUrl} external>
              🛡️ VirusTotal: 0 detecções
            </Button>
            <a className={styles.verify} href={release.notesUrl} target="_blank" rel="noopener noreferrer">
              🔎 SHA-256 e notas da versão
            </a>
          </>
        )}
      </div>
    </article>
  );
}
