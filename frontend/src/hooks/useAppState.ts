/**
 * useAppState Hook / Hook useAppState
 *
 * EN: Custom hook for accessing the global application state.
 * ES: Hook personalizado para acceder al estado global de la aplicación.
 */
import { useContext } from 'react';
import { AppContext, AppContextValue } from '../context/AppContext';

/**
 * useAppState Hook / Hook useAppState
 *
 * EN: Hook for accessing the global application state and dispatch function.
 *     Must be used within an AppProvider component.
 * ES: Hook para acceder al estado global de la aplicación y función dispatch.
 *     Debe usarse dentro de un componente AppProvider.
 *
 * @returns Application state and dispatch / Estado de aplicación y dispatch
 * @throws Error if used outside AppProvider / Error si se usa fuera de AppProvider
 *
 * @example
 * const { state, dispatch } = useAppState();
 *
 * // Read state
 * console.log(state.jobId);
 *
 * // Update state
 * dispatch({ type: 'SET_JOB_ID', payload: 'job-123' });
 */
export function useAppState(): AppContextValue {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error(
      'useAppState must be used within an AppProvider. ' +
      'Make sure your component is wrapped in <AppProvider>.'
    );
  }

  return context;
}

export default useAppState;
