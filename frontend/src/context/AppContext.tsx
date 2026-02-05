/**
 * App Context / Contexto de Aplicación
 *
 * EN: Global application state context using React Context API.
 * ES: Contexto de estado global de la aplicación usando React Context API.
 */
import { createContext, Dispatch } from 'react';
import { FileInfo } from '../utils/fileUtils';
import { FileError, StatusResponse } from '../services/statusService';
import { AppStatusType } from '../config/constants';

/**
 * Process Results Interface / Interfaz de Resultados de Proceso
 *
 * EN: Structure containing the results of a processing job.
 * ES: Estructura que contiene los resultados de un trabajo de procesamiento.
 */
export interface ProcessResults {
  totalFiles: number;
  processedFiles: number;
  totalRecords: number;
  totalAmount: number;
  downloadUrl: string;
  completedAt: string;
}

/**
 * App State Interface / Interfaz de Estado de Aplicación
 *
 * EN: Complete state structure for the application.
 * ES: Estructura de estado completa para la aplicación.
 */
export interface AppState {
  /** EN: Current application status | ES: Estado actual de la aplicación */
  status: AppStatusType;
  /** EN: Current job identifier | ES: Identificador del trabajo actual */
  jobId: string | null;
  /** EN: Files being processed | ES: Archivos siendo procesados */
  files: FileInfo[];
  /** EN: Processing results | ES: Resultados del procesamiento */
  results: ProcessResults | null;
  /** EN: Errors encountered | ES: Errores encontrados */
  errors: FileError[];
  /** EN: Last status response | ES: Última respuesta de estado */
  lastStatus: StatusResponse | null;
}

/**
 * App Action Types / Tipos de Acciones de Aplicación
 *
 * EN: All possible actions for the application reducer.
 * ES: Todas las acciones posibles para el reducer de la aplicación.
 */
export type AppAction =
  | { type: 'SET_STATUS'; payload: AppStatusType }
  | { type: 'SET_JOB_ID'; payload: string | null }
  | { type: 'ADD_FILES'; payload: FileInfo[] }
  | { type: 'REMOVE_FILE'; payload: string }
  | { type: 'UPDATE_FILE'; payload: { id: string; updates: Partial<FileInfo> } }
  | { type: 'CLEAR_FILES' }
  | { type: 'SET_RESULTS'; payload: ProcessResults | null }
  | { type: 'ADD_ERROR'; payload: FileError }
  | { type: 'CLEAR_ERRORS' }
  | { type: 'SET_LAST_STATUS'; payload: StatusResponse | null }
  | { type: 'RESET' };

/**
 * App Context Value Interface / Interfaz de Valor del Contexto
 *
 * EN: Value provided by the AppContext.
 * ES: Valor proporcionado por el AppContext.
 */
export interface AppContextValue {
  state: AppState;
  dispatch: Dispatch<AppAction>;
}

/**
 * Initial State / Estado Inicial
 *
 * EN: Default initial state for the application.
 * ES: Estado inicial por defecto para la aplicación.
 */
export const initialState: AppState = {
  status: 'idle',
  jobId: null,
  files: [],
  results: null,
  errors: [],
  lastStatus: null,
};

/**
 * App Context / Contexto de Aplicación
 *
 * EN: React context for global application state.
 * ES: Contexto de React para estado global de la aplicación.
 */
export const AppContext = createContext<AppContextValue | null>(null);

AppContext.displayName = 'AppContext';

/**
 * App Reducer / Reducer de Aplicación
 *
 * EN: Reducer function for managing application state transitions.
 * ES: Función reducer para manejar transiciones de estado de la aplicación.
 *
 * @param state - Current state / Estado actual
 * @param action - Action to apply / Acción a aplicar
 * @returns New state / Nuevo estado
 */
export function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_STATUS':
      return {
        ...state,
        status: action.payload,
      };

    case 'SET_JOB_ID':
      return {
        ...state,
        jobId: action.payload,
      };

    case 'ADD_FILES':
      return {
        ...state,
        files: [...state.files, ...action.payload],
      };

    case 'REMOVE_FILE':
      return {
        ...state,
        files: state.files.filter((f) => f.id !== action.payload),
      };

    case 'UPDATE_FILE':
      return {
        ...state,
        files: state.files.map((f) =>
          f.id === action.payload.id
            ? { ...f, ...action.payload.updates }
            : f
        ),
      };

    case 'CLEAR_FILES':
      return {
        ...state,
        files: [],
      };

    case 'SET_RESULTS':
      return {
        ...state,
        results: action.payload,
      };

    case 'ADD_ERROR':
      return {
        ...state,
        errors: [...state.errors, action.payload],
      };

    case 'CLEAR_ERRORS':
      return {
        ...state,
        errors: [],
      };

    case 'SET_LAST_STATUS':
      return {
        ...state,
        lastStatus: action.payload,
      };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

export default AppContext;
