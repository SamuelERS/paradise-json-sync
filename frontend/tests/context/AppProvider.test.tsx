/**
 * AppProvider Component Tests (Tests del Componente AppProvider)
 *
 * Tests for the AppProvider context component.
 * Tests para el componente de contexto AppProvider.
 */
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useContext } from 'react';
import { AppProvider } from '../../src/context/AppProvider';
import { AppContext, AppState, initialState } from '../../src/context/AppContext';

// Test component to access context
function TestConsumer() {
  const context = useContext(AppContext);
  if (!context) {
    return <div data-testid="no-context">No context</div>;
  }
  return (
    <div>
      <div data-testid="status">{context.state.status}</div>
      <div data-testid="job-id">{context.state.jobId ?? 'null'}</div>
      <div data-testid="files-count">{context.state.files.length}</div>
      <button
        data-testid="set-status"
        onClick={() => context.dispatch({ type: 'SET_STATUS', payload: 'processing' })}
      >
        Set Processing
      </button>
      <button
        data-testid="set-job"
        onClick={() => context.dispatch({ type: 'SET_JOB_ID', payload: 'test-job-123' })}
      >
        Set Job
      </button>
      <button
        data-testid="reset"
        onClick={() => context.dispatch({ type: 'RESET' })}
      >
        Reset
      </button>
    </div>
  );
}

describe('AppProvider', () => {
  describe('Context Provision', () => {
    it('provides context to children', () => {
      render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toBeInTheDocument();
    });

    it('provides initial state', () => {
      render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('idle');
      expect(screen.getByTestId('job-id')).toHaveTextContent('null');
      expect(screen.getByTestId('files-count')).toHaveTextContent('0');
    });

    it('provides dispatch function', () => {
      render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('set-status')).toBeInTheDocument();
    });
  });

  describe('State Override', () => {
    it('accepts initial state override', () => {
      const override: Partial<AppState> = {
        status: 'processing',
        jobId: 'override-job',
      };

      render(
        <AppProvider initialStateOverride={override}>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('processing');
      expect(screen.getByTestId('job-id')).toHaveTextContent('override-job');
    });

    it('merges override with initial state', () => {
      const override: Partial<AppState> = {
        jobId: 'partial-override',
      };

      render(
        <AppProvider initialStateOverride={override}>
          <TestConsumer />
        </AppProvider>
      );

      // Override applied
      expect(screen.getByTestId('job-id')).toHaveTextContent('partial-override');
      // Default preserved
      expect(screen.getByTestId('status')).toHaveTextContent('idle');
    });

    it('override does not affect default files array', () => {
      const override: Partial<AppState> = {
        status: 'completed',
      };

      render(
        <AppProvider initialStateOverride={override}>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('files-count')).toHaveTextContent('0');
    });
  });

  describe('Dispatch Actions', () => {
    it('SET_STATUS updates status', async () => {
      render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('idle');

      await act(async () => {
        screen.getByTestId('set-status').click();
      });

      expect(screen.getByTestId('status')).toHaveTextContent('processing');
    });

    it('SET_JOB_ID updates jobId', async () => {
      render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('job-id')).toHaveTextContent('null');

      await act(async () => {
        screen.getByTestId('set-job').click();
      });

      expect(screen.getByTestId('job-id')).toHaveTextContent('test-job-123');
    });

    it('RESET returns to initial state', async () => {
      const override: Partial<AppState> = {
        status: 'completed',
        jobId: 'some-job',
      };

      render(
        <AppProvider initialStateOverride={override}>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('completed');

      await act(async () => {
        screen.getByTestId('reset').click();
      });

      expect(screen.getByTestId('status')).toHaveTextContent('idle');
      expect(screen.getByTestId('job-id')).toHaveTextContent('null');
    });
  });

  describe('Rendering', () => {
    it('renders children', () => {
      render(
        <AppProvider>
          <div data-testid="child">Child content</div>
        </AppProvider>
      );

      expect(screen.getByTestId('child')).toBeInTheDocument();
      expect(screen.getByText('Child content')).toBeInTheDocument();
    });

    it('renders multiple children', () => {
      render(
        <AppProvider>
          <div data-testid="child-1">First</div>
          <div data-testid="child-2">Second</div>
        </AppProvider>
      );

      expect(screen.getByTestId('child-1')).toBeInTheDocument();
      expect(screen.getByTestId('child-2')).toBeInTheDocument();
    });

    it('renders nested components', () => {
      render(
        <AppProvider>
          <div>
            <div>
              <TestConsumer />
            </div>
          </div>
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toBeInTheDocument();
    });
  });

  describe('Context Value Stability', () => {
    it('state is accessible after multiple renders', async () => {
      const { rerender } = render(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('idle');

      rerender(
        <AppProvider>
          <TestConsumer />
        </AppProvider>
      );

      expect(screen.getByTestId('status')).toHaveTextContent('idle');
    });
  });
});

describe('AppContext without Provider', () => {
  it('returns null when used outside provider', () => {
    render(<TestConsumer />);

    expect(screen.getByTestId('no-context')).toBeInTheDocument();
  });
});

describe('initialState', () => {
  it('has correct default values', () => {
    expect(initialState.status).toBe('idle');
    expect(initialState.jobId).toBeNull();
    expect(initialState.files).toEqual([]);
    expect(initialState.results).toBeNull();
    expect(initialState.errors).toEqual([]);
    expect(initialState.lastStatus).toBeNull();
  });
});
