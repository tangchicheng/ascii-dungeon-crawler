#Author: Tang Chi Cheng
#Last modified: 23/10/2025
#Version: 1.0

from typing import Tuple, Optional
from abc import ABC, abstractmethod
import random
import json
import time 
from pathlib import Path

#========================================================
#Constants
#========================================================

GAME_JSON   = Path("game.json")
HIGHSCORES_JSON = Path("highscores.json")
CLEAR = "\x1b[2J\x1b[H"   #ANSI code for clearing the screen and returning cursor to top left corner

#========================================================
#Colours
#========================================================

# ANSI reset code
RESET = "\x1b[0m"

# Mapping of game symbols to ANSI colours
SYMBOL_TO_COLOUR = {
    ".": "\x1b[38;5;236m",      # dark grey floor
    "@": "\x1b[38;5;122;1m",    # turquoise player
    "E": "\x1b[38;5;160m",      # red enemy
    "p": "\x1b[38;5;91m",       # purple potion
    "$": "\x1b[38;5;228m",      # yellow gold
    "T": "\x1b[38;5;35m",       # green treasure chest
    "#": "\x1b[38;5;253m",      # light grey wall
    "X": "\x1b[48;5;75m",       # blue exit
}


def symbol_colour(character: str) -> str:
    col = SYMBOL_TO_COLOUR.get(character, '')
    return f"{col}{character}{RESET}"


#========================================================
#Map
#========================================================

MAP_TEXT_LEVEL_1 = [
    "##########################################",
    "#@..E.$..p........#.......$.....#........#",
    "#..#########.....####...........#..$.....#",
    "#..#.....#..........E.....#..#####.......#",
    "#..#..#.......$..#......$.#......#$......#",
    "#..####..####......########......p.......#",
    "#......E.....$..$..$...$....$............#",
    "#$..$.p..#####..$......######........p...#",
    "#..$.......####....###......#.......E....#",
    "#.....T....#.....$.............$.........#",
    "#..........#............#....$...#######.#",
    "#......$.$$#.....p......#..............#.#",
    "#.E.....#.................######.......#.#",
    "#....p..#.....p.......#####......p.....#.#",
    "#.......#.............E...####.........#p#",
    "######################X###################",
]

MAP_TEXT_LEVEL_2 = [
    "######################################################",
    "#.p...............#........$.....#.....E.........ET..#",
    "#..#########.....####....E.......#..$.......##########",
    "#..#.....#.................#..#####.........#...$....#",
    "#..#..#.......$..#......$..#......#$........E..@.....#",
    "#EE####..####......########...........$.....#....p...#",
    "#...........$..$..$...$....$.....p..........#........#",
    "#$..$....#####..$......######.......$.......##########",
    "#..$.......####....###......#......E.....$...........#",
    "#....E.....#.....$................$..........p.......#",
    "#..........#..p.........#....$.......####............#",
    "#.........$#.....p......#........................E...#",
    "#.......#.................######........$............#",
    "#....p..#...X....E....#####......#..................E#",
    "#.......#.................####.....##########........#",
    "#.......####################................#........#",
    "#.E.....#....E.............#........E.......#...######",
    "#.......#.......####........................#........#",
    "#.......#...p.............###....p...................#",
    "######################################################",
]

MAP_TEXT_LEVEL_3 = [
    "##################################################################",
    "#......p..........#........$.....#.....E.#...................p...#",
    "#..#########.....####....E.......#..$....#..p....$.#....##########",
    "#..#.....#...p.............#..#####......#.........#....#...$....#",
    "#..#..#..........#..p...$..#......#$.....#..E......#...........E.#",
    "#...$....####.........................$..########..#.........p...#",
    "#.................$........$....E........#.........#....#........#",
    "#$..$....#####..$......######.......$....#..########..........####",
    "#..$.......####....###......#.........p.......E.....$.....#......#",
    "#....E.....#.....$............p..............$............#......#",
    "#..........#..........p...E........#....$.......###.#.....#......#",
    "#..p......$#.....p........E........#......................#..E...#",
    "#.......#..#............$.E..........######.........$.....#......#",
    "#....p..#........E........E......#####......#.............#.....E#",
    "#.......#.................E..........####.....#.#########........#",
    "#......#############.p.........########.................#........#",
    "#.E.E.#......E........................#......$..........#...######",
    "#.....#...............#....####.........................#.....p..#",
    "#..X..#######.........#........p.....###########....p............#",
    "#.....#...p...........#..............##$.......#..........$......#",
    "#######..........#######################.......#..........p......#",
    "#@..E.........$.....................###$....p.#.................#",
    "#...E...........................$....###.......#.....p...........#",
    "########....p..........p.............###.......##...........$....#",
    "#..p...E...........$.................###.T.....EEE...............#",
    "##################################################################",
]

LEVELS = [MAP_TEXT_LEVEL_1, MAP_TEXT_LEVEL_2, MAP_TEXT_LEVEL_3]


#========================================================
#Game over exception
#========================================================
class GameOver(Exception):
    pass


#========================================================
#Items
#========================================================

class Item(ABC):
    """
    Represents an item
    """
    def __init__(self, name: str = "", symbol: str = "", item_picked_up: bool = False):
        self.name = name 
        self.symbol = symbol
        self.item_picked_up = item_picked_up

    @abstractmethod
    def on_pickup(self, player, log): 
        pass

    @abstractmethod
    def on_use(self, player, log):
        pass


class Gold(Item):
    """
    Represents a gold item
    """
    def __init__(self, amount=1):
        super().__init__("Gold", "$")
        self.amount = amount

    def on_pickup(self, player, log):
        """
        Increases the amount of gold the player has when the player picks up gold

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        player.gold += self.amount
        log.append(f"You pick up {self.amount} gold.")
        self.item_picked_up = True

    def on_use(self, player, log):
        pass


class Potion(Item):
    """
    Represents a potion item
    """
    def __init__(self, amount=1):
        super().__init__("Potion", "p")

    def on_pickup(self, player, log):
        """
        Adds the potion to the player's inventory when it's picked up

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        if len(player.inventory) < Player.MAX_INVENTORY:
            player.inventory.append(self)
            log.append("You pick up a Potion.")
            self.item_picked_up = True
        else:
            log.append("Your inventory is full. Item cannot be picked up.")
            self.item_picked_up = False

    def on_use(self, player, log):
        """
        Increases the player's hp when the potion is used

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        #Nothing happens if the player's hp is full
        if player.hp == player.MAX_HP:
            log.append("Your health is full. Nothing happens.")
        else:
            number = random.randint(3, player.MAX_HP)
            old_hp = player.hp
            player.hp = min(player.hp + number, player.MAX_HP)
            healed = player.hp - old_hp
            log.append(f"Your health increases by {healed}.")



class Weapon(Item):
    """
    Represents weapon data
    """
    def __init__(self, name: str, attack_low: int, attack_high: int, symbol: str = "w"):
        super().__init__(name, symbol)
        self.attack_low = attack_low
        self.attack_high = attack_high

    def get_attack(self) -> int:
        """
        Returns a randomized number for the weapon's attack damage points
        """
        return random.randint(self.attack_low, self.attack_high)

    def on_pickup(self, player, log):
        """
        The weapon is added to the player's inventory when picked up

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        if len(player.inventory) < Player.MAX_INVENTORY:
            player.inventory.append(self)
            #log.append(f"You pick up the {self.name}.")
            self.item_picked_up = True
        else:
            log.append(f"Your inventory is full. The {self.name} cannot be picked up.")
            self.item_picked_up = False

    def on_use(self, player, log):
        """
        Equips the weapon 

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        original_weapon = player.weapon
        player.weapon = self
        log.append(f"You equipped the {self.name}")
        if original_weapon:
            player.inventory.append(original_weapon)
            log.append(f"You place your {original_weapon.name} back in your inventory.")


class Dagger(Weapon):
    """
    Represents dagger (weapon) data
    """
    def __init__(self):
        super().__init__("Dagger", attack_low = 2, attack_high = 3)


class Sword(Weapon):
    """
    Represents sword (weapon) data
    """
    def __init__(self):
        super().__init__("Sword", attack_low = 3, attack_high = 4)


class Axe(Weapon):
    """
    Represents axe (weapon) data
    """
    def __init__(self):
        super().__init__("Axe", attack_low = 5, attack_high = 6)


#========================================================
#Tiles
#========================================================

class Tile(ABC):
    """
    Represents tile data
    """
    walkable: bool = True

    def __init__(self, symbol: str = "", item: Item = None, enemy = None):
        self.symbol = symbol
        self.item = item
        self.enemy = enemy

    @abstractmethod
    def on_enter(self, player, log: list[str]):
        """
        An abstract method that is called when the player moves onto this tile.
        """
        pass

    @abstractmethod
    def on_interact(self, player, log: list[str]):
        """
        An abstract method for when the player interacts with the tile
        """
        log.append("There is nothing to interact with.")



class WallTile(Tile):
    """
    Represents wall tiles
    """
    walkable = False
    def __init__(self):
        super().__init__("#")

    def on_enter(self, player, log: list[str]):
        """
        Prints out a message when the player enters the tile

        Parameters: 
            player (Player): The player
            log (list[str]): The log
        """
        log.append("You bump into a wall.")

    def on_interact(self, player, log):
        """
        Prints out a message when the player interacts with the tile

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        log.append("Nothing happens.")



class FloorTile(Tile):
    """
    Represents floor tiles
    """
    def __init__(self):
        super().__init__(".")

    def on_enter(self, player, log: list[str]):
        """
        Prints a message when the player enters the tile

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        if self.item:
            log.append(f"You find a {self.item.name.lower()}. Press [T] to take.")
        elif self.enemy:
            log.append(f"There is a {self.enemy.name} in your way. Press [F] to fight. Press [R] to run away.")

    def on_interact(self, player, log: list[str]):
        """
        Lets the player pick up the item if there is an item on the tile

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        if self.item:
            self.item.on_pickup(player, log)
            if self.item.item_picked_up == True:
                self.item = None
        else:
            log.append("There's nothing interesting on the floor.")


class TreasureChestTile(Tile):
    """
    Represents treasure chest tile data
    """
    def __init__(self):
        super().__init__("T")
        self.treasure = []
        self.treasure.append(pick_random([Dagger(), Sword(), Axe()]))
        self.treasure.append(Potion())

    def on_enter(self, player, log: list[str]):
        """
        Prints out a message when the player enters the tile

        Parameters: 
            player (Player): The player
            log (list[str]): The log
        """
        if self.treasure:
            log.append("You find a treasure chest. Press [T] to open.")
        else:
            log.append("You find an empty treasure chest.")

    def on_interact(self, player, log: list[str], grid: list[list[Tile]]):
        """
        Lets the player take items if the treasure chest is not empty

        Parameters:
            player (Player): The player
            log (list[str]): The log
            grid (list[list[Tile]])
        """
        if not self.treasure:
            log.append("The chest is empty.")
            return

        log.append("You see the following item(s).")
        while self.treasure:
            message = "Pick an item: [0] Back "
            for i, item in enumerate(self.treasure, start=1):
                message += f"[{i}] {item.name} "
            log.append(message)

            choice = read_int("> ", log, grid, player, 0, len(self.treasure))
            if choice == None:
                log.append("You decide not to take anything.")
                return

            index = choice - 1
            self.treasure[index].on_pickup(player, log)
            if self.treasure[index].item_picked_up:
                log.append(f"You take the {self.treasure[index].name}.")
                self.treasure.pop(index)
            elif not self.treasure[index].item_picked_up:
                break

        if not self.treasure:
            log.append("The chest is now empty.")


class ExitTile(Tile):
    """
    Represents the exit tile.
    It acts as the dungeon exit. Locked until all enemies are defeated.
    """
    walkable = False
    def __init__(self):
        super().__init__("X")

    def on_enter(self, player: "Player", log: list[str], grid: list[list[Tile]]):
        remaining = enemies_remaining(grid)  
        if remaining > 0:
            log.append(f"The exit is sealed by magic. {remaining} enemy(ies) remain.")
        else:
            player.at_exit = True

    def on_interact(self, player, log: list[str]):
        pass


#========================================================
#Characters
#========================================================

class Player:
    """
    Represents the player data
    """
    MAX_INVENTORY = 5
    MAX_HP = 20

    def __init__(self, x: int = 0, y: int = 0, hp: int = MAX_HP, gold: int = 0, weapon: Item = None, inventory: list[Item] = None, at_exit: bool = False):
        """
        Initializes player
        """
        self.x = x
        self.y = y
        self.hp = hp
        self.gold = gold
        self.weapon = weapon
        self.inventory = [] if inventory is None else inventory
        self.at_exit = at_exit


class Enemy:
    """
    Represents the enemy data
    """
    def __init__(self, name: str = "monster", symbol: str = "E", x: int = 0, y: int = 0, hp: int = random.randint(4,10), attack_damage_low: int = 1, attack_damage_high: int = 3, item_drop: list[Item] = None, can_move: bool = True, engage_chance: float = 0.2):
        self.name = name 
        self.symbol = symbol
        self.x = x
        self.y = y 
        self.hp = hp
        self.attack_damage_low = attack_damage_low 
        self.attack_damage_high = attack_damage_high
        self.item_drop = [] if item_drop is None else item_drop
        self.can_move = can_move
        self.engage_chance = engage_chance 

    def get_attack_damage(self) -> int:
        """
        Returns a random number for the enemy's attack damage
        """
        return random.randint(self.attack_damage_low, self.attack_damage_high)

    def attack(self, player, log):
        """
        Lets the enemy attack the player and decrease the player's hp

        Parameters:
            player (Player): The player
            log (list[str]): The log
        """
        attack_damage = self.get_attack_damage()
        player.hp -= attack_damage
        log.append(f"The {self.name} attacks you! You take {attack_damage} damage!")

        if player.hp <= 0:
            raise GameOver()

    def take_damage(self, amount: int, player: Player, log: list[str], grid: list[list[Tile]], current_tile = Tile):
        """
        Decreases the enemy's hp when the player attacks it

        Parameters:
            amount (int): The amount of hp to decrease
            player (Player): The player
            log (list[str]): The log
            grid (list[list[Tile]]): The map grid
            current_tile (Tile): The current tile
        """
        self.hp -= amount

        #Decrease enemy's hp if hp is sbove zero
        if self.hp > 0:
            log.append(f"You attack the {self.name}. It takes {amount} damage (HP: {self.hp}).")
        else:
            log.append(f"The {self.name} takes {amount} damage (HP: 0).")
            log.append(f"The {self.name} is defeated!")
            current_tile.enemy = None

            if enemies_remaining(grid) == 0:
                for row in grid:
                    for tile in row:
                        if isinstance(tile, ExitTile):
                            tile.walkable = True
                            log.append("You hear a distant click. The exit has unlocked.")


            #If the enemy has an item, it will drop it after it's defeated
            if self.item_drop:
                for item in self.item_drop:
                    if len(player.inventory) < player.MAX_INVENTORY:
                        player.inventory.append(item)
                        log.append(f"The {self.name} dropped a {item.name}. You put it in your inventory.")
                    else:
                        log.append(f"The {self.name} dropped a {item.name}, but your inventory is too full.")
                        log.append(f"Would you like to remove an item from your inventory? (y/n)")

                        while True:
                            render(grid, player, log)
                            command = input("> ").strip().lower()
                            if command != "y" and command != "n":
                                log.append("Please enter a valid input")
                            else:
                                break

                        if command == "y":
                            message = "Choose an item: [0] Back "
                            for i, item in enumerate(player.inventory, start=1):
                                message += f"[{i}] {item.name} "
                            log.append(message)
                            render(grid, player, log)

                            choice = read_int("> ", log, grid, player, 0, len(player.inventory)) 
                            if choice == None:
                                log.append("You decide not to remove anything.")
                                current_tile.enemy = None
                                return
                            index = choice - 1
                            log.append(f"You throw a {player.inventory[index].name} away and take the {item.name} instead.")
                            player.inventory.pop(index)
                            player.inventory.append(item)
                        elif command == "n":
                            log.append("You decide not to remove anything.")
            current_tile.enemy = None
                    

class EnemyWithItem(Enemy):
    """
    Represents an enemy that is carrying items
    """
    def __init__(self):
        super().__init__(item_drop = [Potion()])

class EnemyLevelTwo(Enemy):
    """
    Represents a level two enemy
    """
    def __init__(self):
        super().__init__(hp = random.randint(10,20), attack_damage_low = 3, attack_damage_high = 5, engage_chance = 0.4)

class EnemyLevelTwoWithItem(Enemy):
    """
    Represents a level two enemy that is carrying items
    """
    def __init__(self):
        super().__init__(hp = random.randint(10,20), attack_damage_low = 3, attack_damage_high = 5, item_drop = [Potion()], engage_chance = 0.4)

class EnemyLevelThree(Enemy):
    """
    Represents a level three enemy
    """
    def __init__(self):
        super().__init__(hp = random.randint(20,25), attack_damage_low = 5, attack_damage_high = 10, engage_chance = 0.7)

class EnemyLevelThreeWithItem(Enemy):
    """
    Represents a level three enemy that is carrying items
    """
    def __init__(self):
        super().__init__(hp = random.randint(20,25), attack_damage_low = 5, attack_damage_high = 10, item_drop = [Potion()], engage_chance = 0.7)



#========================================================
#Saving & Loading
#========================================================

#Dictionaries

ITEM_TYPES = {
    "Gold": Gold,
    "Potion": Potion,
    "Dagger": Dagger,
    "Sword": Sword,
    "Axe": Axe,
}


ENEMY_TYPES = {
    "Enemy": Enemy,
    "EnemyWithItem": EnemyWithItem,
    "EnemyLevelTwo": EnemyLevelTwo,
    "EnemyLevelTwoWithItem": EnemyLevelTwoWithItem,
    "EnemyLevelThree": EnemyLevelThree,
    "EnemyLevelThreeWithItem": EnemyLevelThreeWithItem,
}


TILE_TYPES = {
    "WallTile": WallTile,
    "FloorTile": FloorTile,
    "TreasureChestTile": TreasureChestTile,
    "ExitTile": ExitTile,
}

#Item serialization
def item_to_dict(item: Item | None) -> dict | None:
    """
    Turns the item (if it exists) into a dictionary and returns it 

    Parameters:
        item (Item | None): The item

    Returns the dictionary or None if there is no item
    """
    if item is None:
        return None
    dictionary = {"type": type(item).__name__}
    if isinstance(item, Gold):
        dictionary["amount"] = item.amount
    elif isinstance(item, Potion):
        pass
    elif isinstance(item, Weapon):
        dictionary.update({"name": item.name, "attack_low": item.attack_low, "attack_high": item.attack_high})
    return dictionary


def item_from_dict(dictionary: dict | None) -> Item | None:
    """
    Turns the item from the dictionary into an Item object

    Parameters:
        dictionary (dict): The dictionary

    Returns the Item object or None if there is no dictionary
    """
    if dictionary is None:
        return None
    
    #Get the item type
    item_type = dictionary["type"]

    if item_type == "Gold":
        return Gold(amount = dictionary.get("amount", 1))
    elif item_type == "Potion":
        return Potion()
    elif item_type in ("Dagger", "Sword", "Axe"):
        return ITEM_TYPES[item_type]() 
    else:
        raise ValueError(f"Unknown item type {item_type}")


#Enemy serialization 
def enemy_to_dict(enemy: Enemy | None) -> dict | None:
    """
    Turns the enemy object data into a dictionary

    Parameters:
        enemy (Enemy): The enemy

    Returns the dictionary or None if the enemy does not exist
    """
    if enemy is None:
        return None
    
    if enemy.item_drop:
        drop_list = []
        for item in enemy.item_drop:
            drop_list.append(item_to_dict(item))
    else:
        drop_list = []
    
    return {
        "type": type(enemy).__name__, #The class name
        "name": enemy.name,
        "symbol": enemy.symbol,
        "x": enemy.x,
        "y": enemy.y,
        "hp": enemy.hp,
        "attack_damage_low": enemy.attack_damage_low,
        "attack_damage_high": enemy.attack_damage_high,
        "can_move": enemy.can_move,
        "engage_chance": enemy.engage_chance,
        "item_drop": drop_list,
    }


def enemy_from_dict(dictionary: dict | None) -> Enemy | None:
    """
    Turns the enemy from the dictionary into an Enemy object

    Parameters:
        dictionary (dict): The dictionary

    Returns the Enemy object or None if there is no dictionary
    """
    if dictionary is None:
        return None
    
    if dictionary.get("item_drop"):
        drop_list = []
        for item in dictionary["item_drop"]:
            drop_list.append(item_from_dict(item))
    else:
        drop_list = []

    enemy_type = ENEMY_TYPES.get(dictionary["type"], Enemy)
    enemy = enemy_type()  #Create an object with the default values first
    enemy.name = dictionary.get("name", enemy.name)
    enemy.symbol = dictionary.get("symbol", enemy.symbol)
    enemy.x = dictionary.get("x", enemy.x)
    enemy.y = dictionary.get("y", enemy.y)
    enemy.hp = dictionary.get("hp", enemy.hp)
    enemy.attack_damage_low = dictionary.get("attack_damage_low", enemy.attack_damage_low)
    enemy.attack_damage_high = dictionary.get("attack_damage_high", enemy.attack_damage_high)
    enemy.can_move = dictionary.get("can_move",enemy.can_move)
    enemy.engage_chance = dictionary.get("engage_chance", enemy.engage_chance)
    enemy.item_drop = drop_list

    return enemy


#Tile serialization
def tile_to_dict(tile: Tile) -> dict:
    """
    Turns the tile object data into a dictionary

    Parameters:
        tile (Tile): The tile

    Returns the dictionary 
    """
    data = {
        "type": type(tile).__name__,
        "symbol": tile.symbol,
        "walkable": tile.walkable,
        "item": item_to_dict(getattr(tile, "item", None)),
        "enemy": enemy_to_dict(getattr(tile, "enemy", None))
    }

    return data


def tile_from_dict(dictionary: dict) -> Tile:
    """
    Turns the tile from the dictionary into a Tile object

    Parameters:
        dictionary (dict): The dictionary

    Returns the Tile object
    """
    tile_type = TILE_TYPES.get(dictionary["type"], FloorTile)
    tile = tile_type()
    tile.symbol = dictionary.get("symbol", tile.symbol)
    tile.walkable = dictionary["walkable"]
    tile.item = item_from_dict(dictionary.get("item"))
    tile.enemy = enemy_from_dict(dictionary.get("enemy"))

    return tile


#Player serialization
def player_to_dict(player: Player) -> dict:
    """
    Turns the player data into a dictionary

    Parameters:
        player (Player): The player

    Returns the dictionary 
    """
    inventory = []
    if player.inventory:
        inventory = []
        for item in player.inventory:
            inventory.append(item_to_dict(item))

    data = {
        "x": player.x, 
        "y": player.y,
        "hp": player.hp, 
        "gold": player.gold,
        "at_exit": player.at_exit,
        "MAX_HP": player.MAX_HP,
        "weapon": item_to_dict(player.weapon),
        "inventory": inventory,
    }

    return data


def player_from_dict(dictionary: dict) -> Player:
    """
    Turns the player from the dictionary into a Player object

    Parameters:
        dictionary (dict): The dictionary

    Returns the Player object
    """
    inventory = []
    if dictionary.get("inventory"):
        for item in dictionary["inventory"]:
            inventory.append(item_from_dict(item))

    player = Player()
    player.x = dictionary.get("x", player.x)
    player.y = dictionary.get("y", player.y)
    player.hp = dictionary.get("hp", player.hp)
    player.gold = dictionary.get("gold", player.gold)
    player.at_exit = dictionary.get("at_exit", False)
    player.MAX_HP = dictionary.get("MAX_HP", Player.MAX_HP)
    player.weapon = item_from_dict(dictionary.get("weapon"))
    player.inventory = inventory

    return player


#Grid serialization
def grid_to_dict(grid: list[list[Tile]]) -> dict:
    """
    Turns the grid data into a dictionary

    Parameters:
        grid (list[list[Tile]]): The grid

    Returns the dictionary 
    """
    tiles_data = []
    for row in grid:                        
        row_data = [] #New row                      
        for tile in row:                        
            tile_dictionary = tile_to_dict(tile)      
            row_data.append(tile_dictionary)      
        tiles_data.append(row_data)        

    data = {
        "rows": len(grid),
        "columns": len(grid[0]) if grid else 0,
        "tiles": tiles_data,
    }

    return data


def grid_from_dict(dictionary: dict) -> list[list[Tile]]:
    """
    Turns the grid data from the dictionary into a list of list of Tiles

    Parameters:
        dictionary (dict): The dictionary

    Returns the list of list of Tiles (grid)
    """
    tiles = dictionary["tiles"]

    grid = []  
    for row in tiles:                     
        new_row = []                       
        for tile_dictionary in row:                 
            tile = tile_from_dict(tile_dictionary)  
            new_row.append(tile)           
        grid.append(new_row)   

    return grid


def save_game(path: Path, grid: list[list[Tile]], player: Player, level_index: int, play_time: float):
    """
    Saves the current game state to a JSON file.
    Automatically creates the parent directory if needed.
    """
    data = {
        "version": 1,
        "level_index": level_index,
        "player": player_to_dict(player),
        "grid": grid_to_dict(grid),
        "play_time": play_time,
    }

    try:
        #Creates the parent folder if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        #Writes in the file
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        print(f"Game saved to {path}")
    except Exception as e:
        print(f"Error saving game: {e}")


def validate_save(data: dict) -> bool:
    """
    Validates the save file.

    Parameters:
        data (dict): The data

    Returns true if the save file is valid, else returns false
    """
    try:
        #Must be a dictionary
        if not isinstance(data, dict):
            return False
        #Must have player, grid, and level_index
        if "player" not in data or "grid" not in data or "level_index" not in data:
            return False

        player = data["player"]
        if not (0 <= player.get("hp", 0) <= player.get("MAX_HP", 15)):
            return False
        grid = data["grid"]
        if grid["rows"] <= 0 or grid["columns"] <= 0:
            return False
        if "play_time" in data and not isinstance(data["play_time"], (int, float)):
            return False
        return True
    
    except Exception:
        return False



def load_game(path: Path) -> tuple[list[list[Tile]], Player, int, list[str]] | None:
    """
    Loads the game state from a JSON file if it exists.
    Returns (grid, player, level_index, play_time) or None if file missing/corrupted.
    """
    # Check if the file exists first
    if not path.exists():
        print(f"No save file found at {path}")
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8")) #reads the file as a string then converts it into a dictionary

        if not validate_save(data):
            print("Save file invalid or corrupted.")
            return None

        level_index = data.get("level_index", 1)
        player = player_from_dict(data["player"])
        grid = grid_from_dict(data["grid"])
        play_time = float(data.get("play_time", 0.0))

        print(f"Game loaded from {path}")
        return grid, player, level_index, play_time

    except json.JSONDecodeError:
        print("Save file is corrupted or incomplete.")
        return None
    except Exception as e:
        print(f"Unexpected error while loading game: {e}")
        return None


def save_best(best_score: int, best_time: float | None):
    """
    Saves the best score and best time (seconds)

    Parameters: 
        best_score (int): The number of gold
        best_time (float | None): The time taken to play the game
    """
    data = {"best_score": best_score, "best_time": best_time}
    HIGHSCORES_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_best() -> dict:
    """
    Returns the data from highscores.json as a dictionary if it exists
    """
    if not HIGHSCORES_JSON.exists():
        return {"best_score": 0, "best_time": None}
    try:
        data = json.loads(HIGHSCORES_JSON.read_text(encoding="utf-8"))
        return {
            "best_score": int(data.get("best_score", 0)),
            "best_time": (float(data["best_time"]) if data.get("best_time") is not None else None),
        }
    except Exception:
        return {"best_score": 0, "best_time": None}

#========================================================
#Functions
#========================================================

"""
A dictionary that maps the symbols in the map to their corresponding Tile class
"""
SYMBOL_TO_TILE = {
"#": WallTile,
".": FloorTile,
"T": TreasureChestTile,
"X": ExitTile,
}

"""
A dictionary that maps the symbols in the map to the corresponding item
"""
SYMBOL_TO_ITEM = {
    "$": Gold,
    "p": Potion,
}


def make_map(map_text: list[str], level: int) -> list[list[Tile]]:
    """
    Converts MAP_TEXT (list of strings) into a grid of Tile objects.

    Parameters:
        map (list[str]): the map as a list of strings

    Returns:
        The map as a list of Tile objects
    """
    grid = []
    for row in map_text:
        grid_row = []
        for character in row:
            #Turns the character into a tile object 

            tile = (SYMBOL_TO_TILE.get(character, FloorTile))() #defaults to FloorTile

            #Checks if there are any items and adds them to the tile
            if character in SYMBOL_TO_ITEM:
                tile.item = (SYMBOL_TO_ITEM.get(character, None))() 

            #Checks if there is an enemy and adds it to the tile
            if character == "E":
                if level == 1:
                    tile.enemy = pick_random([Enemy(), EnemyWithItem()])
                if level == 2:
                    tile.enemy = pick_random([EnemyLevelTwo(), EnemyLevelTwoWithItem()])
                if level == 3:
                    tile.enemy = pick_random([EnemyLevelThree(), EnemyLevelThreeWithItem()])

                #Keep track of the enemy's location
                tile.enemy.x, tile.enemy.y = len(grid_row), len(grid)

            #Add the tile to the grid row
            grid_row.append(tile)
        #Add the grid row to the grd
        grid.append(grid_row)
    return grid


def load_level(map_text: list[str], level: int):
    """
    Builds a grid for the given map and returns (grid, start_x, start_y).

    Parameters:
        map_text (list[str]): The map text 

    Returns the grid, start_x, and start_y
    """
    grid = make_map(map_text, level)
    start_x, start_y = find_player(map_text)
    return grid, start_x, start_y


def inventory_text(inventory: list[Item]) -> str:
    """
    Turns the player's inventory data into string and returns it

    Parameters:
        inventory (list[Item]): The player' inventory

    Returns the inventory as a string
    """
    if not inventory:
        return "(empty)"
    counts = {}
    for item in inventory:
        counts[item.name] = counts.get(item.name, 0) + 1

    text = []

    for name, n in counts.items():
        if n > 1:
            text.append(f"{name} x{n}")
        else:
            text.append(name)

    result = ", ".join(text)
    return result


def weapon_text(weapon: Weapon) -> str:
    """
    Turns the player's weapon data into string and returns it

    Parameters:
        weapon (Weapon): The player's weapon

    Returns the weapon as a string
    """
    if not weapon:
        return "-"
    else:
        return weapon.name
    

def atk_text(weapon: Weapon) -> str:
    """
    Turns the player's weapon attack data into string and returns it

    Parameters:
        weapon (Weapon): The player's weapon

    Returns the weapon's attack data as a string
    """
    if not weapon:
        return "1-2"
    else:
        return f"{weapon.attack_low}-{weapon.attack_high}"
    
def hp_text(hp: int) -> str:
    """
    Turns the player's hp data into string and returns it

    Parameters:
        hp (int): The player's hp

    Returns the player's hp as a string
    Returns zero if player's hp <= 0
    """
    if hp <= 0:
        return 0
    else:
        return hp


def render(grid: list[list[Tile]], player: Player, log: list[str]):
    """
    Renders the game

    Parameters:
        grid (list[list[Tile]]): The map 
        player (Player): The player
        log (list[str]): The log
    """
 
    right = [
        f"\x1b[38;5;15;1;4mStatus{RESET}:",
        f"\x1b[38;5;15;1mHP{RESET} : {hp_text(player.hp)}              \x1b[38;5;15;1mATK{RESET} : {atk_text(player.weapon)}",
        f"\x1b[38;5;15;1mGold{RESET} : {player.gold}",
        f"\x1b[38;5;15;1mWeapon{RESET} : {weapon_text(player.weapon)}",
        f"\x1b[38;5;15;1mInventory{RESET} : {inventory_text(player.inventory)}",
        "",
        f"\x1b[38;5;15;1mEnemies remaining{RESET}: {enemies_remaining(grid)}",
        "",
        f"\x1b[38;5;15;1;4mActions{RESET}:",
        f"\x1b[38;5;15;1m[W]{RESET}Up \x1b[38;5;15;1m[S]{RESET}Down \x1b[38;5;15;1m[A]{RESET}Left \x1b[38;5;15;1m[D]{RESET}Right \x1b[38;5;15;1m[F]{RESET}Fight \x1b[38;5;15;1m[R]{RESET}Run",
        f"\x1b[38;5;15;1m[T]{RESET}Take \x1b[38;5;15;1m[U]{RESET}Use \x1b[38;5;15;1m[Q]{RESET}Quit \x1b[38;5;15;1m[P]{RESET}Save \x1b[38;5;15;1m[L]{RESET}Load",
        "",
        f"\x1b[38;5;15;1;4mKey{RESET}:",
        f"\x1b[38;5;253;1m[#]{RESET}Wall \x1b[38;5;236;1m[.]{RESET}Floor \x1b[38;5;122;1m[@]{RESET}Player \x1b[38;5;160;1m[E]{RESET}Enemy ",
        f"\x1b[48;5;75;1m[X]{RESET}Exit \x1b[38;5;228;1m[$]{RESET}Gold  \x1b[38;5;91;1m[P]{RESET}Potion \x1b[38;5;35;1m[T]{RESET}Treasure"
    ]

    print(CLEAR) #clears the screen
    print()

    #prints the map on the left and the stats on the right
    for y, row in enumerate(grid):
        # build one line of map text
        map_line = ""
        for x, tile in enumerate(row):
            if x == player.x and y == player.y:
                character = "@"
            elif tile.item is not None:
                character = tile.item.symbol
            elif tile.enemy is not None:
                character = tile.enemy.symbol
            else:
                character = tile.symbol
            map_line += symbol_colour(character)

        print(map_line.ljust(40), end="") #aligns text to the left
        if right:
            print("   " + right.pop(0)) #returns and deletes the element at index 0
        else:
            print()

    #prints the log
    print(f"\n\x1b[38;5;15;1;4mLog{RESET}:")
    for line in log[-5:]: #prints the last five lines in log
        print("• " + line)


def pick_random(items, amount: int = 1, allow_duplicates: bool =False):
    """
    Picks a random element from a list

    Parameters:
        items (list): The list of items 
        amount (int): The number of randomized items to generate
        allow_duplicates(bool): True if duplicates are allowed

    Returns: A randomized item or list of items
    """
    if amount == 1:
        return random.choice(items)
    elif allow_duplicates:
        return random.choices(items, k=amount)
    else:
        return random.sample(items, amount)
    

def read_int(prompt: str, log: list[str], grid: list[list[Tile]], player: Player, min_val: Optional[int] = None, max_val: Optional[int] = None,) -> int | None:
    """
    Reads the input from the user and returns it as an int

    Parameters:
        prompt (str): The question to ask the user
        log (list[str]): The log
        grid (list[list[Tile]]): The map grid
        player (Player): The player
        min_val (int): The minumum value the user must enter
        max_val (int): The maximum value the user can enter

    Returns: the input from the user as an int, returns None if the player's input is 0
    """

    while True:
        try:
            render(grid, player, log)
            result = int(input(prompt).strip())
            if min_val is not None and result < min_val:
                log.append(f"Please enter a value that is bigger than {min_val}.")
                continue
            if max_val is not None and result > max_val:
                log.append(f"Please enter a value that is smaller than {max_val}.")
                continue
            if result == 0:
                return None
            return result
        except ValueError:
            log.append("Please enter a whole number.")


def format_duration(seconds: float | None) -> str:
    """
    Formats the duration
    """
    if seconds is None:
        return "-"
    
    total = int(seconds)

    hour, remainder = divmod(total, 3600) #divide by 3600 to get hours
    minute, second = divmod(remainder, 60) #divide by 60 to get minutes
    return f"{hour:02}:{minute:02}:{second:02}"


def find_player(map_rows: list[str]) -> Tuple[int, int]:
    """
    Finds where the player is on the map (at the start of the game)

    Parameters:
        map_rows (list[str]): The map
    
        Returns the position of the player as a tuple
    """
    for y, row in enumerate(map_rows):
        x = row.find("@")
        if x != -1:
            return x, y
    raise ValueError("No player on map")


def enemies_remaining(grid: list[list[Tile]]) -> int:
    """
    Finds the total number of enemies in the map

    Parameters:
        grid (list[list[Tile]]): The grid

    Returns the total number of enemies in the map
    """
    total = 0  #Counter for enemies found
    
    #Loops through each row in the map grid
    for row in grid:
        #Loops through each tile in the row
        for tile in row:
            #Checks if the tile has an enemy, returns tile.enemy if it has an enemy, if not, returns None
            enemy = getattr(tile, "enemy", None)
            
            #Adds the enemy to the count
            if enemy is not None:
                total += 1
    
    return total


def in_bounds(grid: list[list[Tile]], x: int, y: int) -> bool:
    """
    Checks whether a coordinate is inside the map

    Parameters:
        grid (list[list[Tile]]): The grid
        x (int): The x position
        y (int): The y position

    Returns true if the coordinate is inside the map
    """
    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
        in_bounds = True
    else:
        in_bounds = False
    return in_bounds


def is_blocked_for_enemy(grid: list[list[Tile]], x: int, y: int) -> bool:
    """
    Checks whether the tile is blocked so the enemy can't enter

    Parameters:
        grid (list[list[Tile]]): The grid
        x (int): The x position
        y (int): The y position

    Returns true if the tile is blocked for the enemy 
    """
    #If outside the map bounds, it's blocked
    if not in_bounds(grid, x, y):
        return True
    
    tile = grid[y][x]
    if not tile.walkable: #wall or blocked exit
        return True
    if getattr(tile, "enemy", None) is not None: #if there is already an enemy on the tile
        return True
    if getattr(tile, "item", None) is not None: #if there is an item on the tile
        return True
    if isinstance(tile, TreasureChestTile):
        return True
    return False


def surrounding_tiles(x: int, y: int) -> list:
    """
    Returns the four adjacent tiles as a list
    """
    return [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]


def list_enemies(grid: list[list[Tile]]) -> list[Tuple]:
    """
    Finds all the enemies on the map and puts them in a list 

    Parameters:
        grid (list[list[Tile]]): The grid
    
    Returns a list of the enemies with their coordinates
    """
    result = []                

    #Go through every row in the grid
    for y, row in enumerate(grid):      
        # Go through every tile in the row
        for x, tile in enumerate(row):         
            # Check if the tile has an enemy object stored in tile.enemy, if no, return None
            if getattr(tile, "enemy", None) is not None:
                result.append((x, y, tile.enemy))

    return result


def move_enemies(grid: list[list[Tile]], player: Player, log: list[str]):
    """
    Moves each enemy with can_move = True one tile at a time

    Parameters:
        grid (list[list[Tile]]): The grid
        player (Player): The player
        log (list[str]): The log
    """
    enemies_list = list_enemies(grid) #Gets the list of enemies
    random.shuffle(enemies_list)  #Shuffles the list (to avoid consistent movement)

    reserved: set[tuple[int, int]] = set()  # create an empty set used to avoid enemies choosing the same tile

    for x, y, enemy in enemies_list:
        #Skip if enemy disappeared (defeated) or can't move
        if grid[y][x].enemy is not enemy:
            continue
        if not getattr(enemy, "can_move", True):
            continue
        if x == player.x and y == player.y:
            continue

        #If next to player, sometimes will enter and attack, sometimes stays still
        if abs(x - player.x) + abs(y - player.y) == 1:
            # If another enemy already at player tile
            if (player.x, player.y) in reserved:
                continue

            #Random chance to see if the enemy will attack
            engage_p = getattr(enemy, "engage_chance", 0.5)
            if random.random() < engage_p:
                # Enter player's tile and attack
                grid[y][x].enemy = None
                grid[player.y][player.x].enemy = enemy
                enemy.x, enemy.y = player.x, player.y
                reserved.add((player.x, player.y))
                log.append(f"A {enemy.name} lunges at you!")
                enemy.attack(player, log)
                log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")
            else:
                #Don't move
                pass
            continue

        possible_tiles = []

        #Go through every surrounding tile
        for (nx, ny) in surrounding_tiles(x, y):

            # Check if that coordinate is not blocked and that the coordinate has not been reserved by another enemy
            if not is_blocked_for_enemy(grid, nx, ny) and (nx, ny) not in reserved:
                possible_tiles.append((nx, ny))

        if not possible_tiles: #If there are no possible tiles
            continue
        
        #Choose a tile to move into
        nx, ny = random.choice(possible_tiles)
        grid[y][x].enemy = None #Clear the old tile
        grid[ny][nx].enemy = enemy #Move to new tile
        enemy.x, enemy.y = nx, ny #Update enemy's coordinates
        reserved.add((nx, ny)) #Mark the chosen tile as reserved

        if grid[ny][nx] == grid[player.y][player.x]:
            log.append(f"A {enemy.name} has found you!")
            log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")


def handle_quit(grid: list[list[Tile]], player: Player, log: list[str]):
    """
    Handles quitting

    Parameters:
        grid (list[list[Tile]]): The grid
        player (Player): The player
        log (list[str]): The log
    """
    log.append("You quit the adventure.")
    render(grid, player, log)

def handle_picking_up_items(tile: Tile, player: Player, log: list[str], grid: list[list[Tile]]):
    """
    Handles picking up items

    Parameters:
        tile (Tile)
    """
    #If the tile is a treasure chest tile
    if isinstance(tile, TreasureChestTile):
        tile.on_interact(player, log, grid)
    else:
        tile.on_interact(player, log)


def handle_save(grid: list[list[Item]], player: Player, log: list[str], level_index: int, current_play_time: float):
    """
    Handles saving the game

    Parameters:
        grid (list[list[Item]]): The grid
        player (Player): The player
        log (list[str]): The log
        level_index (int): The level the player is at
        current_play_time (float): The current play time
    """
    if GAME_JSON.exists():
        log.append("Save file already exists. Overwrite? (y/n)")
        render(grid, player, log)
        while True:
            choice = input("> ").strip().lower()
            if choice != "y" and choice != "n":
                log.append("Please enter a valid input.")
                render(grid, player, log)
            else:
                break

        if choice == "n":
            log.append("Save cancelled.")
            
        elif choice == "y":
            save_game(GAME_JSON, grid, player, level_index, current_play_time)
            log.append("Game saved.")

    else:
        save_game(GAME_JSON, grid, player, level_index, current_play_time)
        log.append("Game saved.")


def show_highscore(grid: list[list[Item]], player: Player, log: list[str], best: dict):
    """
    Shows the highscore

    Parameters:
        grid (list[list[Item]]): The grid
        player (Player): The player
        log (list[str]): The log
        bets (dict): The highscore
    """
    log.append("Show highscore? (y/n)")

    while True:
        render(grid, player, log)
        command = input("> ").strip().lower()
        if command != "y" and command != "n":
            log.append("Please enter a valid input")
        else:
            break

    if command == "y":
        log.append("------Highscore------")
        log.append(f"Best score: {best['best_score']}")
        log.append(f"Best time: {format_duration(best['best_time'])}")
        render(grid, player, log)

    elif command == "n":
        pass

#========================================================
#Main
#========================================================

def main():
    #prepares the game
    level_index = 1
    grid, start_x, start_y = load_level(LEVELS[level_index - 1], level_index)
    player_x, player_y = start_x, start_y
    player = Player(player_x, player_y)
    session_start = time.monotonic()
    accumulated_play_time = 0.0
    best = load_best()
    run_away = False
    log: list[str] = ["Welcome to your new adventure!"]
    log.append("Defeat all the enemies, find the exit, and escape!")
    log.append("Press [W] to go up, [S] to go down, [A] to go left, [D] to go right.")
    log.append("Remember to press [enter] to enter your input!")

    #Player input
    try:
        while True:
            render(grid, player, log)
            command = input("> ").strip().lower()
            dx = 0
            dy = 0
            current_tile = grid[player.y][player.x]

            if not command:
                continue
            
            #Player can't move if there's an enemy at the tile
            elif run_away == False and current_tile.enemy and (command == "w" or command == "s" or command == "a" or command == "d"): 
                log.append(f"You can't move! There is a {current_tile.enemy.name} blocking your way.")
                log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")
                continue
            
            #Player quits
            elif command == "q":
                handle_quit(grid, player, log)
                break

            #Handles movement
            elif command == "w": 
                dy = -1 #y-axis increases downwards
                run_away = False
            elif command == "s": 
                dy = 1
                run_away = False
            elif command == "a": 
                dx = -1
                run_away = False
            elif command == "d": 
                dx = 1
                run_away = False

            #Picking up items
            elif command == "t":
                handle_picking_up_items(current_tile, player, log, grid)
                continue
        
            #Using items
            elif command == "u":
                inventory_used = False
                if player.inventory == []:
                    log.append("Your inventory is empty, there is nothing to use.")
                else:
                    message = "Choose an item: [0] Back "
                    for i, item in enumerate(player.inventory, start=1):
                        message += f"[{i}] {item.name} "
                    log.append(message)
                    render(grid, player, log)

                    choice = read_int("> ", log, grid, player, 0, len(player.inventory))

                    if choice == None:
                        log.append("You decide not to use anything.")
                        continue
                    index = choice - 1
                    player.inventory[index].on_use(player, log)
                    player.inventory.pop(index)
                    inventory_used = True

                #If the player is currently fighting (tile has an enemy), then the enemy will attack after the player uses an item
                if current_tile.enemy and inventory_used:
                    current_tile.enemy.attack(player, log)
                    log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")
                continue

            #Fighting
            elif command == "f":
                if run_away:
                    log.append("You have already run away.")
                    continue
                if current_tile.enemy:
                    if player.weapon:
                        current_tile.enemy.take_damage(player.weapon.get_attack(), player, log, grid, current_tile)
                    else:
                        current_tile.enemy.take_damage(random.randint(1,2), player, log, grid, current_tile)

                    if current_tile.enemy:
                        current_tile.enemy.attack(player, log)
                        log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")
                else:
                    log.append("There is nothing to fight.")
                continue

            #Running away
            elif command == "r":
                if run_away:
                    log.append("You have already run away.")
                    continue

                if current_tile.enemy:
                    result = random.randint(1,6)
                    if result <= 3:
                        run_away = True
                        log.append("You successfully run away.")
                    else:
                        log.append("You try to run away but fail.")
                        current_tile.enemy.attack(player, log)
                        log.append("Press [F] to fight, [R] to run away, or [U] to use an item.")
                    continue
                else:
                    log.append("There is nothing to runaway from.")
                    continue

            #Saving the game
            elif command == "p":
                current_play_time = accumulated_play_time + (time.monotonic() - session_start)
                handle_save(grid, player, log, level_index, current_play_time)
                continue

            #Loading the game
            elif command == "l":
                log.append("Are you sure you want to load from a save file? (y/n)")
                render(grid, player, log)

                while True:
                        choice = input("> ").strip().lower()
                        if choice != "y" and choice != "n":
                            log.append("Please enter a valid input.")
                            render(grid, player, log)
                        else:
                            break

                if choice == "n":
                    log.append("Load cancelled.")
                elif choice == "y":
                    result = load_game(GAME_JSON)
                    if result is None:
                        log.append("No valid save file found or file is corrupted.")
                    else:
                        grid, player, level_index, loaded_play_time = result
                        accumulated_play_time = loaded_play_time
                        session_start = time.monotonic()
                        log.append("Game loaded successfully.")
                continue

            #Unknown commands
            else:
                log.append("Unknown command.")
                continue


            #------Game over if player's hp is depleted------
            if player.hp <= 0:
                log.append("Your health has been depleted.")
                log.append("GAME OVER!")
                render(grid, player, log)
                break

            #------Player moves------
            new_x, new_y = player.x + dx, player.y + dy

            if new_x < 0 or new_x >= len(grid[0]) or new_y >= len(grid) or new_y < 0:   #Stops player from moving outside the map
                log.append("You can't move outside the map.")
                continue

            next_tile = grid[new_y][new_x]
            #If the tile is walkable, move player
            if next_tile.walkable: 
                player.x, player.y = new_x, new_y
                if isinstance(next_tile, ExitTile):
                    next_tile.on_enter(player, log, grid)
                else:
                    next_tile.on_enter(player, log)

                move_enemies(grid, player, log) #Move enemies

            #If the tile is not walkable, player doesn't move
            elif not next_tile.walkable:  
                if isinstance(next_tile, ExitTile):
                    next_tile.on_enter(player, log, grid)
                else:
                    next_tile.on_enter(player, log)

                
            #------Next level or win------
            if player.at_exit:
                if level_index < len(LEVELS):
                    level_index += 1
                    log.append("You step through the exit.")
                    log.append(f"Welcome to Level {level_index}!")
                    grid, start_x, start_y = load_level(LEVELS[level_index - 1], level_index)
                    player.x, player.y = start_x, start_y
                    player.at_exit = False
                    run_away = False
                    #Health increases
                    player.MAX_HP += 5
                    player.hp = player.MAX_HP
                else:
                    total_time = accumulated_play_time + (time.monotonic() - session_start)
                    log.append("You step through the final exit.")
                    log.append(f"\x1b[38;5;206;1m------Congratulations, you win!------{RESET}")
                    log.append(f"Your score (gold): {player.gold}")
                    log.append(f"Total time: {format_duration(total_time)}")

                    #Update highscore
                    new_best_score = max(best["best_score"], player.gold)
                    if best["best_time"] is None or total_time < best["best_time"]:
                        new_best_time = total_time
                    else:
                        new_best_time = best["best_time"]

                    #Save the new highscore if changed 
                    if new_best_score != best["best_score"] or new_best_time != best["best_time"]:
                        save_best(new_best_score, new_best_time)
                        best = {"best_score": new_best_score, "best_time": new_best_time}
                        log.append(f"\x1b[38;5;226;1mNew highscore achieved!{RESET}")

                    render(grid, player, log)
                    show_highscore(grid, player, log, best)
                    break

    except GameOver:
        total_time = accumulated_play_time + (time.monotonic() - session_start)
        log.append("Your health has been depleted.")
        log.append(f"\x1b[38;5;160;1m------GAME OVER!------{RESET}")
        log.append(f"Your score (gold): {player.gold}")
        log.append(f"Total time: {format_duration(total_time)}")

        show_highscore(grid, player, log, best)

    except KeyboardInterrupt:
        log.append("You quit the adventure.")
        render(grid, player, log)

            
if __name__ == "__main__":
    main()
