import styles from './SmartScreenMock.module.css';

/** Illustration of the Windows SmartScreen dialog, highlighting where to click. */
export function SmartScreenMock() {
  return (
    <div className={styles.dialog} aria-hidden="true">
      <p className={styles.title}>O Windows protegeu o computador</p>
      <p className={styles.text}>O Windows SmartScreen impediu a inicialização de um aplicativo não reconhecido...</p>
      <p className={styles.link}>
        Mais informações <span className={styles.pointer}>👆</span>
      </p>
      <p className={styles.text}>
        Editor: <b>Editor desconhecido</b>
      </p>
      <div className={styles.buttons}>
        <span className={styles.run}>Executar assim mesmo</span>
        <span>Não executar</span>
      </div>
    </div>
  );
}
