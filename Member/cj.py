import random
import pdb
from settings import length as length
def generate_random_name(length):
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    name = ''
    for i in range(length):
        if i % 2 == 0:
            name += random.choice(consonants).upper()
        else:
            name += random.choice(vowels)
    return name

pdb.set_trace()

random_name = generate_random_name(length)
print(random_name)
#ss