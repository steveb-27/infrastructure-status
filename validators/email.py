from validator import Validator


class EmailValidator(Validator):

    name = "SMTP Server"

    def validate(self, context):
        # Check for mapped relayhost
        value_exp = False
        value_fnd = context.postfix.get('sender_dependent_relayhost_maps',False)
        context.add_result(
            validator=self.name,
            config="sender_dependent_relayhost_mapse",
            value_exp = value_exp,
            value_fnd = value_fnd,
            passes = value_exp == value_fnd
        )

        # Check for single relayhost
        value_exp = False
        value_fnd = context.postfix.get('relayhost', False)
        context.add_result(
            validator=self.name,
            config="relayhost",
            value_exp=value_exp,
            value_fnd=value_fnd,
            passes=value_exp == value_fnd
        )