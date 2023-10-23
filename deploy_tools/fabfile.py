from fabric.contrib.files import  exists, upload_template
from fabric.api import cd, env, local, run, sudo

REPO_URL='https://github.com/SteveMayze/leawood_gateway.git'

def deploy():
    site_folder = f'/home/{env.user}/python/leawood_gateway'
    run(f'mkdir -p {site_folder}')
    _stop_gateway()
    with cd(site_folder):
        _get_last_source()
        _update_virtualenv()
        _create_or_update_config()
        ## _create_or_update_daemon()
    ## _start_the_gateway()

def _stop_gateway():
    if exists('src/leawood'):
        if  exists('/etc/init.d/leawood-gateway'):
            sudo('/etc/init.d/leawood-gateway stop', shell=False)
        else:
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
    run('chmod +x leawood-gateway')

def _create_or_update_config():
    upload_template('prod_config_template.ini', 'config.ini')

def _start_the_gateway():
    ### run('nohup .venv/bin/python  -m leawood -c ~/python/leawood_gateway/config.ini start &')
    sudo('/etc/init.d/leawood-gateway start &', shell=False)


def _create_or_update_daemon():
    if  not exists('/etc/init.d/leawood-gateway'):
        sudo('cp leawood-gateway /etc/init.d/', shell=False)
        sudo('chmod 755 /etc/init.d/leawood-gateway', shell=False)


