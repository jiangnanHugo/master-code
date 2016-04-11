import numpy as np

def get_random_int(lower, upper):
    """ Return pseudo-random integer in interval (inclusive) [lower, upper] """
    return int(np.floor(np.random.random() * (upper - lower + 1)) + lower)


def swap(l, i, j):
    """ Swap item at index i in list l (by reference) with item at index j """
    tmp = l[i]; l[i] = l[j]; l[j] = tmp;


def simple_string_augmentor(sentences):
    """ Arbitrarily swap two neighbouring indices in each sentence.
    If string contains less than 5 characters, it will not be modified.
    Any character may be swapped.

    Keyword arguments:
    sentences -- list of strings
    """
    assert(isinstance(sentences, list))
    assert(isinstance(sentences[0], str))

    augmented = []
    for sentence in sentences:
        s_list = list(sentence)
        max_idx = len(s_list) - 2
        
        if max_idx < 5:
            augmented.append(''.join(s_list))
            continue
        idx = get_random_int(0, max_idx) # index to swap with

        # swap by reference
        swap(s_list, idx, idx+1)
        augmented.append(''.join(s_list))
    return augmented


def swap_chars_by_percent(elements, element_lens, augment_amount):
    """ Each list in elements will have `augment_amount` percent of list
    swapped. Will not swap elements that have been in an earlier step. If
    augment_amount is None, it will perform

    Keyword arguments:
    elements -- list of list of numbers
    element_lens -- list indicating where padding begins in list of elements
    augment_amount -- float indicating augment percentage
    """
    assert(isinstance(elements, list) or isinstance(elements, np.ndarray))
    assert(isinstance(elements[0], list) or isinstance(elements[0], np.ndarray))
    assert(augment_amount is None or augment_amount < 0.4)
    assert(isinstance(element_lens, list) or isinstance(element_lens, np.ndarray))

    augmented = []
    for idx, element in enumerate(elements):
        elems = list(element)
        max_idx = element_lens[idx] - 2

        if max_idx <= 5:
            augmented.append(elems)
            continue

        indices_swapped = set()
        max_steps = ( np.ceil(augment_amount * max_idx) 
                if augment_amount is not None else 1 )

        while len(indices_swapped) <= max_steps:
            swap_idx = get_random_int(0, max_idx)
            # do not swap indices that have already been swapped
            while swap_idx in indices_swapped or swap_idx+1 in indices_swapped:
                swap_idx = get_random_int(0, max_idx)

            # swap by reference
            swap(elems, swap_idx, swap_idx+1)
            # update which indices have been swapped
            indices_swapped.add(swap_idx)
            indices_swapped.add(swap_idx+1)

        augmented.append(elems)
    return np.array(augmented)


class Augmentor:

  def __init__(self, augmentor=swap_chars_by_percent):
    """ Constructor.
    Keyword arguments:
    augmentor -- function for augmenting
    """
    self.augmentor = augmentor


  def run(self, elements, element_lens=None, augment_amount=None):
    """ Perform augmentation on list of elements.
    If default augmentor `augment_amount` is ignored.
  
    Keyword arguments:
    elements -- a list of elements to augment
    element_lens -- list indicating where padding begins in list of elements
    (default: None)
    augment_amount -- percent of element to augment (default: None)
    """
    return self.augmentor(elements, element_lens, augment_amount)


if __name__ == "__main__":
    simple = Augmentor()
    a = np.array([ [0,1,2,3,4,5,6,7,8,9] ])
    lens = [len(x) for x in a]
    result = simple.run(a, lens)
    [print(a, "\n", r, "\n") for r in result]
    advanced = Augmentor()
    a = np.array([
        [0,1,2,3,4,5,6,7,8,9],      # should have two elements swapped
        [10,11,12,13,14,15,16],     # should not have any swapped elements
        [10,11,12,13,14,15,16,17],  # should have two elements swapped 
        ])
    lens = [len(x) for x in a]
    result = advanced.run(a, lens, 0.2)
    [print(np.array(c), "\n", np.array(r), "\n") for c, r in zip(a, result)]
