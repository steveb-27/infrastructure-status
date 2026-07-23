from validator import Validator


class EmailValidator(Validator):

    name = "SMTP Server"

    def validate(self, context):
        relay = context.postfix.get('sender_dependent_relayhost_maps',False) or context.postfix.get('relayhost',False)

        if relay:
            outcome = 'Fail'
        else:
            outcome = 'Pass'

        context.add_result(
            validator = self.name,
            config = "Email uses relay service",
            value = relay,
            outcome = outcome
        )