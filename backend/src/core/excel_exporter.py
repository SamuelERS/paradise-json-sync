"""
Excel Exporter / Exportador de Excel
====================================

Export invoice data to Excel format.
Exporta datos de facturas a formato Excel.

This module provides:
Este módulo provee:
- export_to_excel: Export invoices to Excel file
                   Exporta facturas a archivo Excel
- create_summary_sheet: Create summary statistics sheet
                        Crea hoja de resumen estadístico
- format_currency: Format decimal values as currency
                   Formatea valores decimales como moneda
"""

import logging
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from src.models.invoice import Invoice, InvoiceType

logger = logging.getLogger(__name__)


class ExcelExporterError(Exception):
    """
    Custom exception for Excel export errors.
    Excepción personalizada para errores de exportación Excel.
    """

    def __init__(
        self,
        message: str,
        output_path: str | None = None,
        original_error: Exception | None = None,
    ) -> None:
        self.message = message
        self.output_path = output_path
        self.original_error = original_error
        super().__init__(self.message)


class ExcelExporter:
    """
    Excel invoice exporter / Exportador de facturas a Excel.

    Creates Excel workbooks with invoice data, including formatting
    and summary statistics.

    Crea libros de Excel con datos de facturas, incluyendo formato
    y estadísticas de resumen.

    Attributes / Atributos:
        currency_symbol: Symbol for currency formatting
                         Símbolo para formato de moneda
        decimal_places: Number of decimal places for currency
                        Número de decimales para moneda
    """

    # Column headers / Encabezados de columna
    HEADERS = [
        "Document Number / Número",
        "Type / Tipo",
        "Issue Date / Fecha",
        "Customer Name / Cliente",
        "Customer ID / NIT",
        "Subtotal",
        "Tax / Impuesto",
        "Total",
        "Source File / Archivo",
    ]

    def __init__(
        self,
        currency_symbol: str = "$",
        decimal_places: int = 2,
    ) -> None:
        """
        Initialize the Excel exporter.
        Inicializa el exportador de Excel.

        Args / Argumentos:
            currency_symbol: Currency symbol to use / Símbolo de moneda a usar
            decimal_places: Decimal places for currency / Decimales para moneda
        """
        self.currency_symbol = currency_symbol
        self.decimal_places = decimal_places
        logger.debug(
            "ExcelExporter initialized with symbol=%s, decimals=%d",
            currency_symbol,
            decimal_places,
        )

    def export_to_excel(
        self,
        invoices: list[Invoice],
        output_path: str,
        include_summary: bool = True,
        include_items: bool = False,
    ) -> str:
        """
        Export invoices to an Excel file.
        Exporta facturas a un archivo Excel.

        Args / Argumentos:
            invoices: List of invoices to export / Lista de facturas a exportar
            output_path: Path for the output Excel file
                         Ruta para el archivo Excel de salida
            include_summary: Whether to include summary sheet
                             Si incluir hoja de resumen
            include_items: Whether to include detailed items sheet
                           Si incluir hoja de ítems detallados

        Returns / Retorna:
            Path to the created Excel file / Ruta al archivo Excel creado

        Raises / Lanza:
            ExcelExporterError: If export fails / Si la exportación falla
        """
        if not invoices:
            raise ExcelExporterError("No invoices provided for export")

        logger.info("Exporting %d invoices to %s", len(invoices), output_path)

        try:
            workbook = Workbook()

            # Create main invoices sheet
            self._create_invoices_sheet(workbook, invoices)

            # Create summary sheet if requested
            if include_summary:
                self.create_summary_sheet(workbook, invoices)

            # Create items detail sheet if requested
            if include_items:
                self._create_items_sheet(workbook, invoices)

            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            workbook.save(str(output_file))

            logger.info("Successfully exported to %s", output_path)
            return str(output_file)

        except ExcelExporterError:
            raise
        except Exception as e:
            raise ExcelExporterError(
                f"Error exporting to Excel: {e}",
                output_path=output_path,
                original_error=e,
            ) from e

    def create_summary_sheet(
        self,
        workbook: Workbook,
        invoices: list[Invoice],
    ) -> None:
        """
        Create a summary statistics sheet in the workbook.
        Crea una hoja de estadísticas de resumen en el libro.

        Args / Argumentos:
            workbook: The workbook to add the sheet to
                      El libro al que agregar la hoja
            invoices: List of invoices for statistics
                      Lista de facturas para estadísticas
        """
        sheet = workbook.create_sheet(title="Summary - Resumen")

        # Calculate statistics
        total_count = len(invoices)
        total_subtotal = sum((inv.subtotal for inv in invoices), Decimal(0))
        total_tax = sum((inv.tax for inv in invoices), Decimal(0))
        total_amount = sum((inv.total for inv in invoices), Decimal(0))

        # Count by type
        type_counts = dict.fromkeys(InvoiceType, 0)
        for inv in invoices:
            type_counts[inv.invoice_type] += 1

        # Date range
        dates = [inv.issue_date for inv in invoices]
        min_date = min(dates) if dates else None
        max_date = max(dates) if dates else None

        # Write summary data
        summary_data = [
            ("Summary / Resumen", ""),
            ("", ""),
            ("Total Invoices / Total Facturas", total_count),
            ("", ""),
            ("By Type / Por Tipo:", ""),
            ("  Factura", type_counts[InvoiceType.FACTURA]),
            ("  CCF", type_counts[InvoiceType.CCF]),
            ("  Nota Crédito", type_counts[InvoiceType.NOTA_CREDITO]),
            ("", ""),
            ("Date Range / Rango de Fechas:", ""),
            ("  From / Desde", min_date.isoformat() if min_date else "N/A"),
            ("  To / Hasta", max_date.isoformat() if max_date else "N/A"),
            ("", ""),
            ("Totals / Totales:", ""),
            ("  Subtotal", self.format_currency(total_subtotal)),
            ("  Tax / Impuesto", self.format_currency(total_tax)),
            ("  Grand Total / Total General", self.format_currency(total_amount)),
        ]

        for row_num, (label, value) in enumerate(summary_data, start=1):
            sheet.cell(row=row_num, column=1, value=label)
            sheet.cell(row=row_num, column=2, value=value)

        # Apply styling
        self._style_summary_sheet(sheet)

        logger.debug("Created summary sheet with %d invoices", total_count)

    def format_currency(self, value: Decimal) -> str:
        """
        Format a decimal value as currency.
        Formatea un valor decimal como moneda.

        Args / Argumentos:
            value: Decimal value to format / Valor decimal a formatear

        Returns / Retorna:
            Formatted currency string / String de moneda formateado
        """
        format_str = f"{{symbol}}{{value:,.{self.decimal_places}f}}"
        return format_str.format(symbol=self.currency_symbol, value=float(value))

    def _create_invoices_sheet(
        self,
        workbook: Workbook,
        invoices: list[Invoice],
    ) -> None:
        """
        Create the main invoices data sheet.
        Crea la hoja principal de datos de facturas.
        """
        sheet = workbook.active
        sheet.title = "Invoices - Facturas"

        # Write headers
        for col, header in enumerate(self.HEADERS, start=1):
            cell = sheet.cell(row=1, column=col, value=header)
            self._style_header_cell(cell)

        # Write invoice data
        for row_num, invoice in enumerate(invoices, start=2):
            sheet.cell(row=row_num, column=1, value=invoice.document_number)
            sheet.cell(row=row_num, column=2, value=invoice.invoice_type.value)
            sheet.cell(row=row_num, column=3, value=invoice.issue_date.isoformat())
            sheet.cell(row=row_num, column=4, value=invoice.customer_name)
            sheet.cell(row=row_num, column=5, value=invoice.customer_id or "")
            sheet.cell(row=row_num, column=6, value=float(invoice.subtotal))
            sheet.cell(row=row_num, column=7, value=float(invoice.tax))
            sheet.cell(row=row_num, column=8, value=float(invoice.total))
            sheet.cell(row=row_num, column=9, value=invoice.source_file or "")

            # Apply currency format to numeric cells
            for col in [6, 7, 8]:
                cell = sheet.cell(row=row_num, column=col)
                cell.number_format = f"{self.currency_symbol}#,##0.00"

        # Auto-adjust column widths
        self._auto_adjust_columns(sheet)

        logger.debug("Created invoices sheet with %d rows", len(invoices))

    def _create_items_sheet(
        self,
        workbook: Workbook,
        invoices: list[Invoice],
    ) -> None:
        """
        Create a detailed items sheet.
        Crea una hoja de ítems detallados.
        """
        sheet = workbook.create_sheet(title="Items - Items")

        item_headers = [
            "Invoice / Factura",
            "Item # / Ítem #",
            "Description / Descripción",
            "Quantity / Cantidad",
            "Unit Price / Precio Unit.",
            "Total",
        ]

        # Write headers
        for col, header in enumerate(item_headers, start=1):
            cell = sheet.cell(row=1, column=col, value=header)
            self._style_header_cell(cell)

        # Write item data
        row_num = 2
        for invoice in invoices:
            for item_num, item in enumerate(invoice.items, start=1):
                sheet.cell(row=row_num, column=1, value=invoice.document_number)
                sheet.cell(row=row_num, column=2, value=item_num)
                sheet.cell(row=row_num, column=3, value=item.description)
                sheet.cell(row=row_num, column=4, value=float(item.quantity))
                sheet.cell(row=row_num, column=5, value=float(item.unit_price))
                sheet.cell(row=row_num, column=6, value=float(item.total))

                # Apply currency format
                for col in [5, 6]:
                    cell = sheet.cell(row=row_num, column=col)
                    cell.number_format = f"{self.currency_symbol}#,##0.00"

                row_num += 1

        self._auto_adjust_columns(sheet)

        logger.debug("Created items sheet")

    def _style_header_cell(self, cell) -> None:
        """
        Apply header styling to a cell.
        Aplica estilo de encabezado a una celda.
        """
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="4472C4",
            end_color="4472C4",
            fill_type="solid",
        )
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

    def _style_summary_sheet(self, sheet) -> None:
        """
        Apply styling to the summary sheet.
        Aplica estilo a la hoja de resumen.
        """
        # Title styling
        title_cell = sheet.cell(row=1, column=1)
        title_cell.font = Font(bold=True, size=14)

        # Section headers
        for row in [5, 10, 14]:
            cell = sheet.cell(row=row, column=1)
            cell.font = Font(bold=True)

        # Adjust column widths
        sheet.column_dimensions["A"].width = 35
        sheet.column_dimensions["B"].width = 20

    def _auto_adjust_columns(self, sheet) -> None:
        """
        Auto-adjust column widths based on content.
        Ajusta automáticamente anchos de columna según contenido.
        """
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = get_column_letter(column_cells[0].column)

            for cell in column_cells:
                try:
                    cell_length = len(str(cell.value)) if cell.value else 0
                    max_length = max(max_length, cell_length)
                except Exception:
                    pass

            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
