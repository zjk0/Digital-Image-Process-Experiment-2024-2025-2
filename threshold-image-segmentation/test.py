import numpy as np

array = np.random.randint(0, 10, (5, 4, 3))
# print(array)
var = (array[:, :, 1] < 5) & (array[:, :, 1] > 1)
print(var)
array[:, :, 0][~var] = 11
print(array)
