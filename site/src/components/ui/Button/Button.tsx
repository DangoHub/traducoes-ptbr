import type { ReactNode } from 'react';
import { cx } from '@/utils/classNames';
import styles from './Button.module.css';

export type ButtonVariant = 'start' | 'ghost' | 'download' | 'deck' | 'virusTotal' | 'small';

interface ButtonProps {
  children: ReactNode;
  variant?: ButtonVariant;
  href?: string;
  external?: boolean;
  type?: 'button' | 'submit';
  disabled?: boolean;
  grow?: boolean;
  className?: string;
  onClick?: () => void;
}

export function Button({ children, variant = 'small', href, external, type = 'button', disabled, grow, className, onClick }: ButtonProps) {
  const classes = cx(styles.button, styles[variant], grow && styles.grow, className);
  if (href) {
    return (
      <a className={classes} href={href} {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>
        {children}
      </a>
    );
  }
  return (
    <button className={classes} type={type} disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
}
