import type { CSSProperties } from 'react';
import type { TranslationProgress } from '@/models/game';
import styles from './ProgressBar.module.css';

export function ProgressBar({ label, percent }: TranslationProgress) {
  return (
    <div className={styles.bar}>
      <span>{label}</span>
      <div className={styles.track} aria-hidden="true">
        <i style={{ '--progress': `${percent}%` } as CSSProperties} />
      </div>
      <b>{percent}%</b>
    </div>
  );
}
