from iconservice import *

# ================================================
#  Exceptions
# ================================================
class SeedUninitialized(Exception):
    pass

class Utils:
    # _rand_state should be initialized for each transaction call,
    # using a seed that is hard to guess enough.
    _rand_state: list = [0, 0, 0, 0]

    @staticmethod
    def rotl64(var, rotation):
        var = var & 0xffffffffffffffff
        return (var << rotation) | (var >> (64 - rotation))

    @staticmethod
    def srand(seed: str, use_sha3_256: bool = True) -> None:
        """ Xoshiro256** PRNG 256 bits seed initialization """
        if use_sha3_256:
            seed = sha3_256(seed.encode())
        seed_int = int.from_bytes(bytes(seed), 'big')
        Utils._rand_state[0] = (seed_int & 0xffffffffffffffff)
        seed_int >>= 64
        Utils._rand_state[1] = (seed_int & 0xffffffffffffffff)
        seed_int >>= 64
        Utils._rand_state[2] = (seed_int & 0xffffffffffffffff)
        Utils._rand_state[3] = seed_int >> 64

    @staticmethod
    def rand(min_value: int, max_value: int) -> int:
        """ Xoshiro256** PRNG implementation :
            http://xoshiro.di.unimi.it/xoshiro256starstar.c
        """
        if sum(Utils._rand_state) == 0:
            raise SeedUninitialized

        result = (Utils.rotl64(Utils._rand_state[1] * 5, 7) * 9) & 0xffffffffffffffff

        value = (Utils._rand_state[1] << 17) & 0xffffffffffffffff

        Utils._rand_state[2] ^= Utils._rand_state[0]
        Utils._rand_state[3] ^= Utils._rand_state[1]
        Utils._rand_state[1] ^= Utils._rand_state[2]
        Utils._rand_state[0] ^= Utils._rand_state[3]
        Utils._rand_state[2] ^= value
        Utils._rand_state[3] = Utils.rotl64(Utils._rand_state[3], 45)

        return min_value + (result % max_value)

    @staticmethod
    def shuffle(items: list) -> list:
        """ Fisher–Yates shuffle
            https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
        """
        for pos in reversed(range(len(items))):
            randpos = Utils.rand(0, pos)
            items[pos], items[randpos] = items[randpos], items[pos]
        return items

    @staticmethod
    def rand_pick(items: list):
        randpos = Utils.rand(0, len(items))
        return items[randpos]

    @staticmethod
    def is_ascii(string):
        return all(ord(c) < 127 and ord(c) > 32 for c in string)
