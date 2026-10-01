/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly GROCERY_AI_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
