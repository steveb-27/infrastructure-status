class Context:

    def __init__(self):
        """Initialize properties that can be written to"""
        self.certificates = []
        self.domains = []
        self.public_ip = None
        self.smtp_hostname = None
        self.postfix = None
        self.nginx_sites = []
        self.bunnycdn_pull_zone = []

        self.results = []

    def add_result(self, validator, config, value_exp, value_fnd, passes):
        """Helper to append a structured tuple to the log."""
        self.results.append({
            'validator':        validator,
            'config':           config,
            'value_exp':        value_exp,
            'value_fnd':        value_fnd,
            'passes':           passes,
        })