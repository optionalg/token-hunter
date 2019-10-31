import json
import os
import re


class Issue:
    def __init__(self, ident, web_url, description):
        self.ident = ident
        self.web_url = web_url
        self.description = description


class Comment:
    def __init__(self, comment_type, parent_url, comment_body):
        self.comment_type = comment_type
        self.comment_body = comment_body
        self.parent_url = parent_url


class Secret:
    def __init__(self, secret_type, secret, url):
        self.secret_type = secret_type
        self.url = url
        self.secret = secret


class SecretsMonitor:

    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), "../regexes.json"), 'r') as f:
            self.regexes = json.loads(f.read())
        for key in self.regexes:
            self.regexes[key] = re.compile(self.regexes[key])

    def sniff_secrets(self, content):
        if len(content.keys()) == 0:
            return []
        secrets = []
        for web_url, raw_data in content.items():
            found_secrets = self.__get_secrets(raw_data)
            for secret_type, secret in found_secrets.items():
                secrets.append(Secret(secret_type, secret, web_url))
        return secrets

    def __get_secrets(self, content):
        result = {}
        if not content:
            return result
        for key in self.regexes:
            match = self.regexes[key].search(content)
            if match:
                result.update({key: match.group()})
        return result
