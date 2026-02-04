/**
 * Upload Flow Integration Tests / Tests de Integración de Flujo de Carga
 *
 * Tests for the file upload flow using MSW.
 * Tests para el flujo de carga de archivos usando MSW.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { server, useHandlers } from '../setup';
import { uploadErrorHandler } from '../handlers';
import {
  uploadInvalidTypeError,
  uploadFileTooLargeError,
} from '../mocks/uploadResponse';

// Import components when they are implemented
// Importar componentes cuando estén implementados
// import { HomePage } from '../../../src/pages/Home';
// import { DropzoneUpload } from '../../../src/components/DropzoneUpload';

// MSW Setup / Configuración de MSW
beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Upload Flow / Flujo de Carga', () => {
  // Helper to create a mock file
  // Helper para crear un archivo mock
  const createMockFile = (
    name: string,
    type: string,
    content: string = '{}'
  ): File => {
    return new File([content], name, { type });
  };

  describe('Render and Basic Interaction / Renderizado e Interacción Básica', () => {
    it.skip('renders HomePage with dropzone / renderiza HomePage con dropzone', () => {
      // TODO: Uncomment when component is implemented
      // TODO: Descomentar cuando el componente esté implementado
      // render(<HomePage />);
      //
      // expect(screen.getByTestId('dropzone')).toBeInTheDocument();
      // expect(screen.getByTestId('upload-section')).toBeInTheDocument();
    });

    it.skip('shows empty state when no files are uploaded / muestra estado vacío cuando no hay archivos', () => {
      // render(<HomePage />);
      //
      // expect(screen.queryByTestId('file-item')).not.toBeInTheDocument();
      // expect(screen.getByTestId('process-button')).toBeDisabled();
    });
  });

  describe('File Upload / Carga de Archivos', () => {
    it.skip('uploads a JSON file and shows it in the list / sube archivo JSON y lo muestra en la lista', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      const file = createMockFile(
        'invoice.json',
        'application/json',
        JSON.stringify({ factura: { numero: 'FAC-001' } })
      );

      // Get the file input (usually hidden inside dropzone)
      // Obtener el input de archivo (usualmente oculto dentro del dropzone)
      // const input = screen.getByTestId('file-input');
      // await user.upload(input, file);

      // await waitFor(() => {
      //   expect(screen.getByText('invoice.json')).toBeInTheDocument();
      // });
      //
      // expect(screen.getByTestId('file-item')).toBeInTheDocument();
    });

    it.skip('uploads multiple files / sube múltiples archivos', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      const files = [
        createMockFile('invoice1.json', 'application/json'),
        createMockFile('invoice2.json', 'application/json'),
      ];

      // const input = screen.getByTestId('file-input');
      // await user.upload(input, files);

      // await waitFor(() => {
      //   expect(screen.getByText('invoice1.json')).toBeInTheDocument();
      //   expect(screen.getByText('invoice2.json')).toBeInTheDocument();
      // });
      //
      // expect(screen.getAllByTestId('file-item')).toHaveLength(2);
    });

    it.skip('enables process button after file upload / habilita botón procesar después de cargar archivo', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      const file = createMockFile('invoice.json', 'application/json');

      // const input = screen.getByTestId('file-input');
      // await user.upload(input, file);

      // await waitFor(() => {
      //   expect(screen.getByTestId('process-button')).toBeEnabled();
      // });
    });
  });

  describe('Error Handling / Manejo de Errores', () => {
    it.skip('shows error for invalid file type / muestra error para tipo de archivo inválido', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      const invalidFile = createMockFile('document.txt', 'text/plain', 'plain text');

      // const input = screen.getByTestId('file-input');
      // await user.upload(input, invalidFile);

      // await waitFor(() => {
      //   expect(screen.getByTestId('error-message')).toBeInTheDocument();
      // });
      //
      // expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    });

    it.skip('shows error when upload fails / muestra error cuando la carga falla', async () => {
      // Override handler to simulate error
      // Sobreescribir handler para simular error
      useHandlers(uploadErrorHandler('Server error during upload'));

      const user = userEvent.setup();
      // render(<HomePage />);

      const file = createMockFile('invoice.json', 'application/json');

      // const input = screen.getByTestId('file-input');
      // await user.upload(input, file);

      // await waitFor(() => {
      //   expect(screen.getByTestId('error-message')).toBeInTheDocument();
      // });
    });
  });

  describe('File Management / Gestión de Archivos', () => {
    it.skip('removes file from list when remove button is clicked / elimina archivo de la lista al hacer clic en botón eliminar', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      // First upload a file
      // Primero subir un archivo
      const file = createMockFile('invoice.json', 'application/json');
      // const input = screen.getByTestId('file-input');
      // await user.upload(input, file);

      // await waitFor(() => {
      //   expect(screen.getByText('invoice.json')).toBeInTheDocument();
      // });

      // Click remove button
      // Hacer clic en botón eliminar
      // const removeButton = screen.getByTestId('remove-file');
      // await user.click(removeButton);

      // await waitFor(() => {
      //   expect(screen.queryByText('invoice.json')).not.toBeInTheDocument();
      // });
    });

    it.skip('clears all files / limpia todos los archivos', async () => {
      const user = userEvent.setup();
      // render(<HomePage />);

      const files = [
        createMockFile('invoice1.json', 'application/json'),
        createMockFile('invoice2.json', 'application/json'),
      ];

      // const input = screen.getByTestId('file-input');
      // await user.upload(input, files);

      // await waitFor(() => {
      //   expect(screen.getAllByTestId('file-item')).toHaveLength(2);
      // });

      // Click clear all button
      // Hacer clic en botón limpiar todo
      // const clearButton = screen.getByTestId('clear-all');
      // await user.click(clearButton);

      // await waitFor(() => {
      //   expect(screen.queryByTestId('file-item')).not.toBeInTheDocument();
      // });
    });
  });

  describe('Drag and Drop / Arrastrar y Soltar', () => {
    it.skip('accepts files via drag and drop / acepta archivos vía arrastrar y soltar', async () => {
      // render(<HomePage />);

      const file = createMockFile('invoice.json', 'application/json');
      // const dropzone = screen.getByTestId('dropzone');

      // Simulate drag and drop
      // Simular arrastrar y soltar
      // const dataTransfer = {
      //   files: [file],
      //   items: [{ kind: 'file', type: file.type, getAsFile: () => file }],
      //   types: ['Files'],
      // };

      // fireEvent.drop(dropzone, { dataTransfer });

      // await waitFor(() => {
      //   expect(screen.getByText('invoice.json')).toBeInTheDocument();
      // });
    });

    it.skip('shows visual feedback during drag / muestra feedback visual durante arrastre', async () => {
      // render(<HomePage />);
      // const dropzone = screen.getByTestId('dropzone');

      // fireEvent.dragEnter(dropzone);
      //
      // expect(dropzone).toHaveClass('drag-active');
      //
      // fireEvent.dragLeave(dropzone);
      //
      // expect(dropzone).not.toHaveClass('drag-active');
    });
  });
});

describe('Upload API Integration / Integración de API de Carga', () => {
  it.skip('sends correct request to upload endpoint / envía petición correcta al endpoint de carga', async () => {
    // This test verifies the actual API call
    // Este test verifica la llamada real a la API

    const user = userEvent.setup();
    // render(<HomePage />);

    const file = createMockFile(
      'invoice.json',
      'application/json',
      JSON.stringify({ factura: { numero: 'FAC-001' } })
    );

    // const input = screen.getByTestId('file-input');
    // await user.upload(input, file);

    // MSW will intercept and validate the request
    // MSW interceptará y validará la petición

    // await waitFor(() => {
    //   expect(screen.getByText('invoice.json')).toBeInTheDocument();
    // });
  });

  it.skip('handles upload response correctly / maneja la respuesta de carga correctamente', async () => {
    const user = userEvent.setup();
    // render(<HomePage />);

    const file = createMockFile('invoice.json', 'application/json');

    // const input = screen.getByTestId('file-input');
    // await user.upload(input, file);

    // await waitFor(() => {
    //   // File should show in list with ID from response
    //   // Archivo debe mostrarse en lista con ID de la respuesta
    //   expect(screen.getByTestId('file-item')).toHaveAttribute('data-file-id');
    // });
  });
});
