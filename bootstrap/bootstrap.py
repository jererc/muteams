import os
import urllib.request

url = 'https://raw.githubusercontent.com/jererc/svcutils/refs/heads/main/svcutils/bootstrap.py'
exec(urllib.request.urlopen(url).read().decode('utf-8'))
Bootstrapper(
    name='muteams',
    install_requires=[
        # 'git+https://github.com/jererc/muteams.git',
        'muteams @ https://github.com/jererc/muteams/archive/refs/heads/main.zip',
    ],
    force_reinstall=True,
    init_cmds=[
        ['playwright', 'install-deps'],
    ],
    extra_cmds=[
        ['playwright', 'install', 'chromium'],
    ],
    shortcuts=[
        {'name': 'muteams', 'args': ['muteams.main', '-p', os.getcwd()], 'headless': False},
    ],
    download_assets=[
        ('user_settings.py', 'https://raw.githubusercontent.com/jererc/muteams/refs/heads/main/bootstrap/user_settings.py'),
    ],
)
