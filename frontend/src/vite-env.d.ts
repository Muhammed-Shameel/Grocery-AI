/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly GROCERY_AI_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
