import { Button } from '@/components/ui/Button/Button';
import { cx } from '@/utils/classNames';
import { SUGGEST_GAME_URL } from '@/utils/links';
import cardStyles from '../GameCard/GameCard.module.css';
import styles from './UpcomingGameCard.module.css';

export function UpcomingGameCard() {
  return (
    <article className={cx(cardStyles.card, styles.locked)}>
      <div className={cx(cardStyles.cover, styles.cover)}>
        <span className={styles.lock}>?</span>
      </div>
      <div className={cardStyles.body}>
        <h3 className={cardStyles.title}>Próxima fase</h3>
        <p className={cardStyles.meta}>Em breve</p>
        <p>Novos jogos single-player estão na fila. Quer sugerir um? Abra uma sugestão no GitHub.</p>
        <div className={cardStyles.actions}>
          <Button href={SUGGEST_GAME_URL} external>
            Sugerir jogo
          </Button>
        </div>
      </div>
    </article>
  );
}
