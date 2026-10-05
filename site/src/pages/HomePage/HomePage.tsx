import { GameCard } from '@/components/games/GameCard/GameCard';
import { GameGrid } from '@/components/games/GameGrid/GameGrid';
import { UpcomingGameCard } from '@/components/games/UpcomingGameCard/UpcomingGameCard';
import { Hero } from '@/components/home/Hero/Hero';
import { InstallSection } from '@/components/home/InstallSection/InstallSection';
import { SecuritySection } from '@/components/home/SecuritySection/SecuritySection';
import { SupportSection } from '@/components/home/SupportSection/SupportSection';
import { PageLayout } from '@/components/layout/PageLayout/PageLayout';
import { Faq } from '@/components/ui/Faq/Faq';
import { Section } from '@/components/ui/Section/Section';
import { publishedGames } from '@/data/games';
import { homeFaq } from '@/data/homeContent';
import { DEFAULT_DISCLAIMER, homeNavigation } from '@/data/navigation';

export function HomePage() {
  return (
    <PageLayout brandHref="#inicio" navLinks={homeNavigation} disclaimer={DEFAULT_DISCLAIMER}>
      <Hero />
      <Section
        id="jogos"
        tag="01"
        title="Seleção de jogos"
        subtitle="Escolha o seu jogo, baixe o instalador e pronto. Só funciona com a cópia original do jogo."
      >
        <GameGrid>
          {publishedGames.map((game) => (
            <GameCard key={game.slug} game={game} />
          ))}
          <UpcomingGameCard />
        </GameGrid>
      </Section>
      <InstallSection />
      <SecuritySection />
      <SupportSection />
      <Section id="faq" tag="05" title="FAQ">
        <Faq items={homeFaq} />
      </Section>
    </PageLayout>
  );
}
