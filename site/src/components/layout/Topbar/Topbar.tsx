import type { NavLink } from '@/models/content';
import { cx } from '@/utils/classNames';
import { DangoLogo } from '../DangoLogo/DangoLogo';
import styles from './Topbar.module.css';

interface TopbarProps {
  brandHref: string;
  links: NavLink[];
}

export function Topbar({ brandHref, links }: TopbarProps) {
  return (
    <header className={styles.topbar}>
      <a className={styles.brand} href={brandHref}>
        <DangoLogo />
        <span className={styles.brandText}>
          DANGO<b>HUB</b>
          <small>traduções</small>
        </span>
      </a>
      <nav className={styles.nav} aria-label="Navegação principal">
        {links.map((link) => (
          <a key={link.href} className={cx(styles.link, link.highlighted && styles.highlighted)} href={link.href}>
            {link.label}
          </a>
        ))}
      </nav>
    </header>
  );
}
