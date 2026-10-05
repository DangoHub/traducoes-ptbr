import type { ReactNode } from 'react';

export interface NavLink {
  label: string;
  href: string;
  highlighted?: boolean;
}

export interface FaqItem {
  question: string;
  answer: ReactNode;
}

export interface Step {
  title: string;
  description: ReactNode;
}

export interface Achievement {
  icon: string;
  title: string;
  description: string;
}
