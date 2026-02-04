/**
 * Process Flow Integration Tests / Tests de Integración de Flujo de Procesamiento
 *
 * Tests for the file processing flow using MSW.
 * Tests para el flujo de procesamiento de archivos usando MSW.
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { server, useHandlers } from '../setup';
import { processingInProgressHandler, processingErrorHandler } from '../handlers';
import { http, HttpResponse, delay } from 'msw';
import {
  statusProcessing25,
  statusProcessing50,
  statusProcessing75,
  statusCompleted,
  statusFailed,
} from '../mocks/statusResponse';

// Import components when they are implemented
// Importar componentes cuando estén implementados
// import { HomePage } from '../../../src/pages/Home';

// MSW Setup / Configuración de MSW
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Process Flow / Flujo de Procesamiento', () => {
  // Helper to setup component with uploaded file
  // Helper para configurar componente con archivo subido
  const setupWithUploadedFile = async () => {
    const user = userEvent.setup();
    // render(<HomePage />);

    // const file = new File(['{}'], 'invoice.json', { type: 'application/json' });
    // const input = screen.getByTestId('file-input');
    // await user.upload(input, file);

    // await waitFor(() => {
    //   expect(screen.getByTestId('file-item')).toBeInTheDocument();
    // });

    return user;
  };

  describe('Processing Start / Inicio de Procesamiento', () => {
    it.skip('starts processing when process button is clicked / inicia procesamiento al hacer clic en botón procesar', async () => {
      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('progress-bar')).toBeInTheDocument();
      // });
    });

    it.skip('disables process button while processing / deshabilita botón procesar durante procesamiento', async () => {
      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(processButton).toBeDisabled();
      // });
    });
  });

  describe('Progress Display / Visualización de Progreso', () => {
    it.skip('shows progress bar during processing / muestra barra de progreso durante procesamiento', async () => {
      // Override status handler to return in-progress status
      // Sobreescribir handler de estado para retornar estado en progreso
      useHandlers(processingInProgressHandler('job-001', 50));

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   const progressBar = screen.getByTestId('progress-bar');
      //   expect(progressBar).toBeInTheDocument();
      // });
    });

    it.skip('updates progress percentage / actualiza porcentaje de progreso', async () => {
      // Simulate progress updates
      // Simular actualizaciones de progreso
      let currentProgress = 0;

      useHandlers(
        http.get('/api/v1/status/:jobId', async () => {
          currentProgress = Math.min(currentProgress + 25, 100);
          return HttpResponse.json({
            job_id: 'job-001',
            status: currentProgress === 100 ? 'completed' : 'processing',
            progress: currentProgress,
            message: `Processing... ${currentProgress}%`,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // Wait for progress to increase
      // Esperar a que el progreso aumente
      // await waitFor(() => {
      //   expect(screen.getByTestId('progress-text')).toHaveTextContent(/[0-9]+%/);
      // }, { timeout: 5000 });
    });

    it.skip('progress bar width matches progress value / ancho de barra coincide con valor de progreso', async () => {
      useHandlers(processingInProgressHandler('job-001', 75));

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   const progressFill = screen.getByTestId('progress-fill');
      //   expect(progressFill).toHaveStyle({ width: '75%' });
      // });
    });
  });

  describe('Completion / Completado', () => {
    it.skip('shows success message when processing completes / muestra mensaje de éxito cuando el procesamiento completa', async () => {
      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('success-message')).toBeInTheDocument();
      // }, { timeout: 10000 });
    });

    it.skip('enables download buttons after completion / habilita botones de descarga después de completar', async () => {
      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('download-excel')).toBeEnabled();
      //   expect(screen.getByTestId('download-pdf')).toBeEnabled();
      // }, { timeout: 10000 });
    });

    it.skip('shows completed status / muestra estado completado', async () => {
      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   const statusMessage = screen.getByTestId('status-message');
      //   expect(statusMessage).toHaveTextContent(/complet|success|listo/i);
      // }, { timeout: 10000 });
    });
  });

  describe('Error Handling / Manejo de Errores', () => {
    it.skip('shows error message when processing fails / muestra mensaje de error cuando el procesamiento falla', async () => {
      // Override to simulate error
      // Sobreescribir para simular error
      useHandlers(processingErrorHandler('job-001', 'Failed to process invoice'));

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('error-message')).toBeInTheDocument();
      //   expect(screen.getByText(/failed to process/i)).toBeInTheDocument();
      // });
    });

    it.skip('allows retry after error / permite reintentar después de error', async () => {
      let hasErrored = false;

      useHandlers(
        http.get('/api/v1/status/:jobId', async () => {
          if (!hasErrored) {
            hasErrored = true;
            return HttpResponse.json({
              job_id: 'job-001',
              status: 'failed',
              progress: 0,
              error: 'Processing failed',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            });
          }
          return HttpResponse.json(statusCompleted);
        })
      );

      const user = await setupWithUploadedFile();

      // First attempt fails
      // Primer intento falla
      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('error-message')).toBeInTheDocument();
      // });

      // Retry should be possible
      // Reintento debe ser posible
      // const retryButton = screen.getByTestId('retry-button');
      // await user.click(retryButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('success-message')).toBeInTheDocument();
      // });
    });

    it.skip('shows error list for multiple errors / muestra lista de errores para múltiples errores', async () => {
      useHandlers(
        http.get('/api/v1/status/:jobId', async () => {
          return HttpResponse.json({
            job_id: 'job-001',
            status: 'completed',
            progress: 100,
            errors: [
              { file: 'invoice1.json', error: 'Invalid format' },
              { file: 'invoice2.json', error: 'Missing required field' },
            ],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   const errorItems = screen.getAllByTestId('error-item');
      //   expect(errorItems).toHaveLength(2);
      // });
    });
  });

  describe('Status Polling / Polling de Estado', () => {
    it.skip('polls status endpoint while processing / consulta endpoint de estado mientras procesa', async () => {
      let pollCount = 0;

      useHandlers(
        http.get('/api/v1/status/:jobId', async () => {
          pollCount++;
          const progress = Math.min(pollCount * 20, 100);
          return HttpResponse.json({
            job_id: 'job-001',
            status: progress === 100 ? 'completed' : 'processing',
            progress,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          });
        })
      );

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('success-message')).toBeInTheDocument();
      // }, { timeout: 10000 });

      // Should have polled multiple times
      // Debe haber consultado múltiples veces
      // expect(pollCount).toBeGreaterThan(1);
    });

    it.skip('stops polling after completion / detiene polling después de completar', async () => {
      let pollCount = 0;

      useHandlers(
        http.get('/api/v1/status/:jobId', async () => {
          pollCount++;
          return HttpResponse.json(statusCompleted);
        })
      );

      const user = await setupWithUploadedFile();

      // const processButton = screen.getByTestId('process-button');
      // await user.click(processButton);

      // await waitFor(() => {
      //   expect(screen.getByTestId('success-message')).toBeInTheDocument();
      // });

      // Wait a bit more to verify no additional polls
      // Esperar un poco más para verificar que no hay polls adicionales
      // const finalPollCount = pollCount;
      // await new Promise(resolve => setTimeout(resolve, 2000));
      // expect(pollCount).toBe(finalPollCount);
    });
  });
});

describe('Process API Integration / Integración de API de Procesamiento', () => {
  it.skip('sends correct request to process endpoint / envía petición correcta al endpoint de proceso', async () => {
    let capturedRequest: { file_ids?: string[] } | null = null;

    useHandlers(
      http.post('/api/v1/process', async ({ request }) => {
        capturedRequest = await request.json() as { file_ids?: string[] };
        return HttpResponse.json({
          job_id: 'job-001',
          status: 'processing',
          file_ids: capturedRequest?.file_ids || [],
          created_at: new Date().toISOString(),
        });
      })
    );

    // const user = userEvent.setup();
    // render(<HomePage />);

    // Upload and process
    // Subir y procesar
    // ... setup code ...

    // await waitFor(() => {
    //   expect(capturedRequest).not.toBeNull();
    //   expect(capturedRequest?.file_ids).toBeDefined();
    //   expect(capturedRequest?.file_ids?.length).toBeGreaterThan(0);
    // });
  });

  it.skip('includes processing options in request / incluye opciones de procesamiento en la petición', async () => {
    let capturedRequest: { options?: Record<string, unknown> } | null = null;

    useHandlers(
      http.post('/api/v1/process', async ({ request }) => {
        capturedRequest = await request.json() as { options?: Record<string, unknown> };
        return HttpResponse.json({
          job_id: 'job-001',
          status: 'processing',
          created_at: new Date().toISOString(),
        });
      })
    );

    // Test with options enabled in UI
    // Probar con opciones habilitadas en UI
    // ... setup code ...

    // await waitFor(() => {
    //   expect(capturedRequest?.options).toBeDefined();
    // });
  });
});
