import type { Step } from '@/models/content';
import styles from './QuestSteps.module.css';

export function QuestSteps({ steps }: { steps: Step[] }) {
  return (
    <ol className={styles.steps}>
      {steps.map((step) => (
        <li key={step.title} className={styles.step}>
          <h3 className={styles.title}>{step.title}</h3>
          <p className={styles.description}>{step.description}</p>
        </li>
      ))}
    </ol>
  );
}
