export const REPOSITORY_URL = 'https://github.com/DangoHub/traducoes-ptbr';
export const ISSUES_URL = `${REPOSITORY_URL}/issues`;
export const SUGGEST_GAME_URL = `${ISSUES_URL}/new?title=${encodeURIComponent('Sugestão de jogo: ')}`;
export const IDEAS_URL = `${REPOSITORY_URL}/discussions/new?category=ideas`;
export const VERIFY_GUIDE_URL = `${REPOSITORY_URL}/blob/main/VERIFICAR.md`;
export const GITHUB_CLI_URL = 'https://cli.github.com/';

export function releaseTagUrl(tag: string): string {
  return `${REPOSITORY_URL}/releases/tag/${tag}`;
}

export function releaseAssetUrl(tag: string, fileName: string): string {
  return `${REPOSITORY_URL}/releases/download/${tag}/${fileName}`;
}

export function steamCoverUrl(appId: number): string {
  return `https://cdn.cloudflare.steamstatic.com/steam/apps/${appId}/header.jpg`;
}

export function virusTotalUrl(sha256: string): string {
  return `https://www.virustotal.com/gui/file/${sha256}`;
}
