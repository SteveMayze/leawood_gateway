from fabric.contrib.files import  exists, upload_template
from fabric.api import cd, env, local, run

REPO_URL='https://github.com/SteveMayze/leawood_gateway.git'

def deploy():
    site_folder = f'/home/{env.user}/python/leawood_gateway'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _stop_gateway()
        _get_last_source()
        _update_virtualenv()
        _create_or_update_config()
        # _start_the_gateway()

def _stop_gateway():
    if exists('src/leawood'):
        run('.venv/bin/python -m leawood stop')        

def _get_last_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'git reset --hard {current_commit}')

def _update_virtualenv():
    if not exists('.venv/bin/pip'):
        run(f'python -m venv .venv')
        run('.venv/bin/python -m pip install --upgrade pip')
    run('.venv/bin/pip install -r requirements.txt')
    run('.venv/bin/pip install RPi.GPIO')
    run('.venv/bin/pip install --upgrade --force-reinstall digi-xbee')

def _create_or_update_config():
    upload_template('config_template.ini', 'config.ini')

def _start_the_gateway():
     run('nohup .venv/bin/python  -m leawood -c ~/python/leawood_gateway/config.ini start &')


