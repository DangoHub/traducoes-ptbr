import { useCallback, useEffect, useRef, useState } from 'react';

const FEEDBACK_MS = 2000;

/** Copy text to the clipboard; `copied` stays true for a moment so the UI can confirm it. */
export function useCopyToClipboard() {
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => () => clearTimeout(timer.current), []);

  const copy = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      return false;
    }
    setCopied(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setCopied(false), FEEDBACK_MS);
    return true;
  }, []);

  return { copied, copy };
}
