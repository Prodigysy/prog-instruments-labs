#./bin/python3
from typing import Tuple, List, Union
from os.path import abspath, join
from random import randint
from collections import Counter
try: # Module not installed for everyone
    from termcolor import colored
    COLOR = True
except:
    global colored
    def colored(x, *_, **__):
        return x
    COLOR = False

# Words from https://people.sc.fsu.edu/~jburkardt/datasets/words

global ABSPATH
ABSPATH = abspath(".")
def _count_gen(reader):
    b = reader(1 << 20) # 1 MB at a time
    while b:
        yield b
        b = reader(1 << 20)

def random_line(stream) -> str:
    # https://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file#3540315
    line = next(stream)
    for index, _line in enumerate(stream, 2):
        if not randint(0, stream):
            line = _line
    return str(line)

class Wordle_Game:
    '''Game class implementing wordle, no word validation'''
    def __init__(self, wordspath) -> None:
        with open(wordspath, 'rb') as wordslist:
            self._word = random_line(wordslist)[2:-2].upper()
        self.length = len(self._word)
        self.attempts = 0
        self._counter = Counter(self._word)
        self.won = False

    def __len__(self) -> int:
        '''returns how many attempts the player has made'''
        # len(Game) --> attempts
        return self.attempts

    def _validate(self, word):
        ''' Do not use. Internal function'''
        bull, cow = 0, self._counter & Counter(word) # Counter intersection, letters match but wrong place
        res = [None] * len(word) # Preallocate to save memory and increase speed
        cows = [None] * len(word)
        # First pass matches the letters together
        for idx, (x,y) in enumerate(zip(self._word, word)):
            if x==y: # Bull
                cow[x] -= 1
                bull += 1
                res[idx] = colored(x, 'green', attrs=['reverse'])

        # Second pass makes sure that wrong place letters processed
        for idx, x in enumerate(word):
            if res[idx] == None:
                if cow[x] > 0:
                    cow[x] -= 1 # Subtract one to not have duplicates
                    if COLOR:
                        res[idx] = colored(x, 'yellow')
                    else:
                        cows[idx] = x
                else:
                    res[idx] = '*'
        return res, cows, bull, len(cow)

    def guess(self, word:str) -> Tuple[List[str], List[str], Int, Int]:
        '''Outside interface for guesses:
        Returns:
            bulls: Array of characters with correct letters in place
            cows : Array of characters with letters in incorrect places
            bull : count of correct characters
            cow  : count of characters in wrong place'''
        if self.won:
            # Already won, no point
            return
        word, cows, bull, cow = self._validate(word)
        self.attempts += 1
        if bull == self.length:
            self.won = True
        return word, cows, bull, cow

def wordle_player(words="passwords.txt") -> bool:
    '''Simple human interface for game'''
    wordspath = join(ABSPATH, words)
    try:
        while True:
            # Main game loop
            game = Wordle_Game(wordspath)
            # Guess length
            print("WORD:\n[", "*" * game.length, "]") 
            while not game.won:
                inp = input("> ").upper()
                if len(inp) != game.length:
                    print("  ERR: WRONG LENGTH") # Undefined case if shorter than word
                    continue
                word, cow, bullcount, cowcount = game.guess(inp)
                print(f"\r> {''.join(word)} : {len(game)}")
                if not COLOR and c != 0:
                    # Gives generic hints as to letter composition
                    print(f"> {''.join(cow)} Misplaced")
            else:
                print("  Victory! ")
                return True
    except EOFError or KeyboardInterrupt:
        # Exit conditions, otherwise throw an exception
        print(f"> Word was:\n> {game._word}")
    return False

if __name__ == "__main__":
    wordle_player()
