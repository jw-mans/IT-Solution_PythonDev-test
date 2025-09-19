import os
import sys

from .settings import USERNAME

project_home = f'/home/{USERNAME}/quoteshooter'
if project_home not in sys.path:
    sys.path.append(project_home)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quoteshooter.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
