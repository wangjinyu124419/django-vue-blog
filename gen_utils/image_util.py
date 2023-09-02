import os
import uuid

from PIL import Image
from django.conf import settings
from lxml import etree


def resize_img(img_file_obj, resize=500):
    file_human_size = img_file_obj.size / 1024 / 1024
    uid = str(uuid.uuid1())
    img_name = uid + '.' + img_file_obj.name.split('.')[-1]
    img_path = os.path.join(settings.MEDIA_ROOT, img_name)
    url_path = os.path.join(settings.MEDIA_URL, img_name)
    im = Image.open(img_file_obj)

    width, height = im.width, im.height
    resize_width = int(resize / height * width)
    im_resized = im.resize((resize_width, resize))
    quality = int(min(1 / (file_human_size / 10), 1) * 95)
    if im.format == "GIF":
        with open(img_path, 'wb+') as f:
            for chunk in img_file_obj.chunks():
                f.write(chunk)
        os.system(f"convert {img_path} -resize {resize_width}x{resize} {img_path}")
        gif_watermark(img_path)
    else:
        if im_resized.mode == "RGBA":
            im_resized = im_resized.convert('RGB')
        im_resized.save(img_path, format='JPEG', quality=quality, optimize=True)
    return img_name, url_path


def fit_image(form):
    body = form.cleaned_data['body']
    selector = etree.HTML(body)
    imgs = selector.xpath('//p/img/@src')
    for i in range(0, len(imgs), 2):
        w1_path = os.path.join(settings.MEDIA_ROOT, imgs[i].split('/')[-1])
        w2_path = os.path.join(settings.MEDIA_ROOT, imgs[i + 1].split('/')[-1])
        im1 = Image.open(w1_path)
        w1, raw_h = im1.width, im1.height
        im2 = Image.open(w2_path)
        w2, raw_h = im2.width, im2.height

        new_height = int(raw_h * 1000 / (w1 + w2))
        new_w1 = int(new_height / raw_h * w1)
        new_w2 = 1000 - new_w1
        im1.resize((new_w1, new_height)).save(w1_path)
        im2.resize((new_w2, new_height)).save(w2_path)


# def gif_watermark_old(file_path):
#     # https://stackoverflow.com/a/51479982/9917670
#     im = Image.open(file_path)
#     W, H = im.width, im.height
#     font_path = os.path.join(settings.BASE_DIR, 'static', 'font', 'arial.ttf')
#
#     text_font = ImageFont.truetype(font_path, W // 20)
#     # text_font = ImageFont.truetype(font_path)
#     # A list of the frames to be outputted
#     frames = []
#     # Loop over each frame in the animated image
#     for frame in ImageSequence.Iterator(im):
#         # Draw the text on the frame
#         d = ImageDraw.Draw(frame)
#         d.text((W - 5, 5), "freeshare.blog", fill='red', anchor='rt', font=text_font)
#         # d.text((W-50,5), "freeshare.blog",fill='red')
#         del d
#         # However, 'frame' is still the animated image with many frames
#         # It has simply been seeked to a later frame
#         # For our list of frames, we only want the current frame
#         # Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
#         # To be efficient, we will save it to a stream, rather than to file
#         b = io.BytesIO()
#         frame.save(b, format="GIF")
#         frame = Image.open(b)
#         # Then append the single frame image to a list of frames
#         frames.append(frame)
#     # Save the frames as a new image
#     frames[0].save(file_path, save_all=True, append_images=frames[1:])

def gif_watermark(file_path):
    # font_path = PurePath(settings.BASE_DIR, 'static', 'font', 'arial.ttf')
    font_path = os.path.join(settings.BASE_DIR, 'static', 'font', 'ariblk.ttf')
    comand = f'ffmpeg -i {file_path} -vf "drawtext=fontfile={font_path}:text="freeshare.blog":fontcolor=red:fontsize=20:x=(w-text_w-5):y=5" -codec:a copy {file_path} -y'
    os.system(comand)
