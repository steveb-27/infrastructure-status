import json
from validator import Validator


class DomainsValidator(Validator):

    name = "DNS"

    def validate(self, context):

        nginx_domains = {
            host
            for config in context.nginx_sites
            for host in config['server_names']
        }

        for domain in context.domains:
            name = domain['name']
            print(f"Checking domain: {name}...")

            for record in domain['records']:
                if record['name'] == name:
                    if record['type'] == 'A':
                        value_exp = context.public_ip
                        value_fnd = record['content']
                        context.add_result(
                            validator = f"{self.name}|A",
                            config = f"{record['name']}",
                            value_exp = value_exp,
                            value_fnd = value_fnd,
                            passes = value_exp == value_fnd
                        )
                elif record['type'] == 'CNAME':
                    # Nginx Check

                    # Check if CNAME is directed at server
                    if record['content'] == name:
                        value_exp = True
                        value_fnd = record['name'] in nginx_domains
                        context.add_result(
                            validator = f"{self.name}|CNAME-NGINX",
                            config = record['name'],
                            value_exp = value_exp,
                            value_fnd = value_fnd,
                            passes = value_exp == value_fnd
                        )
                    # CDN Checks

                    # Check if CNAME points to an active CDN
                    elif record['content'] in [
                        cdn['cdn']
                        for cdn in context.bunnycdn_pull_zone
                    ]:
                        value_exp = True
                        value_fnd = True
                        context.add_result(
                            validator = f"{self.name}|CNAME-CDN-PULLZONE",
                            config = record['name'],
                            value_exp = record['content'],
                            value_fnd = record['content'],
                            passes = value_exp == value_fnd
                        )

                        # Check if the CDN the CNAME points to lists it as one of the hosts
                        hosts = {
                            hosts
                            for cdn in context.bunnycdn_pull_zone if cdn['cdn'] == record['content']
                            for hosts in cdn['hosts']
                        }
                        value_fnd = hosts.copy()
                        value_exp = hosts.copy()
                        value_exp.add(record['name'])
                        context.add_result(
                            validator = f"{self.name}|CNAME-CDN-HOST",
                            config = record['name'],
                            value_exp = value_exp,
                            value_fnd = value_fnd,
                            passes = value_exp == value_fnd
                        )

                    # CNAME is unknown - possibly delete
                    else:
                        context.add_result(
                            validator = f"{self.name}|CNAME",
                            config = record['name'],
                            value_exp = 'Should point to server, CDN or third party service.',
                            value_fnd = record['content'],
                            passes = False
                        )
                elif record['type'] == 'MX':
                    value_exp = context.smtp_hostname
                    value_fnd = record['content']
                    context.add_result(
                        validator = f"{self.name}|MX",
                        config = record['name'],
                        value_exp = value_exp,
                        value_fnd = value_fnd,
                        passes = value_exp == value_fnd
                    )
                else:
                    context.add_result(
                        validator = f"{self.name}|{record['type']}",
                        config = record['name'],
                        value_exp = 'Unknown',
                        value_fnd = record['content'],
                        passes = True
                    )