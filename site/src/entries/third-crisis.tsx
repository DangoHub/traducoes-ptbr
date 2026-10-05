import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThirdCrisisPage } from '@/pages/ThirdCrisisPage/ThirdCrisisPage';
import '@/styles/global.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThirdCrisisPage />
  </StrictMode>
);
