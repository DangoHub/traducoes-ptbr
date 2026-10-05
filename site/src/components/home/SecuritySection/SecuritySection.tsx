import { Section } from '@/components/ui/Section/Section';
import { achievements } from '@/data/homeContent';
import { WindowsWarning } from '../WindowsWarning/WindowsWarning';
import styles from './SecuritySection.module.css';

export function SecuritySection() {
  return (
    <Section
      id="seguranca"
      tag="03"
      title="Por que confiar"
      subtitle="Baixar programas da internet exige confiança. Por isso cada etapa aqui pode ser conferida por qualquer pessoa."
    >
      <div className={styles.achievements}>
        {achievements.map((achievement) => (
          <div key={achievement.title} className={styles.achievement}>
            <span className={styles.icon}>{achievement.icon}</span>
            <div>
              <h3>{achievement.title}</h3>
              <p>{achievement.description}</p>
            </div>
          </div>
        ))}
      </div>
      <WindowsWarning />
    </Section>
  );
}
