from django.utils.crypto import get_random_string


def create_activation_code(order):
    order.activation_code = get_random_string(10)
    order.save()
