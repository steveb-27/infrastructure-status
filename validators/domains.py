import json
from validator import Validator


class DomainsValidator(Validator):

    name = "Domains"

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
                        if record['content'] == context.public_ip:
                            outcome = 'Pass'
                        else:
                            outcome = 'Fail'
                        context.add_result(
                            validator=self.name,
                            config=f"{record['name']} (A Record)",
                            value=record['content'],
                            outcome=outcome
                        )
                elif record['type'] == 'CNAME':
                    found = False
                    # Nginx Check
                    if record['content'] == name:
                        if record['name'] in nginx_domains:
                            context.add_result(
                                validator=self.name,
                                config=f"{record['name']} (CNAME Record)",
                                value='Record exists in Nginx',
                                outcome='Pass'
                            )
                            found = True
                        else:
                            context.add_result(
                                validator=self.name,
                                config=f"{record['name']} (CNAME Record)",
                                value='Record not in Nginx, possibly misconfigured',
                                outcome='Fail'
                            )
                            found = True
                    # CDN Check
                    for index, cdn in enumerate(context.bunnycdn_pull_zone):
                        if record['content'] == cdn['cdn']:
                            if record['name'] in context.bunnycdn_pull_zone[index]['hosts']:
                                context.add_result(
                                    validator=self.name,
                                    config=f"{record['name']} (CNAME Record)",
                                    value=f"Maps to CDN: {cdn['cdn']}",
                                    outcome='Pass'
                                )
                                found = True
                            else:
                                context.add_result(
                                    validator=self.name,
                                    config=f"{record['name']} (CNAME Record)",
                                    value=f"Host not in CDN: {cdn['cdn']}",
                                    outcome='Fail'
                                )
                                found = True
                    # Possibly Misconfigured
                    if not found:
                        context.add_result(
                            validator=self.name,
                            config=f"{record['name']} (CNAME Record)",
                            value=f"Target not found, possibly misconfigured: {record['content']}",
                            outcome='Fail'
                        )
                    continue
                elif record['type'] == 'MX':
                    if record['content'] == context.smtp_hostname:
                        context.add_result(
                            validator=self.name,
                            config=f"{record['name']} (MX Record)",
                            value=f"Correct local MX record configured: {record['content']}",
                            outcome='Pass'
                        )
                    else:
                        context.add_result(
                            validator=self.name,
                            config=f"{record['name']} (MX Record)",
                            value=f"External MX record configured: {record['content']}",
                            outcome='Fail'
                        )
                else:
                    context.add_result(
                            validator=self.name,
                            config=f"{record['name']} ({record['type']} Record)",
                            value=f"Untested DNS entry found: {record['content']}",
                            outcome='TBD'
                        )