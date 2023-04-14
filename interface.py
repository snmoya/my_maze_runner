from __future__ import annotations
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image
from tkinter import filedialog

from game import *
from Interface_support import AbstractGrid
from constants import *

#__author__ = "Sebastian Moya"

class LevelView(AbstractGrid):
    """ 
        LevelView is a view class that displays the maze tiles and the entities.
        Tiles are drawn as a coloured rectangles at their (row, column) postitions,
        and entities are drawn over the tiles using coloured, annotated ovals at their
        (row, column) positions.
    """
    
    def __init__(self, master: [tk.Tk, tk.Frame], dimensions: tuple[int, int], size: tuple[int, int], **kwargs) -> None:
        """
        Sets up the LevelView with the master frame, dimensions and size.
        
        Parameters:
            master(tk.Frame): is the Frame
            dimensions(tuple<int>): The dimensions of the maze.
            size(tuple<int>): width and height.
        """
        super().__init__(master, dimensions, size, **kwargs)

    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:
        """
        Clears and redraws the entire level (maze and entities).

        Parameters:
            tiles(list[list[Tile]]): The tiles of the maze.
            items(dict[tuple[int,int]]): items on the maze.
            player_pos(tuple<int>): player position(row, col)
                
        """
        self.clear()
        #Tiles
        for row, tile_row in enumerate(tiles):
            for col, tile in enumerate(tile_row):
                bbox = self.get_bbox((row, col))
                tilename = str(tile.get_id())
                self.create_rectangle(*bbox, fill=TILE_COLOURS[tilename])
        #Player
        self.create_oval(self.get_bbox((player_pos[0], player_pos[1])), fill='pink')
        self.annotate_position((player_pos[0], player_pos[1]), PLAYER)

        #Items
        for item in items:
            self.create_oval(self.get_bbox(item), fill=ENTITY_COLOURS[str(items[item])])
            self.annotate_position((item), items[item])

class ImageLevelView(LevelView):
    """
        ImageLevelView is a view class that inheritance from LevelView.
        Instead of entities drawn by rectangles and ovals, are done with images.
    """
    def __init__(self, master: [tk.Tk, tk.Frame], dimensions: tuple[int, int], size: tuple[int, int], **kwargs) -> None:
        """
        Sets up the LevelView with the master frame, dimensions and size.
        
        Parameters:
            master(tk.Frame): is the Frame
            dimensions(tuple<int>): The dimensions of the maze.
            size(tuple<int>): width and height.
        """
        super().__init__(master, dimensions, size, **kwargs)
        


    def draw(self, tiles: list[list[Tile]], items: dict[tuple[int, int], Item], player_pos: tuple[int, int]) -> None:
        """
        Clears and redraws the entire level with images.

        Parameters:
            tiles(list[list[Tile]]): The tiles of the maze.
            items(dict[tuple[int,int]]): items on the maze.
            player_pos(tuple<int>): player position(row, col)
                
        """
        self.clear()
        ent = {'C': COIN, 'M': POTION, 'H': HONEY, 'A': APPLE, 'W': WATER}
        self._images = {}

        #Tiles images
        for row, tile_row in enumerate(tiles):
            for col, tile in enumerate(tile_row):
                tilename = str(tile.get_id())
                midpoint = self.get_midpoint((row, col))
                image = Image.open('images/'+TILE_IMAGES[tilename]).resize(self.get_cell_size())
                photoimg = ImageTk.PhotoImage(image)
                self._images[tilename+str(row)+str(col)] = photoimg
                self.create_image(midpoint[0], midpoint[1], image=photoimg)

        #Items images
        for item in items:
            midpoint = self.get_midpoint(item)
            keyent = items[item].get_id()
            image = Image.open('images/'+ENTITY_IMAGES[ent[keyent]]).resize(self.get_cell_size())
            photoimg = ImageTk.PhotoImage(image)
            self._images[ent[keyent]+str(item)] = photoimg
            self.create_image(midpoint[0], midpoint[1], image=photoimg)

        #Player image
        midpoint = self.get_midpoint((player_pos[0], player_pos[1]))
        image = Image.open('images/player.png').resize(self.get_cell_size())
        photoimg = ImageTk.PhotoImage(image)
        self._images[Player] = photoimg
        self.create_image(midpoint[0], midpoint[1], image=photoimg)
                
class StatsView(AbstractGrid):
    """
        displays the player’s stats (HP, health, thirst), along with
        the number of coins collected.
    """
    def __init__ (self, master: Union[tk.Tk, tk.Frame], width: int, **kwargs) -> None:
        """
        Sets up the StatsView with the master frame and width.
        
        Parameters:
            master(tk.Frame): is the Frame
            width(<int>): the width of the frame.
 
        """
        super().__init__(master, (2, 4), (width, STATS_HEIGHT), **kwargs)
        self.config(bg=THEME_COLOUR)
        

    def draw_stats(self, player_stats: tuple[int, int, int]) -> None:
        """
        Draws the player’s stats (hp, hunger, thirst).

        Parameters:
            player_stats(tuple<int>): player stats
        """
        health, hunger, thirst = player_stats
        self.annotate_position((0, 0), 'HP')
        self.annotate_position((1, 0), health)
        self.annotate_position((0, 1), 'Hunger')
        self.annotate_position((1, 1), hunger)
        self.annotate_position((0, 2), 'Thirst')
        self.annotate_position((1, 2), thirst)

    def draw_coins(self, num_coins: int) -> None:
        """
        Draws the number of coins.

        Parameters:
            num_coins(tuple<int>): number of coins
        """        
        self.annotate_position((0, 3), 'Coins')
        self.annotate_position((1, 3), str(num_coins))


class InventoryView(tk.Frame):
    """
        Displays the items the player has in their inventory
        via tk.Labels, under a title label. Also helps with functions
        so the user can apply items.
    """
    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """
        Sets up the StatsView with the master frame and width.
        
        Parameters:
            master(tk.Frame): is the Frame
            width(<int>): the width of the frame.
 
        """
        super().__init__(master, **kwargs)
        self._master = master
        headergg = tk.Label(self, text='Inventory', font=HEADING_FONT)
        headergg.pack()
        self._callback = None
        
    def set_click_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the function to be called when an item is clicked

        Parameters:
            callback(<str>): a function to be called.
        """
        self._callback = callback
        
    def clear(self) -> None:
        """
            Clears all child widgets from this InventoryView.
        """
        #Clears all the widget but i create the inventory label again.
        for widget in self.winfo_children():
                widget.destroy()
        headergg = tk.Label(self, text='Inventory', font=HEADING_FONT)
        headergg.pack()
        

    def _draw_item(self, name: str, num: int, colour: str) -> None:
        """
        Creates and binds (if a callback exists) a single tk.Label in the InventoryView frame.

        Parameters:
            name(<str>): name of the item
            num(<str>): amount of items
            colour(<str>): colour of the label     
        """
        self._label_name= tk.Label(self, text=f'{name}: {num}', bg=colour, width=30, height=2)
        self._label_name.pack(side=tk.TOP)
        self._label_name.bind('<Button-1>', lambda e, name=name: self._callback(name))
            
    def draw_inventory(self, inventory: Inventory) -> None:
        """
        Draws any non-coin inventory items with their quantities
        and binds the callback for each, if a click callback has been set.

        Parameters:
            inventory(dict): Inventory
        """
        ent = {'Coin': COIN, 'Potion': POTION, 'Honey': HONEY, 'Apple': APPLE, 'Water': WATER}
        if inventory != {}:
           inv = inventory.get_items()
           for element in inv:
               num = len(inv[element])
               colourmatch = ent[element]
               self._draw_item(element, num, colour=ENTITY_COLOURS[colourmatch])

class ControlsFrame(tk.Frame):
    """
    Class that display buttons for restart game, new game and a timer.
    """
    def __init__(self, master: Union[tk.Tk, tk.Frame], **kwargs) -> None:
        """
        Sets up the StatsView with the master frame and width.
        
        Parameters:
            master(tk.Frame): is the Frame
        """
        super().__init__(master, **kwargs)
        self._master = master
        self.draw_restart_game()
        self.draw_new_game()
        self.draw_timer()
        
        self._sec = 0
        self._min = 0
        self.adding_seconds()

    def set_restartg_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the function to be called when an item is clicked

        Parameters:
            callback(<str>): a function to be called.

        """
        self._restartg_button.config(command=callback)

    def set_newg_callback(self, callback: Callable[[str], None]) -> None:
        """
        Sets the function to be called when an item is clicked

        Parameters:
            callback(<str>): a function to be called.

        """ 
        self._newg_button.config(command=callback)

    def draw_restart_game(self):
        """
            Draw the button that restart the game.
        """
        self._restartg_button = tk.Button(self, text='Restart game')
        self._restartg_button.pack(side=tk.LEFT, expand=True)

    def draw_new_game(self):
        """
            Draw the button that create a new game.
        """
        self._newg_button = tk.Button(self, text='New game')
        self._newg_button.pack(side=tk.LEFT, expand=True, command = None)

    def draw_timer(self):
        """
            Draw the frame to set the timer header and the timer numbers.
        """
        #Frame for both elements
        self._timeframe = tk.Frame(self)
        self._timeframe.pack(side=tk.LEFT, expand=True)
        #Time title label
        self._timelabel = tk.Label(self._timeframe, text='Timer', font=TEXT_FONT)
        self._timelabel.pack(side=tk.TOP)
        #Numbers label
        self._timenumbers = tk.Label(self._timeframe, font=TEXT_FONT)
        self._timenumbers.pack(side=tk.TOP)

    def adding_seconds(self):
        """
            A function that add seconds, and every 60, add a minute. 
        """
        self._timenumbers.config(text=f'{self._min}m {self._sec}s')
        self._sec += 1
        #if seconds are 60, add a minut and restart seconds.
        if self._sec // 60 == 1:
            self._min += 1
            self._sec = 0
        self._master.after(1000, self.adding_seconds)
    
class GraphicalInterface(UserInterface):
    """
        This class manages the overall view.
        the title banner and the three major widgets are display.
        And some events handling.
    """
    def __init__(self, master: tk.Tk) -> None:
        """
        Sets up GraphicalInterface with the master.
        
        Parameters:
            master(tk.Tk): master frame
        
        """
        self._master = master
        master.title("MazeRunner")
        
        self._titlelabel = tk.Label(master, text="MazeRunner", bg=THEME_COLOUR, font=BANNER_FONT)
        self._titlelabel.pack(fill=tk.X)
        #i set the self._contro_view in here to get acces for the callback functions.
        if TASK == 2:
            self._control_view = ControlsFrame(self._master)

    def create_interface(self, dimensions: tuple[int, int]) -> None:
        """
            This funciont creates the components (level view, inventory view, and stats view)
            in the master frame for this interface.

            Parameters:
                Dimensions(tuple<int>): dimensions of the maze (row, col)
        """
        self._mid_frame = tk.Frame(self._master)
        self._mid_frame.pack()

        #Handle the view depending of TASK.
        if TASK == 1:
            self._level_view = LevelView(self._mid_frame, dimensions, size=(MAZE_WIDTH, MAZE_HEIGHT))
            self._level_view.pack(side=tk.LEFT)
        elif TASK == 2:
            self._level_view = ImageLevelView(self._mid_frame, dimensions, size=(MAZE_WIDTH, MAZE_HEIGHT))
            self._level_view.pack(side=tk.LEFT)
            self._control_view.pack(side=tk.BOTTOM, expand=True, fill=tk.BOTH)
            
        
        self._inventory_view = InventoryView(self._mid_frame, width=INVENTORY_WIDTH)
        self._inventory_view.pack(side=tk.LEFT, anchor = tk.N)

        
        self._stats_view = StatsView(self._master, (MAZE_WIDTH+INVENTORY_WIDTH))
        self._stats_view.pack(side=tk.TOP)
              
    def clear_all(self) -> None:
        """
            Clears each of the three major components
        """
        self._stats_view.clear()
        self._level_view.clear()
        self._inventory_view.clear()

    def set_maze_dimensions(self, dimensions: tuple[int, int]) -> None:
        """
            This function updates the dimensions
            of the maze in the level to dimensions.

            Parameters:
                Dimensions(tuple<int>): dimensions of the maze (row, col)
        """
        self.set_dimensions(dimensions)

    def bind_keypress(self, command: Callable[[tk.Event], None]) -> None:
        """
            Binds the given command to the general keypress event.

            Parameters:
                callback(<str>): a function to be called.
        """
        self._master.bind('<KeyPress>', command)
        
    def set_inventory_callback(self, callback: Callable[[str], None]) -> None:
        """
            Sets the function to be called when an item is
            clicked in the inventory view to be callback.

            Parameters:
                callback(<str>): a function to be called.            
        """
        self._inventory_view.set_click_callback(callback)

    def set_controlrestart_callback(self, callback: Callable[[str], None]) -> None:
        """
            Sets the function to be called when restart game button is
            clicked in the controlframe to be callback.

            Parameters:
                callback(<str>): a function to be called.            
        """        
        self._control_view.set_restartg_callback(callback)

    def set_controlnewg_callback(self, callback: Callable[[str], None]) -> None:
        """
            Sets the function to be called when new game button is
            clicked in the controlframe to be callback.

            Parameters:
                callback(<str>): a function to be called.            
        """         
        self._control_view.set_newg_callback(callback)

    def draw_inventory(self, inventory: Inventory) -> None:
        """
            Draws any non-coin inventory items with their quantities
            and binds the callback for each, if a click callback has been set.

            Parameters:
                Intenvotry(dic): Inventory
        """
        self.draw_inventory(inventory)
            
    def draw(self, maze: Maze, items: dict[tuple[int, int], Item], player_position: tuple[int, int], inventory: Inventory, player_stats: tuple[int, int, int]) -> None:
        """
            clearing the three major components and redrawing them with the new state.

            Parameters:
                maze: Maze
                items(dic): items and positon
                player_position(tuple<int>): position of the player.
                inventory(dic): Inventory
                player_stats(tuple<int>): the player hp, hunger, thirst.
        """
        self.clear_all()
        self._draw_inventory(inventory)
        self._draw_level(maze, items, player_position)
        self._draw_player_stats(player_stats)

    def _draw_inventory(self, inventory: Inventory) -> None:
        """
            this method draw the non-coin items on the inventory view
            and also draw the coins on the stats view.

            Parameters:
                inventory(dic): Inventory
        """
        num_coins = 0
        if inventory != {}:
            inv = inventory.get_items()
            if 'Coin' in inv:
                num_coins = len(inv['Coin'])

        
        self._inventory_view.draw_inventory(inventory)
        self._stats_view.draw_coins(num_coins)

    def _draw_level(self, maze: Maze, items: dict[tuple[int, int], Item], player_position: tuple[int, int]) -> None:
        """
            This method draw the level.

            Parameters:
                maze: Maze
                items(dic): items and positon
                player_position(tuple<int>): position of the player.      
        """
        tiles = maze.get_tiles()
        self._level_view.draw(tiles, items, player_position)

    def _draw_player_stats(self, player_stats: tuple[int, int, int]) -> None:
        """
            This method draw the player stats.
            
            Parameters:
                player_stats(tuple<int>): the player hp, hunger, thirst.
        """
        self._stats_view.draw_stats(player_stats)
        

class GraphicalMazeRunner(MazeRunner):
    """
        This class handle events generated by the user (keypresses and mouse clicks).
    """

    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """
        Sets up GraphicalMazeRunner with the game_file and the root.
        
        Parameters:
            game_file(<str>): the game to be load.
            master(tk.Tk): master frame
        
        """
        self._root = root
        self._model = Model(game_file)
        self._view = GraphicalInterface(root)
        
    def _handle_keypress(self, e: tk.Event) -> None:
        """
            This method handles a keypress.
            If the key pressed was one of ‘w’, ‘a’, ‘s’, or ‘d’ a move is attempted.

            Parameter:
                e: tk.Event
        """
        moves = {'w': UP, 's': DOWN, 'a': LEFT, 'd': RIGHT}
        
        if e.char in moves:
            self._model.move_player(MOVE_DELTAS.get(moves[e.char]))
            if self._model.did_level_up():
                self._view._level_view.set_dimensions(self._model.get_current_maze().get_dimensions())
                self._redraw()
                
            if self._model.has_won():
                messagebox.showinfo(title='title', message=WIN_MESSAGE)
                self._root.destroy()
            elif self._model.has_lost():
                messagebox.showinfo(title='title', message=LOSS_MESSAGE)
                self._root.destroy()
            else:
                self._redraw()

    def _apply_item(self, item_name: str) -> None:
        """
            Attempts to apply an item with the given name to the player.

            Paremeters:
                item_name(<str>): name of the item to apply.
        """
        item = self._model.get_player().get_inventory().remove_item(item_name)
        if item is not None:
            item.apply(self._model.get_player())
        else:
            messagebox.showinfo(title='title', message=ITEM_UNAVAILABLE_MESSAGE)
        self._redraw()

            
    def play(self) -> None:
        """
            This method cause the gameplay to occur.
        """
        self._view.create_interface(self._model.get_current_maze().get_dimensions())
        self._view.draw(self._model.get_current_maze(), self._model.get_current_items(), self._model.get_player().get_position(), self._model.get_player_inventory().get_items(), self._model.get_player_stats())
        self._view.bind_keypress(self._handle_keypress)
        self._view.set_inventory_callback(self._apply_item)

class UpgradedMazeRunner(GraphicalMazeRunner):
    """
        This class inheretance from GraphicalMazeRunner.
        This class add some features like  a file menu
        and handle the controlframe buttons.
    """
    def __init__(self, game_file: str, root: tk.Tk) -> None:
        """
        Sets up UpgradedMazeRunner with the game_file and the root.
        
        Parameters:
            game_file(<str>): the game to be load.
            master(tk.Tk): master frame
        
        """
        self._root = root
        self._model = Model(game_file)
        self._view = GraphicalInterface(root)
        self.file_menu()
        self._view.set_controlrestart_callback(self._restart_game)
        self._view.set_controlnewg_callback(self._new_game)

    def file_menu(self):
        """
            Set up the file menu. With each respective label. 
        """
        menu = tk.Menu(self._root)
        self._root.config(menu=menu)
        file_menu = tk.Menu(menu)
        
        menu.add_cascade(label="File",menu=file_menu)
        file_menu.add_command(label="Save game", command=self._save_game)
        file_menu.add_command(label="Load game", command=self._new_game)
        file_menu.add_command(label="Restart game", command= self._restart_game)
        file_menu.add_command(label="Quit", command=self._quit_game)

    def _save_game(self):
        """
            This method save all necessary information
            to replicate the current state of the game.
        """
##        filetypes = ('text files', '*.txt')
##        data = {self._model, self._view._control_view._min, self._view._control_view._sec}
##        path = filedialog.askopenfilename(defaultextension=filetypes, initialdir=self.default_path_to_pref, title="saved_game")
##        with open(path_to_pref, 'w') as f:
##                f.write(s)
        pass

    def _load_game(self):
        """
            This method load the game described in that file.
        """
##        with filedialog.askopenfile(mode='r') as file:
##            for line in file:
##            self._redraw()
        pass

    def _restart_game(self):
        """
            Restart the current game, including game timer.
        """
        self._model = Model(GAME_FILE)
        self._view._control_view._min = 0
        self._view._control_view._sec = 0
        self._redraw()

    def _new_game(self):
        """
            This method load a new game prompted by the user.
        """
        self._top = Toplevel(self._root)
        self._top.geometry("200x100")
        self._top.title("New Game")
        self._promp_label = tk.Label(self._top, text=" Please enter a new\n game file path:")
        self._promp_label.pack()
        self._enterbutton = tk.Button(self._top, text="Enter", command=self._enter)
        self._enterbutton.pack(side=tk.BOTTOM)
        self._entry = tk.Entry(self._top)
        self._entry.pack(side=tk.BOTTOM, expand=True, fill=tk.X)

    def _enter(self):
        """
            This function get the entry of the user as a string and if is a proper one
            it load that game path. If is wrong, display a messagebox
        """
        self._entry.get()
        try:
            self._model= Model(self._entry.get())
            self._redraw()
            self._top.destroy()
        except FileNotFoundError:
            messagebox.showinfo(title='title', message='Wrong game path')
        

    def _quit_game(self):
        """
            ask the player wether they are sure they would like to quit.
            If no, do nothing. If yes, quit the game.
        """
        if messagebox.askyesno(titlle=None, message='Are you sure do you like to quit?'):
            self._root.destroy()
            
        

def play_game(root: tk.Tk):
    if TASK == 1:
        controller = GraphicalMazeRunner
    elif TASK == 2:
        controller = UpgradedMazeRunner   
    app = controller(GAME_FILE, root)
    app.play()
    root.mainloop()
    
def main():
    root = tk.Tk()   
    play_game(root)


if __name__ == '__main__':
    main()
