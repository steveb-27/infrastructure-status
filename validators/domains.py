import json

from validator import Validator


class DomainsValidator(Validator):

    name = "Domains"

    def validate(self, context):

        print(f"Running validator: {self.name}")
        print()

        for domain in context.domains:
            name = domain['name']
            print(f"Checking domain: {name}:")

            for record in domain['records']:
                if record['name'] == name:
                    if record['type'] == 'A':
                        print(f"Main A record matches IP: { record['content'] == context.public_ip }")

            print()