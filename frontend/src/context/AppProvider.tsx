/**
 * App Provider / Proveedor de Aplicación
 *
 * EN: Provider component that wraps the application with global state.
 * ES: Componente proveedor que envuelve la aplicación con estado global.
 */
import React, { useReducer, useMemo, ReactNode } from 'react';
import { AppContext, appReducer, initialState, AppState } from './AppContext';

/**
 * App Provider Props / Props del Proveedor de Aplicación
 *
 * EN: Props for the AppProvider component.
 * ES: Props para el componente AppProvider.
 */
interface AppProviderProps {
  /** EN: Child components | ES: Componentes hijos */
  children: ReactNode;
  /** EN: Optional initial state override | ES: Sobrescritura opcional del estado inicial */
  initialStateOverride?: Partial<AppState>;
}

/**
 * App Provider Component / Componente Proveedor de Aplicación
 *
 * EN: Provides global application state to all child components.
 *     Uses useReducer for predictable state management.
 * ES: Proporciona estado global de aplicación a todos los componentes hijos.
 *     Usa useReducer para manejo de estado predecible.
 *
 * @param props - Component props / Props del componente
 * @returns Provider component / Componente proveedor
 *
 * @example
 * // Basic usage
 * <AppProvider>
 *   <App />
 * </AppProvider>
 *
 * // With initial state override (useful for testing)
 * <AppProvider initialStateOverride={{ jobId: 'test-job' }}>
 *   <App />
 * </AppProvider>
 */
export function AppProvider({
  children,
  initialStateOverride,
}: AppProviderProps): React.JSX.Element {
  // EN: Merge initial state with any overrides
  // ES: Combinar estado inicial con cualquier sobrescritura
  const mergedInitialState: AppState = useMemo(
    () => ({
      ...initialState,
      ...initialStateOverride,
    }),
    [initialStateOverride]
  );

  const [state, dispatch] = useReducer(appReducer, mergedInitialState);

  // EN: Memoize context value to prevent unnecessary re-renders
  // ES: Memorizar valor del contexto para prevenir re-renderizados innecesarios
  const contextValue = useMemo(
    () => ({
      state,
      dispatch,
    }),
    [state]
  );

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
}

export default AppProvider;
