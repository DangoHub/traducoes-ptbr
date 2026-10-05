import { Button } from '@/components/ui/Button/Button';
import { donation } from '@/data/donation';
import { useCopyToClipboard } from '@/hooks/useCopyToClipboard';
import styles from './PixCard.module.css';

export function PixCard() {
  const { copied, copy } = useCopyToClipboard();

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.coin} aria-hidden="true">
          ☕
        </span>
        <h3>Café via Pix</h3>
      </div>
      <p>Escaneie com o app do seu banco. Expresso, cappuccino ou um balde inteiro: você escolhe o valor.</p>
      <div className={styles.qrCode}>
        <img src={donation.qrCodeUrl} alt="QR Code Pix para doação" width={220} height={220} />
      </div>
      <p>Ou use o Pix copia e cola:</p>
      <code className={styles.pixCode}>{donation.pixCode}</code>
      <Button onClick={() => copy(donation.pixCode)} className={styles.copyButton}>
        {copied ? '✔ Código copiado!' : '📋 Copiar código Pix'}
      </Button>
      <p className={styles.recipient}>
        Favorecido: <b>{donation.recipient}</b> · {donation.bank}
      </p>
      <Button variant="download" href={donation.paymentUrl} external className={styles.paymentLink}>
        Abrir página de pagamento
      </Button>
      <p className={styles.thanks}>Todo café, de qualquer tamanho, vira tradução. Valeu demais! ☕♥</p>
    </div>
  );
}
