from enums import WebhookType
from switch import switch
from Views import app
import yaml
import json
import urllib
import urllib2
import pickle

class GithubAPI(object):
    UserRepositories = []
    EnabledRepositories = []
    UserWebhooks = []

    @staticmethod
    def setup(force_update=False):
        # Setup headers    
        GithubAPI.GITHUB_HEADERS = {
            'Authorization': 'token ' + app.user_config['token'], 
            'User-Agent': 'DIY Build Server',
            'Content-Type': 'application/json'
        }
    
        # Setup URLs
        GithubAPI.GITHUB_API_URL = 'https://api.github.com'
        GithubAPI.GITHUB_OWNER_REPOS = GithubAPI.GITHUB_API_URL + '/user/repos'
        GithubAPI.GITHUB_USER_REPO = GithubAPI.GITHUB_API_URL + '/repos/{}/{}'
        GithubAPI.GITHUB_REPO_CONTENTS = GithubAPI.GITHUB_USER_REPO + '/contents/{}'
        GithubAPI.GITHUB_REPO_HOOKS = GithubAPI.GITHUB_USER_REPO + '/hooks'

        def fetch_repos():
            # Try to load repos
            try:
                GithubAPI.UserRepositories = GithubAPI._safe_load(open('.UserRepositories.yml'))
            except:
                pass

            # If no repos are found
            if not GithubAPI.UserRepositories or force_update:
                with GithubAPI.APIRequest(GithubAPI.GITHUB_OWNER_REPOS, GithubAPI.GITHUB_HEADERS) as request:
                    if request.status == 200:
                        for repository in request.data:
                            repository = GithubAPI.Repository(repository)
                            GithubAPI.UserRepositories.append(repository)

                # Safe for later usage
                GithubAPI._safe_dump(GithubAPI.UserRepositories, open('.UserRepositories.yml', 'w'))
            
            for repository in GithubAPI.UserRepositories:
                if repository.enabled:
                    GithubAPI.EnabledRepositories.append(repository)

            print [(_.id, _.name, _.enabled) for _ in GithubAPI.UserRepositories]

        def fetch_hooks():
            for repository in GithubAPI.EnabledRepositories:
                url = GithubAPI.GITHUB_REPO_HOOKS.format(app.user_config['owner'], repository.name)
                with GithubAPI.APIRequest(url, GithubAPI.GITHUB_HEADERS) as request:
                        if request.status == 200:
                            print request.data
                            if len(request.data) == 0:
                                data = {
                                    'name': 'web', 
                                    'active': True, 
                                    'events': ['push', 'pull_request'],
                                    'config': {
                                        'url': 'http://g-build-server.asuscomm.com:5555/hooks',
                                        'content_type': 'json'
                                    }
                                }

                                query = GithubAPI.APIRequest(url, GithubAPI.GITHUB_HEADERS, data=data).query()
                                print query.status

        fetch_repos()
        fetch_hooks()

    @staticmethod
    def _safe_load(fp):
        repositories = yaml.safe_load(fp)
        repositoriesObjs = []

        for repository in repositories:
            repositoriesObjs.append(GithubAPI.Repository(repository['data'], False, repository['enabled']))

        return repositoriesObjs


    @staticmethod
    def _safe_dump(repositoriesObjs, fp):
        repositories = []

        for repository in repositoriesObjs:
            repositories.append({'data': repository.data, 'enabled': repository.enabled})

        yaml.safe_dump(repositories, fp)


    class APIRequest(object):
        def __init__(self, url, headers, data=None):
            self.url = url
            data = json.dumps(data) if data is not None else None
            self.req = urllib2.Request(url, data, headers)
            self.status = 200
            self.data = None

        def query(self):
            return self.__enter__()

        def __enter__(self):
            try:
                response = urllib2.urlopen(self.req)
                self.data = json.loads(response.read())
            except urllib2.HTTPError as e:
                self.status = e.code
            
            return self
        
        def __exit__(self, exception_type, exception_value, traceback):
            return False


    class Repository(object):
        def __init__(self, data, query_enabled = True, enable_override = False):
            self.data = data

            enabled = False
            if query_enabled:
                url = GithubAPI.GITHUB_REPO_CONTENTS.format(app.user_config['owner'], data['name'], '.build.yml')
                with GithubAPI.APIRequest(url, GithubAPI.GITHUB_HEADERS) as request:
                    enabled = request.status == 200

            self.enabled = enabled or enable_override


        def __getattribute__(self, arg):
            try:
                return object.__getattribute__(self, arg)
            except:
                return object.__getattribute__(self, 'data')[arg]


class Webhook(object):
    def __init__(self, data):
        self.data = data

    def __getattribute__(self, arg):
        data = object.__getattribute__(self, 'data')

        for case in switch(arg):
            if case('action'):
                return WebhookType.from_data(data)

            if case():
                return data[arg]

