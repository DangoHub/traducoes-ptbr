import { cx } from '@/utils/classNames';
import styles from './DangoLogo.module.css';

export function DangoLogo({ small = false }: { small?: boolean }) {
  return (
    <span className={cx(styles.dango, small && styles.small)} aria-hidden="true">
      <i />
      <i />
      <i />
    </span>
  );
}
