import React, { createContext, useReducer, useContext, ReactNode, useMemo, useEffect } from 'react';
import { URLMapping, Extractor, Notification, DashboardStats } from '../types/models';
import { api } from '../services/api';

interface AppState {
  mappings: URLMapping[];
  extractors: Extractor[];
  notifications: Notification[];
  dashboardStats: DashboardStats | null;
  loading: {
    mappings: boolean;
    extractors: boolean;
    dashboard: boolean;
  };
  error: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: { key: keyof AppState['loading']; value: boolean } }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_MAPPINGS'; payload: URLMapping[] }
  | { type: 'SET_EXTRACTORS'; payload: Extractor[] }
  | { type: 'SET_DASHBOARD_STATS'; payload: DashboardStats }
  | { type: 'ADD_MAPPING'; payload: URLMapping }
  | { type: 'UPDATE_MAPPING'; payload: URLMapping }
  | { type: 'DELETE_MAPPING'; payload: string }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string };

const initialState: AppState = {
  mappings: [],
  extractors: [],
  notifications: [],
  dashboardStats: null,
  loading: {
    mappings: false,
    extractors: false,
    dashboard: false
  },
  error: null
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: {
          ...state.loading,
          [action.payload.key]: action.payload.value
        }
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_MAPPINGS':
      return { ...state, mappings: action.payload };
    case 'SET_EXTRACTORS':
      return { ...state, extractors: action.payload };
    case 'SET_DASHBOARD_STATS':
      return { ...state, dashboardStats: action.payload };
    case 'ADD_MAPPING':
      return { ...state, mappings: [...state.mappings, action.payload] };
    case 'UPDATE_MAPPING':
      return {
        ...state,
        mappings: state.mappings.map(m => 
          m.id === action.payload.id ? action.payload : m
        )
      };
    case 'DELETE_MAPPING':
      return {
        ...state,
        mappings: state.mappings.filter(m => m.id !== action.payload)
      };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications]
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(n => 
          n.id === action.payload ? { ...n, read: true } : n
        )
      };
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  actions: {
    loadMappings: () => Promise<void>;
    loadExtractors: () => Promise<void>;
    loadDashboardStats: () => Promise<void>;
    createMapping: (mapping: Omit<URLMapping, 'id' | 'createdAt' | 'extractionCount' | 'successRate' | 'averageResponseTime'>) => Promise<void>;
    updateMapping: (id: string, updates: Partial<URLMapping>) => Promise<void>;
    deleteMapping: (id: string) => Promise<void>;
    addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
    removeNotification: (id: string) => void;
    markNotificationRead: (id: string) => void;
  };
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setLoading = (key: keyof AppState['loading'], value: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { key, value } });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}`,
      timestamp: new Date(),
      read: false
    };
    dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification });
  };

  const actions: AppContextType['actions'] = useMemo(() => ({
    loadMappings: async () => {
      try {
        setLoading('mappings', true);
        setError(null);
        const mappings = await api.getMappings();
        dispatch({ type: 'SET_MAPPINGS', payload: mappings });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load mappings';
        setError(errorMessage);
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
      } finally {
        setLoading('mappings', false);
      }
    },

    loadExtractors: async () => {
      try {
        setLoading('extractors', true);
        setError(null);
        const extractors = await api.getExtractors();
        dispatch({ type: 'SET_EXTRACTORS', payload: extractors });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load extractors';
        setError(errorMessage);
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
      } finally {
        setLoading('extractors', false);
      }
    },

    loadDashboardStats: async () => {
      try {
        setLoading('dashboard', true);
        setError(null);
        const stats = await api.getDashboardStats();
        dispatch({ type: 'SET_DASHBOARD_STATS', payload: stats });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to load dashboard stats';
        setError(errorMessage);
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
      } finally {
        setLoading('dashboard', false);
      }
    },

    createMapping: async (mapping: Omit<URLMapping, 'id' | 'createdAt' | 'extractionCount' | 'successRate' | 'averageResponseTime'>) => {
      try {
        const newMapping = await api.createMapping(mapping);
        dispatch({ type: 'ADD_MAPPING', payload: newMapping });
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'URL mapping created successfully'
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to create mapping';
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
        throw error;
      }
    },

    updateMapping: async (id: string, updates: Partial<URLMapping>) => {
      try {
        const updatedMapping = await api.updateMapping(id, updates);
        dispatch({ type: 'UPDATE_MAPPING', payload: updatedMapping });
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'URL mapping updated successfully'
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to update mapping';
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
        throw error;
      }
    },

    deleteMapping: async (id: string) => {
      try {
        await api.deleteMapping(id);
        dispatch({ type: 'DELETE_MAPPING', payload: id });
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'URL mapping deleted successfully'
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to delete mapping';
        addNotification({
          type: 'error',
          title: 'Error',
          message: errorMessage
        });
        throw error;
      }
    },

    addNotification,
    removeNotification: (id: string) => {
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
    },
    markNotificationRead: (id: string) => {
      dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id });
    }
  }), [dispatch]);

  // Load initial data
  useEffect(() => {
    actions.loadMappings();
    actions.loadExtractors();
    actions.loadDashboardStats();
  }, [actions]);

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}