
"""

    Created on Monday, January 24 2022  15:37:54 
    
    @author: Dieuveille BOUSSA ELLENGA
    
"""


from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils import six
import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
account_activation_token = TokenGenerator()