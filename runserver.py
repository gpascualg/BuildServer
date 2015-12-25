"""
This script runs the BuildServer application using a development server.
"""

from flask import abort, request
from os import environ, getcwd
from netaddr import IPAddress, IPNetwork
from Views.eenum import EEnum
from Views import app
import yaml
import json


class ServerRole(EEnum):
    ANNOUNCER = 1
    SLAVE = 0

    
static_config = {
    ServerRole.ANNOUNCER:
        {
            'HOST': IPAddress('0.0.0.0'),
            'PORT': 5555,
            'DEBUG': True
        },
    ServerRole.SLAVE:
        {
            'HOST': IPAddress('0.0.0.0'),
            'PORT': 5555,
            'DEBUG': True
        }
}


if __name__ == '__main__':
    #        IPs         #
    # ------------------ #

    with open(getcwd() + '/BuildServer/.build.yml') as fp:
        app.user_config = yaml.safe_load(fp)

    # Configure role
    role = ServerRole.from_string(app.user_config.get('role', 'SLAVE'))
    app.user_config['role'] = role

    # Configure masks
    app.user_config['masks'] = [IPNetwork(_) for _ in app.user_config.get('masks', [])]

    # Disallow if not in mask subnets
    @app.before_request
    def limit_remote_addr():
        subnets = [IPNetwork(request.remote_addr + '/' + x.prefixlen).network == x.network for x in app.user_config['masks']]
        if not any(subnets) and subnets:
            abort(403) # Forbidden

    # Start app
    app.secret_key = app.user_config['secret_key']
    app.run(str(static_config[role]['HOST']), 
            static_config[role]['PORT'], 
            debug=static_config[role]['DEBUG'])
