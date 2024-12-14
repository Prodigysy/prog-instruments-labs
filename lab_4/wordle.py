import logging

from typing import Tuple, List
from os.path import abspath, join
from random import randint
from collections import Counter

try:
    from termcolor import colored
    COLOR = True
except ImportError:
    def colored(text, *args, **kwargs):
        return text  # Fallback for missing termcolor module
    COLOR = False


# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('game_log.log'),
                              logging.StreamHandler()])

global ABSPATH
ABSPATH = abspath(".")


def _count_gen(reader):
    b = reader(1 << 20)  # 1 MB at a time
    while b:
        yield b
        b = reader(1 << 20)


def random_line(stream) -> str:
    # Получаем все строки в списке
    lines = stream.readlines()
    # Генерируем случайный индекс
    random_index = randint(0, len(lines) - 1)
    return lines[random_index].strip()
# Возвращаем выбранную строку, удаляя лишние пробелы и символы новой строки


class Wordle_Game:
    '''Game class implementing wordle, no word validation'''

    def __init__(self, wordspath) -> None:
        with open(wordspath, 'rb') as wordslist:
            self._word = random_line(wordslist)[2:-2].upper()
        self.length = len(self._word)
        self.attempts = 0
        self._counter = Counter(self._word)
        self.won = False
        logging.info("Game initialized with word: %s", self._word)
        # Логируем инициализацию игры

    def __len__(self) -> int:
        '''returns how many attempts the player has made'''
        return self.attempts

    def _validate(self, word):
        '''Do not use. Internal function'''
        bull, cow = 0, self._counter & Counter(word)
        # Counter intersection, letters match but wrong place
        res = [None] * len(word)
        cows = [None] * len(word)

        # First pass matches the letters together
        for idx, (x, y) in enumerate(zip(self._word, word)):
            if x == y:  # Bull
                cow[x] -= 1
                bull += 1
                res[idx] = colored(x, 'green', attrs=['reverse'])

        # Second pass processes wrong place letters
        for idx, x in enumerate(word):
            if res[idx] is None:
                if cow[x] > 0:
                    cow[x] -= 1  # Subtract one to avoid duplicates
                    if COLOR:
                        res[idx] = colored(x, 'yellow')
                    else:
                        cows[idx] = x
                else:
                    res[idx] = '*'
        return res, cows, bull, len(cow)

    def guess(self, word: str) -> Tuple[List[str], List[str], int, int]:
        '''Outside interface for guesses'''
        if self.won:
            return
        word, cows, bull, cow = self._validate(word)
        self.attempts += 1
        logging.info("Attempt #%d: Player guessed %s", self.attempts, word)
        # Логируем попытку игрока
        if bull == self.length:
            self.won = True
            logging.info("Player won! Word is: %s", self._word)
            # Логируем победу
        return word, cows, bull, cow


def wordle_player(words="passwords.txt") -> bool:
    '''Simple human interface for game'''
    wordspath = join(ABSPATH, words)
    try:
        while True:
            # Main game loop
            game = Wordle_Game(wordspath)
            logging.info("Starting a new game.")  # Логируем начало игры
            print("WORD:\n[", "*" * game.length, "]")
            while not game.won:
                inp = input("> ").upper()
                if len(inp) != game.length:
                    print("  ERR: WRONG LENGTH")
                    logging.warning(
                        "Invalid input length: %s (expected %d)", inp,
                        game.length)
                    # Логируем ошибку длины
                    continue
                word, cow, bullcount, cowcount = game.guess(inp)
                print(f"\r> {''.join(word)} : {len(game)}")
                if not COLOR and cowcount != 0:
                    print(f"> {''.join(cow)} Misplaced")
            else:
                logging.info("Victory! Word was: %s", game._word)
                # Логируем победу
                print("  Victory! ")
                return True
    except EOFError or KeyboardInterrupt:
        logging.info("Game exited. Word was: %s", game._word)  # Логируем выход
        print(f"> Word was:\n> {game._word}")
    return False


if __name__ == "__main__":
    logging.info("Starting Wordle game.")
    wordle_player()
    logging.info("Game ended.")
