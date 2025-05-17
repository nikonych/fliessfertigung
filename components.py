import flet as ft
import pandas as pd

def format_number(nr, digits=3):
    if pd.isna(nr):
        return '0' * digits
    return f"{int(nr):0{digits}d}"

def create_data_table(df, column_names, format_columns=None):
    if format_columns is None:
        format_columns = {}

    columns = [ft.DataColumn(ft.Text(col, weight=ft.FontWeight.BOLD)) for col in column_names]
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in column_names:
            value = row[col]
            if col in format_columns:
                value = format_columns[col](value)
            cells.append(ft.DataCell(ft.Text(str(value))))
        rows.append(ft.DataRow(cells=cells))

    return ft.DataTable(
        columns=columns,
        rows=rows,
        border=ft.border.all(1, ft.Colors.GREY_400),
        heading_row_color=ft.Colors.GREY_200,
        heading_row_height=40,
        data_row_min_height=40,
        column_spacing=10,
    )