from io import BytesIO
from random import choices
from string import ascii_letters, digits

from captcha.image import ImageCaptcha


def generate_random_chars(k=4):
    chars_choices = list(ascii_letters + digits)
    chars_choices.remove('0')
    chars_choices.remove('o')
    chars_choices.remove('O')
    random_chars = ''.join(choices(chars_choices, k=k))
    return random_chars


def get_captcha_io(random_chars):
    image = ImageCaptcha()
    captcha_io = BytesIO()
    image.write(random_chars, captcha_io)
    return captcha_io


if __name__ == '__main__':
    pass
    # get_captcha_io()
