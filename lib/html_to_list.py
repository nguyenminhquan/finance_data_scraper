from bs4 import BeautifulSoup

def table_to_list(html):
    grid = []
    html = str(html)
    html = ''.join(line.strip() for line in html.split('\n'))

    soup = BeautifulSoup(html, 'html.parser')
    table_tag = soup.table

    #Adding rows
    for row_tag in table_tag.contents:
        row = []
        for data_tag in row_tag.children:
            col = [data_tag.text.strip(),
                   (int(data_tag.attrs['colspan']) if 'colspan' in data_tag.attrs else 1),
                   (int(data_tag.attrs['rowspan']) if 'rowspan' in data_tag.attrs else 1)]
            row.append(col)
        grid.append(row)

    #Make symmetrical grid
    for row in grid:
        for col in row:
            if col[1] > 1: #colspan > 1
                for _ in range(1, col[1]):
                    row.insert(row.index(col)+1, [None, 1, col[2]])
            if col[2] > 1: #rowspan > 1
                curt_col = row.index(col)
                curt_row = grid.index(row)
                for i in range(1, col[2]):
                    grid[curt_row+i].insert(curt_col, [None, 1, 1])

    #Remove colspan and rowspan values
    for row in grid:
        for i in range(0, len(row)):
            row[i] = row[i][0]
    return grid