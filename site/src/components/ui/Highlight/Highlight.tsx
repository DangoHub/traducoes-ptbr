import type { ReactNode } from 'react';
import styles from './Highlight.module.css';

export function Highlight({ children }: { children: ReactNode }) {
  return <span className={styles.highlight}>{children}</span>;
}
