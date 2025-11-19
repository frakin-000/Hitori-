import os
import sys

# Добавляем корень проекта в sys.path, чтобы модули 'hitori' и 'moduls' были доступны при запуске pytest
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
