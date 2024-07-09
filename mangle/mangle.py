import os
import shutil
import random
from PIL import Image, ImageFilter, ImageDraw

data_dir = os.fsencode("..")
blur_dir = os.fsencode("blurred")
dust_dir = os.fsencode("dusty")
dustyblur_dir = os.fsencode("dustyblurred")


blur_radius = [1, 2, 4, 6, 8]
dust_size = [2, 4, 8, 16, 24]
dust_colour = (0, 0, 0, 191)

dustyblurs = []
for i in blur_radius:
    for j in dust_size:
        dustyblurs.append((i, j))

for num in os.listdir(data_dir):
    if os.fsdecode(num)[0] == '.':
        continue

    if not os.fsdecode(num).startswith("veri_set_"):
        continue

    for i in blur_radius:
        if not os.path.exists(os.path.join(blur_dir, f"{i}".encode('utf-8'), num)):
            os.makedirs(os.path.join(blur_dir, f"{i}".encode('utf-8'), num))
    for i in dust_size:
        if not os.path.exists(os.path.join(dust_dir, f"{i}".encode('utf-8'), num)):
            os.makedirs(os.path.join(dust_dir, f"{i}".encode('utf-8'), num))

    for i in dustyblurs:
        if not os.path.exists(os.path.join(dustyblur_dir, f"{i[0]}+{i[1]}".encode('utf-8'), num)):
            os.makedirs(os.path.join(dustyblur_dir, f"{i[0]}+{i[1]}".encode('utf-8'), num))

    for img_file in os.listdir(os.path.join(data_dir, num)):
        if os.fsdecode(img_file)[0] == '.':
            continue

        if not os.fsdecode(img_file).lower().endswith(".jpg"):
            for i in blur_radius:
                shutil.copyfile(os.path.join(data_dir, num, img_file), os.path.join(blur_dir, f"{i}".encode('utf-8'), num, img_file))
            for i in dust_size:
                shutil.copyfile(os.path.join(data_dir, num, img_file), os.path.join(dust_dir, f"{i}".encode('utf-8'), num, img_file))
            for i in dustyblurs:
                shutil.copyfile(os.path.join(data_dir, num, img_file), os.path.join(dustyblur_dir, f"{i[0]}+{i[1]}".encode('utf-8'), num, img_file))
            continue

        filename = os.fsdecode(img_file)
        print(filename)
        img = Image.open(os.path.join(data_dir, num, img_file))

#        extend = 64
#        img_blur = Image.new('RGB', (img.width+extend, img.height+extend), (255, 255, 255))
#        img_blur.paste(img, (extend//2, extend//2))

        for i in blur_radius:
            img_blur = img.filter(ImageFilter.GaussianBlur(i))
            img_blur.save(os.path.join(blur_dir, f"{i}".encode('utf-8'), num, img_file))

        for i in dust_size:
            img_dust = img.copy()
            dust_pos = (random.randint(0, img.width-i-1), random.randint(0, img.height-i-1))
            draw = ImageDraw.Draw(img_dust, 'RGBA')
            draw.rectangle((dust_pos, (dust_pos[0]+i, dust_pos[1]+i)), fill=dust_colour)
            img_dust.save(os.path.join(dust_dir, f"{i}".encode('utf-8'), num, img_file))

        for i in dustyblurs:
            dust_pos = (random.randint(0, img.width-i[1]-1), random.randint(0, img.height-i[1]-1))
            img_dustyblur = img.filter(ImageFilter.GaussianBlur(i[0]))
            draw = ImageDraw.Draw(img_dustyblur, 'RGBA')
            draw.rectangle((dust_pos, (dust_pos[0]+i[1], dust_pos[1]+i[1])), fill=dust_colour)
            img_dustyblur.save(os.path.join(dustyblur_dir, f"{i[0]}+{i[1]}".encode('utf-8'), num, img_file))
