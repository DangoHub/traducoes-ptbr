import { Highlight } from '@/components/ui/Highlight/Highlight';
import { Section } from '@/components/ui/Section/Section';
import { supportPerks } from '@/data/homeContent';
import { REPOSITORY_URL } from '@/utils/links';
import { PixCard } from '../PixCard/PixCard';
import styles from './SupportSection.module.css';

export function SupportSection() {
  return (
    <Section id="apoie" tag="04" title="Pague um café pro dev">
      <div className={styles.grid}>
        <div className={styles.text}>
          <p className={styles.big}>
            As traduções são e sempre vão ser <Highlight>gratuitas</Highlight>. O café, infelizmente, não. ☕
          </p>
          <p>
            Por trás daquele botão "Instalar tradução" tem um dev abrindo arquivo binário que ninguém documentou, caçando onde o jogo
            esconde cada fala, traduzindo dezenas de milhares de linhas sem matar nenhuma piada nem trocadilho, brigando com o glossário pra
            todo mundo chamar a mesma coisa pelo mesmo nome, montando instalador pra Windows <em>e</em> pra Steam Deck e testando até a fala
            aparecer certinha na tela. E não um <code>(Synonym does not exist)</code> bem no meio da cena.
          </p>
          <p>
            Tudo isso pra você só clicar em um botão e jogar. 😅 Se a tradução te salvou de jogar com o tradutor do celular do lado,
            considere pagar um cafezinho. Qualquer valor vira combustível pro próximo jogo.
          </p>
          <ul className={styles.perks}>
            {supportPerks.map((perk) => (
              <li key={perk}>{perk}</li>
            ))}
          </ul>
          <p className={styles.freeHelp}>
            Sem grana? Relaxa, o dev também sobrevive à base de ⭐. Deixa uma estrela no{' '}
            <a href={REPOSITORY_URL} target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            , compartilha com os amigos e manda os erros de tradução que você achar. Tudo isso ajuda muito.
          </p>
        </div>
        <PixCard />
      </div>
    </Section>
  );
}
