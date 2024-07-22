from random import randint

def sortArray(array: list) -> list:
    """ Sort list with numbers

    В среднем временная сложность такой сортировки O(n*log2 n).
    O(n) за счет перебора всех элементов, O(log2 n) - из-за разделения на подмассивы.
    Затраты на создание нового листа обусловлены предотвращением ошибок,
        которые могут возникнуть при изменении исходного списка.

    Args:
        array (list): array to be sorted

    Returns:
        list: sorted array
    """
    array_len = len(array)
    if array_len < 2:
        return [val for val in array]

    pivot_index = randint(0, array_len - 1)
    pivot = array[pivot_index]
    less = list()
    greater = list()
    equal = list()

    for value in array:
        if value < pivot:
            less.append(value)
        elif value == pivot:
            equal.append(value)
        else:
            greater.append(value)

    return sortArray(less) + equal + sortArray(greater)
