import type { ReactNode } from 'react';
import { cx } from '@/utils/classNames';
import styles from './GameGrid.module.css';

export function GameGrid({ children, single = false }: { children: ReactNode; single?: boolean }) {
  return <div className={cx(styles.grid, single && styles.single)}>{children}</div>;
}
