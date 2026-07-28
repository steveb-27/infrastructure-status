import os
from dotenv import load_dotenv
from collector import Collector


class PostfixCollector(Collector):

    name = "Postfix"

    def __init__(self):
        load_dotenv()
        self._server_config = os.getenv("POSTFIX_SERVER","MAIL_SERVER")

        self._host = os.getenv(self._server_config + "_HOST")
        self._port = int(os.getenv(self._server_config + "_PORT", "22"))
        self._user = os.getenv(self._server_config + "_USER")
        self._password = os.getenv(self._server_config + "_PASSWORD")

        if not self._host:
            raise RuntimeError(self._server_config + "_HOST is not configured.")

        if not self._user:
            raise RuntimeError(self._server_config + "_USER is not configured.")

        if not self._password:
            raise RuntimeError(self._server_config + "_PASSWORD is not configured.")

    def collect(self, context):
        output = self.run_command("postconf -n")
        output_parsed = self._parse(output)

        context.smtp_hostname = output_parsed.get('myhostname','')
        context.postfix = output_parsed

        print(f"Retrieved {len(context.postfix)} Postfix settings")

    def remediate(self, context):
        # Console comands for fixes
        '''
        sudo postconf -X sender_dependent_relayhost_maps
        sudo systemctl reload postfix


        sudo mkdir -p /etc/opendkim/keys
        sudo chown -R opendkim:opendkim /etc/opendkim
        sudo -u opendkim mkdir -p /etc/opendkim/keys/eclipsebtq.com
        sudo -u opendkim opendkim-genkey --bits=2048 --domain=eclipsebtq.com --selector=default --directory=/etc/opendkim/keys/eclipsebtq.com
        PARSE => sudo -u opendkim cat /etc/opendkim/keys/eclipsebtq.com/default.txt
        # Possibly tab separated, dns prefix, type, parentheses includes multiple quoted strings to be concatenated into the dns record.
        # dkim setup currently a shell script, split into test/fix lines for python
        sudo sh setup_dkim.sh eclipsebtq.com
        '''

        '''
        # Test for using generic keys: /etc/ssl/certs/iRedMail.crt and /etc/ssl/private/iRedMail.key
        # On web server: sudo certbot certificates --domain sfu.silverfoxunlimited.com
        Look for:
        Found the following matching certs:
          Certificate Name: sfu.silverfoxunlimited.com-0002
            Serial Number: 555d2bc9e08ce7e14181b3d209a431b21a3
            Key Type: RSA
            Identifiers: sfu.silverfoxunlimited.com
            Expiry Date: 2026-10-08 00:55:06+00:00 (VALID: 72 days)
            Certificate Path: /etc/letsencrypt/live/sfu.silverfoxunlimited.com-0002/fullchain.pem
            Private Key Path: /etc/letsencrypt/live/sfu.silverfoxunlimited.com-0002/privkey.pem
            
            sudo tar -chf - -C /etc/letsencrypt/live/sfu.silverfoxunlimited.com-0002 fullchain.pem privkey.pem | ssh ritgrad10@sfu.local "cat > ~/certs.tar && tar -xf ~/certs.tar -C ~ && rm ~/certs.tar"
            
        # Now on email server:
        # Create the secure directory
        sudo mkdir -p /etc/postfix/ssl
        
        # Move the files from your home folder into place
        sudo mv ~/fullchain.pem ~/privkey.pem /etc/postfix/ssl/
        
        # Lock down permissions (600 means only root can read/write the private key)
        sudo chmod 600 /etc/postfix/ssl/privkey.pem
        sudo chmod 644 /etc/postfix/ssl/fullchain.pem
        sudo chown -R root:root /etc/postfix/ssl

        sudo postconf -e "smtpd_tls_cert_file = /etc/postfix/ssl/fullchain.pem"
        sudo postconf -e "smtpd_tls_key_file = /etc/postfix/ssl/privkey.pem"
        sudo postconf -e "smtp_tls_cert_file = /etc/postfix/ssl/fullchain.pem"
        sudo postconf -e "smtp_tls_key_file = /etc/postfix/ssl/privkey.pem"

        # Test email:
        sudo /usr/sbin/sendmail -f support@eclipsebtq.com steveb.27@outlook.com <<EOF
Subject: Direct Send Live Verification
From: support@eclipsebtq.com
To: steveb.27@outlook.com

This email was sent directly from our Ubuntu Postfix server without a relay.
EOF


        '''
        pass

    def _parse(self, output):
        config = {}

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)

            config[key.strip()] = value.strip()

        return config