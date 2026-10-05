import type { ReactNode } from 'react';
import { cx } from '@/utils/classNames';
import styles from './Section.module.css';

interface SectionProps {
  title: string;
  tag: string;
  children: ReactNode;
  id?: string;
  eyebrow?: string;
  subtitle?: ReactNode;
  className?: string;
}

export function Section({ title, tag, children, id, eyebrow, subtitle, className }: SectionProps) {
  return (
    <section id={id} className={cx(styles.section, className)}>
      {eyebrow && <p className={styles.eyebrow}>{eyebrow}</p>}
      <h2 className={styles.title}>
        <span className={styles.tag}>{tag}</span> {title}
      </h2>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      {children}
    </section>
  );
}
