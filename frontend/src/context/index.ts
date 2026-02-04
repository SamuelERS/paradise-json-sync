/**
 * Context Module Exports / Exportaciones del Módulo de Contexto
 *
 * EN: Re-exports all context components and types.
 * ES: Re-exporta todos los componentes y tipos de contexto.
 */

// AppContext
export {
  AppContext,
  appReducer,
  initialState,
  default as AppContextDefault,
} from './AppContext';
export type {
  AppState,
  AppAction,
  AppContextValue,
  ProcessResults,
} from './AppContext';

// AppProvider
export { AppProvider, default as AppProviderDefault } from './AppProvider';
