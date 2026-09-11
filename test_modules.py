import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
from django.conf import settings
settings.ALLOWED_HOSTS = ['*']
django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User

try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')

c = Client()
c.login(username='testuser', password='testpass123')

urls = [
    ('/stocks/', 'Stocks'),
    ('/ipo/', 'IPO'),
    ('/investments/', 'Money Planner'),
    ('/dashboard/', 'Dashboard'),
]

for url, name in urls:
    try:
        resp = c.get(url)
        print(f'{name} ({url}): status={resp.status_code}')
        if resp.status_code != 200:
            content = resp.content[:1000].decode('utf-8', errors='replace')
            # Just print the error title
            import re
            title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
            if title_match:
                print(f'  Error: {title_match.group(1).strip()[:200]}')
        else:
            print(f'  OK - rendered template')
    except Exception as e:
        print(f'{name} ({url}): ERROR - {type(e).__name__}: {e}')
