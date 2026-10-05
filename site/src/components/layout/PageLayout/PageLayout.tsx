import type { ReactNode } from 'react';
import type { NavLink } from '@/models/content';
import { Footer } from '../Footer/Footer';
import { Topbar } from '../Topbar/Topbar';
import styles from './PageLayout.module.css';

interface PageLayoutProps {
  brandHref: string;
  navLinks: NavLink[];
  disclaimer: string;
  children: ReactNode;
}

export function PageLayout({ brandHref, navLinks, disclaimer, children }: PageLayoutProps) {
  return (
    <>
      <div className={styles.scanlines} aria-hidden="true" />
      <Topbar brandHref={brandHref} links={navLinks} />
      <main>{children}</main>
      <Footer disclaimer={disclaimer} />
    </>
  );
}
