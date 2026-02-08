/**
 * ColumnConfigurator Component Tests
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import {
  ColumnConfigurator,
  PURCHASE_COLUMNS,
  PROFILE_BASICO,
  PROFILE_COMPLETO,
  PROFILE_CONTADOR,
} from '../../../src/components/purchases/ColumnConfigurator';

describe('ColumnConfigurator', () => {
  const defaultProps = {
    columns: PURCHASE_COLUMNS,
    selectedColumns: [...PROFILE_COMPLETO],
    onColumnsChange: vi.fn(),
  };

  it('renders all 5 categories', () => {
    render(<ColumnConfigurator {...defaultProps} />);
    expect(screen.getByText('Identificación')).toBeInTheDocument();
    expect(screen.getByText('Proveedor')).toBeInTheDocument();
    expect(screen.getByText('Receptor')).toBeInTheDocument();
    expect(screen.getByText('Montos')).toBeInTheDocument();
    expect(screen.getByText('Pago y Metadatos')).toBeInTheDocument();
  });

  it('renders profile buttons', () => {
    render(<ColumnConfigurator {...defaultProps} />);
    expect(screen.getByText('Básico')).toBeInTheDocument();
    expect(screen.getByText('Completo')).toBeInTheDocument();
    expect(screen.getByText('Contador')).toBeInTheDocument();
    expect(screen.getByText('Personalizar')).toBeInTheDocument();
  });

  it('selects 10 columns when Básico profile is clicked', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Básico'));
    expect(handleChange).toHaveBeenCalledWith(expect.any(Array));
    const calledWith = handleChange.mock.calls[0][0] as string[];
    expect(calledWith).toHaveLength(10);
    expect(calledWith).toEqual(expect.arrayContaining(PROFILE_BASICO));
  });

  it('selects all 32 columns when Completo profile is clicked', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        selectedColumns={[...PROFILE_BASICO]}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Completo'));
    expect(handleChange).toHaveBeenCalledWith(expect.any(Array));
    const calledWith = handleChange.mock.calls[0][0] as string[];
    expect(calledWith).toHaveLength(32);
  });

  it('selects 15 columns when Contador profile is clicked', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Contador'));
    expect(handleChange).toHaveBeenCalledWith(expect.any(Array));
    const calledWith = handleChange.mock.calls[0][0] as string[];
    expect(calledWith).toHaveLength(15);
    expect(calledWith).toEqual(expect.arrayContaining(PROFILE_CONTADOR));
  });

  it('toggles a checkbox when clicked', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        selectedColumns={['control_number', 'document_type']}
        onColumnsChange={handleChange}
      />
    );
    // Click 'Número de Control' checkbox to deselect it
    fireEvent.click(screen.getByText('Número de Control'));
    expect(handleChange).toHaveBeenCalledWith(['document_type']);
  });

  it('adds a column when unchecked column is clicked', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        selectedColumns={['control_number']}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Tipo de Documento'));
    expect(handleChange).toHaveBeenCalledWith(['control_number', 'document_type']);
  });

  it('selects all columns with Seleccionar Todo', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        selectedColumns={['control_number']}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Seleccionar Todo'));
    expect(handleChange).toHaveBeenCalledWith(expect.any(Array));
    const calledWith = handleChange.mock.calls[0][0] as string[];
    expect(calledWith).toHaveLength(32);
  });

  it('deselects all columns with Deseleccionar Todo', () => {
    const handleChange = vi.fn();
    render(
      <ColumnConfigurator
        {...defaultProps}
        onColumnsChange={handleChange}
      />
    );
    fireEvent.click(screen.getByText('Deseleccionar Todo'));
    expect(handleChange).toHaveBeenCalledWith([]);
  });

  it('shows column count', () => {
    render(
      <ColumnConfigurator
        {...defaultProps}
        selectedColumns={[...PROFILE_BASICO]}
      />
    );
    expect(screen.getByText('10 de 32 columnas seleccionadas')).toBeInTheDocument();
  });
});
