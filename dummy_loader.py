from frostings import loader
import numpy as np

def simple_dummy_sample(max_len, max_len_spaces):
    # setting variables
    elem_len = np.random.choice(int(max_len)) # generates a random len seq
    max_spaces = max_len_spaces

    # setting holders
    space_counter = 0
    elem_X = ""
    elem_t = ""

    # generating output
    for _ in range(elem_len):
        elem_X += str(np.random.choice(10))
        rand = np.random.choice(1)
        if np.random.choice(max(int(elem_len/max_spaces), 1)) == 1:
            if space_counter < max_spaces:
                elem_X += " "
                space_counter += 1
    elem_t = elem_X # X and t are the same (why it's called "simple")
    return elem_X, elem_t

advanced_dict = []
advanced_dict.append({
    '0': 'zero',
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    ' ': ' '
})
advanced_dict.append({
    '0': 'nul',
    '1': 'en',
    '2': 'to',
    '3': 'tre',
    '4': 'fire',
    '5': 'fem',
    '6': 'seks',
    '7': 'syv',
    '8': 'otte',
    '9': 'ni',
    ' ': ' '
})

make_caps = {
    'z': 'Z',
    'e': 'E',
    'r': 'R',
    'o': 'O',
    'n': 'N',
    't': 'T',
    'w': 'W',
    'h': 'H',
    'f': 'F',
    'u': 'U',
    'i': 'I',
    'v': 'V',
    's': 'S',
    'x': 'X',
    'g': 'G',
    'l': 'L',
    'k': 'K',
    'y': 'Y',
    'm': 'M',
    ' ': ' ',
}


def dummy_sampler(max_len, max_len_spaces, sampler='normal'):
    assert sampler in ['normal', 'talord', 'talord_caps1', 'talord_caps2',
        'talord_caps3']
    elem_X, elem_t = simple_dummy_sample(max_len, max_len_spaces)
    if sampler == 'normal':
        pass # base case
    else:
        # Turning it to danish/english (list -> join)
        elem_X = ''.join([advanced_dict[0][e] for e in elem_X])
        elem_t = ''.join([advanced_dict[1][e] for e in elem_t])
        if sampler == 'talord_caps1' or sampler=="talord_caps3":
            holder = [] # hacked around str assignment
            for e in elem_X:
                if np.random.choice(2):
                    holder.append(make_caps[e])
                else:
                    holder.append(e)
            elem_X = ''.join(holder)
        if sampler == 'talord_caps2' or sampler=="talord_caps3":
            if np.random.choice(4) == 0:
                elem_t = ''.join([make_caps[e] for e in elem_t])
    return elem_X, elem_t

class DummySampleGenerator(loader.SampleGenerator):
    """Generates a sample from a dummy sampler

    Extends SampleGenerator
    """


    def __init__(self, make_dummy_sample=dummy_sampler,
                 max_len=4, max_len_spaces=1, sampler='normal'):
        self.make_dummy_sample = make_dummy_sample
        self.max_len = max_len
        self.max_len_spaces = max_len_spaces
        self.sampler = sampler

    def gen_sample(self):
        while True:
            yield self.make_dummy_sample(
                self.max_len, self.max_len_spaces, self.sampler)

if __name__ == '__main__':
    samplers = ['normal', 'talord', 'talord_caps1', 'talord_caps2',
        'talord_caps3']
    for sampler in samplers:
        print
        print('@@@@@')
        print(sampler)
        print('-----')
        dummy_sample_gen = DummySampleGenerator(
            make_dummy_sample = dummy_sampler,
            max_len = 4, max_len_spaces = 1,
            sampler=sampler)
        count = 0
        for sample in dummy_sample_gen.gen_sample():
            print(sample)
            count += 1
            if count > 5:
                break
