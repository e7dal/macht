from itertools import chain

from .. import grid
from . import tile

bg_colors = ['red', 'magenta', 'green', 'cyan', 'blue', 'cyan', 'yellow']
fg_colors = ['black', 'black', 'black', 'black', 'white', 'black']


class Grid(grid.Grid):
    vert_div = '||'
    hor_div = '='
    cross_div = 'XX'

    def __init__(self, x=0, y=0, cols=0, rows=0, tile_width=0, tile_height=0,
                 term=None, Tile=tile.Tile):
        super(Grid, self).__init__(rows=rows, cols=cols, Tile=Tile)
        self.x, self.y = x, y
        self.cols, self.rows = cols, rows
        self.tile_width, self.tile_height = tile_width, tile_height
        self.term = term
        self.Tile = Tile

    def draw(self, fg='white', bg=None):
        style = getattr(self.term, fg + ("_on_" + bg if bg else ""))

        for col_idx in range(self.cols - 1):
            hor_offset = ((col_idx + 1) * self.tile_width +
                          col_idx * len(self.vert_div))

            for vert_offset in range(self.height):
                with self.term.location(self.x + hor_offset,
                                        self.y + vert_offset):
                    print(style(self.vert_div))

        for row_idx in range(self.rows - 1):
            vert_offset = (row_idx + 1) * self.tile_height + row_idx
            with self.term.location(self.x, self.y + vert_offset):
                print(style(self.cross_div.join(
                      [self.hor_div * self.tile_width] * (self.cols))))

    def draw_tiles(self):
        for tile in filter(None, chain(*self)):  # all non-empty tiles
            # choose a color, use modulo to support any value of a tile
            # all bg colors have a bright variant doubling the amount of colors
            color_idx = (tile.exponent - 1) % (len(bg_colors) * 2) // 2
            bg = bg_colors[color_idx]
            if tile.exponent % 2 == 0:
                bg = "bright_" + bg

            tile.draw(fg=fg_colors[color_idx], bg=bg)

    def draw_empty_tile(self, row, column):
        x, y = self.tile_coord(row, column)
        for y_offset in range(self.tile_height):
            with self.term.location(x, y + y_offset):
                print(' ' * self.tile_width)

    @property
    def width(self):
        if self.cols > 0:
            div_width = (self.cols - 1) * len(self.vert_div)
            return self.cols * self.tile_width + div_width
        return 0

    @property
    def height(self):
        if self.rows > 0:
            return self.rows * self.tile_height + self.rows - 1
        return 0

    def tile_coord(self, row, column):
        if row >= self.rows or column >= self.cols:
            raise IndexError

        x = self.x + column * self.tile_width + column * len(self.vert_div)
        y = self.y + row * self.tile_height + row

        return x, y

    def spawn_tile(self, *args, **kwargs):
        action = super(Grid, self).spawn_tile(*args, **kwargs)
        row, column = action.new

        self[row][column].x, self[row][column].y = self.tile_coord(row, column)

        return action

    def move(self, *args, **kwargs):
        actions = super(Grid, self).move(*args, **kwargs)

        for action in actions:
            row, col = action.new

            self[row][col].x, self[row][col].y = self.tile_coord(row, col)

        return actions