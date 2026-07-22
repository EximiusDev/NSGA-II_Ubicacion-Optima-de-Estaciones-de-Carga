import inspect
import pymoo
from pymoo.core.termination import Termination

print('pymoo version:', getattr(pymoo, '__version__', 'unknown'))
print('\n--- Termination source ---\n')
print(inspect.getsource(Termination))
