import { AgeGate } from '@/components/age-gate/AgeGate/AgeGate';
import { GameCard } from '@/components/games/GameCard/GameCard';
import { GameGrid } from '@/components/games/GameGrid/GameGrid';
import { PageLayout } from '@/components/layout/PageLayout/PageLayout';
import { Faq } from '@/components/ui/Faq/Faq';
import { QuestSteps } from '@/components/ui/QuestSteps/QuestSteps';
import { Section } from '@/components/ui/Section/Section';
import { thirdCrisis } from '@/data/games';
import { ADULT_DISCLAIMER, HOME_PAGE, thirdCrisisNavigation } from '@/data/navigation';
import { thirdCrisisFaq, thirdCrisisSteps } from '@/data/thirdCrisisContent';
import { useAgeVerification } from '@/hooks/useAgeVerification';

export function ThirdCrisisPage() {
  const { status, error, verify } = useAgeVerification();
  const verified = status === 'verified';

  return (
    <>
      {!verified && <AgeGate gameTitle={thirdCrisis.title} error={error} denied={status === 'denied'} onSubmit={verify} />}
      <PageLayout brandHref={HOME_PAGE} navLinks={thirdCrisisNavigation} disclaimer={ADULT_DISCLAIMER}>
        {verified && (
          <>
            <Section
              tag="18+"
              title={thirdCrisis.title}
              eyebrow="// área +18"
              subtitle="Tradução PT-BR completa, feita por fãs, para um RPG adulto de ficção científica e fantasia. Todos os personagens do jogo são adultos."
            >
              <GameGrid single>
                <GameCard game={thirdCrisis} />
              </GameGrid>
            </Section>
            <Section id="instalar" tag="01" title="Como vai funcionar">
              <QuestSteps steps={thirdCrisisSteps} />
            </Section>
            <Section id="faq" tag="02" title="FAQ">
              <Faq items={thirdCrisisFaq} />
            </Section>
          </>
        )}
      </PageLayout>
    </>
  );
}
