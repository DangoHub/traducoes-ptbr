import { Button } from '@/components/ui/Button/Button';
import { publishedGames } from '@/data/games';
import { GITHUB_CLI_URL, IDEAS_URL, VERIFY_GUIDE_URL } from '@/utils/links';
import { SmartScreenMock } from '../SmartScreenMock/SmartScreenMock';
import styles from './WindowsWarning.module.css';

const EXAMPLE_ZIP = publishedGames[0].release?.windowsUrl.split('/').pop() ?? 'arquivo.zip';

export function WindowsWarning() {
  return (
    <div className={styles.box}>
      <div className={styles.intro}>
        <span className={styles.heart} aria-hidden="true">
          ♥
        </span>
        <div>
          <h3>"O Windows protegeu o computador"? Calma, a gente explica!</h3>
          <p>
            Quando você abre a tradução, o Windows pode mostrar um aviso de <b>"editor desconhecido"</b>. Isso acontece porque o programa
            não tem uma <b>assinatura digital</b>, um certificado que a Microsoft reconhece e que pode passar de <b>R$ 1.000 por ano</b>.
            Para um desenvolvedor sozinho, que faz tudo de graça, esse custo ainda não cabe no bolso. 🥲
          </p>
          <p>
            Para compensar, cada arquivo é analisado no <b>VirusTotal</b>, que passa ele por mais de 60 antivírus ao mesmo tempo, e todo o
            código fica aberto no GitHub para quem quiser conferir.
          </p>
        </div>
      </div>

      <div className={styles.steps}>
        <div className={styles.step}>
          <span className={styles.number}>1</span>
          <h4>Confira no VirusTotal</h4>
          <p>
            No card do jogo, clique no botão azul <b>🛡️ VirusTotal</b>. Você vai ver a lista de antivírus e quantos acharam algum problema.
            O nosso está em <b>0</b>.
          </p>
        </div>
        <div className={styles.step}>
          <span className={styles.number}>2</span>
          <h4>Abra a tradução</h4>
          <p>
            Se aparecer o aviso azul do Windows, clique em <b>Mais informações</b> e depois em <b>Executar assim mesmo</b>.
          </p>
        </div>
        <SmartScreenMock />
      </div>

      <p className={styles.dream}>
        🔏 O sonho é ter o certificado com o nome <b>DangoHub</b> e acabar com esse aviso de vez. Cada <a href="#apoie">doação</a> deixa
        isso mais perto!
      </p>

      <div className={styles.ideas}>
        <p>
          <b>Tem uma ideia para deixar isso mais seguro ou mais simples?</b> Conta pra gente!
        </p>
        <Button href={IDEAS_URL} external>
          💡 Enviar sugestão no GitHub
        </Button>
      </div>

      <details className={styles.advanced}>
        <summary>Para quem entende de tecnologia: verificação avançada</summary>
        <p>Compare o SHA-256 do arquivo com o publicado nas notas da versão (PowerShell):</p>
        <pre>
          <code>Get-FileHash .\{EXAMPLE_ZIP} -Algorithm SHA256</code>
        </pre>
        <p>
          Confirme que o arquivo foi gerado pelo GitHub Actions a partir deste repositório (precisa do{' '}
          <a href={GITHUB_CLI_URL} target="_blank" rel="noopener noreferrer">
            GitHub CLI
          </a>
          ):
        </p>
        <pre>
          <code>gh attestation verify .\{EXAMPLE_ZIP} --repo DangoHub/traducoes-ptbr</code>
        </pre>
        <p>
          Detalhes em{' '}
          <a href={VERIFY_GUIDE_URL} target="_blank" rel="noopener noreferrer">
            VERIFICAR.md
          </a>
          .
        </p>
      </details>
    </div>
  );
}
