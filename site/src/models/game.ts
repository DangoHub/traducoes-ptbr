import type { ReactNode } from 'react';

export type BadgeTone = 'success' | 'adult';

export interface GameBadge {
  label: string;
  tone: BadgeTone;
}

export interface TranslationProgress {
  label: string;
  percent: number;
}

export interface GameRelease {
  windowsUrl: string;
  linuxUrl: string;
  notesUrl: string;
  virusTotalUrl: string;
}

export interface Game {
  slug: string;
  title: string;
  studio: string;
  steamBuild: string;
  coverUrl: string;
  badge: GameBadge;
  description: ReactNode;
  progress: TranslationProgress[];
  /** Missing while the download is not published yet. */
  release?: GameRelease;
}
