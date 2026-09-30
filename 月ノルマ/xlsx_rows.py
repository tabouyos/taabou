"""予定表の行挿入ヘルパー(openpyxl の insert_rows は結合セル・行高を動かさないため補正する)。"""
from copy import copy

from openpyxl.worksheet.cell_range import CellRange


def insert_row(ws, at, template, values):
    """at 行目に行を挿入し、template 行(挿入前の行番号)の書式をコピーして values(列番号→値)を入れる。
    at を含む/跨ぐ A 列の週結合は1行伸ばす。"""
    heights = {r: ws.row_dimensions[r].height for r in range(1, ws.max_row + 1)}
    merges = [CellRange(str(m)) for m in ws.merged_cells.ranges]
    for m in merges:
        ws.unmerge_cells(str(m))
    ws.insert_rows(at)
    for r, h in heights.items():
        ws.row_dimensions[r + 1 if r >= at else r].height = h
    src = template + 1 if template >= at else template
    ws.row_dimensions[at].height = heights.get(template)
    for c in range(1, ws.max_column + 1):
        s, d = ws.cell(src, c), ws.cell(at, c)
        if s.has_style:
            d._style = copy(s._style)
    for m in merges:
        if m.min_row >= at:
            m.shift(row_shift=1)
        elif m.max_row >= at - 1 and m.min_col == 1 and m.max_col == 1 and m.min_row < at:
            m.expand(down=1)
        ws.merge_cells(m.coord)
    for c, v in values.items():
        ws.cell(at, c).value = v
