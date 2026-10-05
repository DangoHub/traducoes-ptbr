import { DangoLogo } from '../DangoLogo/DangoLogo';
import styles from './Footer.module.css';

export function Footer({ disclaimer }: { disclaimer: string }) {
  return (
    <footer className={styles.footer}>
      <p>
        <DangoLogo small /> DangoHub Traduções · feito por fãs, para fãs
      </p>
      <p className={styles.disclaimer}>{disclaimer}</p>
    </footer>
  );
}
