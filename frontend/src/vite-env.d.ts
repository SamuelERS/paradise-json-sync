/// <reference types="vite/client" />

/**
 * Vite Environment Types / Tipos de Entorno de Vite
 *
 * EN: Type definitions for Vite environment variables.
 * ES: Definiciones de tipos para variables de entorno de Vite.
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
