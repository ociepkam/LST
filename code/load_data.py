import codecs
import yaml
import os
import random
import re
from psychopy import visual


def load_config():
    try:
        with open(os.path.join("config.yaml"), encoding='utf8') as yaml_file:
            doc = yaml.safe_load(yaml_file)
        return doc
    except:
        raise Exception("Can't load config file")


def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert: dynamically generated info
    :return: message
    """
    if not isinstance(file_name, str):
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def load_images(session, randomize):
    training_image = os.listdir(os.path.join("images", "training"))
    experimental_images = [elem for elem in os.listdir(os.path.join("images", "experiment"))
                           if elem.split(".")[0].split("_")[1] == str(session)]

    def my_digit_sort(my_list):
        return list(map(int, re.findall(r'\d+', my_list)))[0]

    experimental_images.sort(key=my_digit_sort)

    if randomize:
        random.shuffle(training_image)
        random.shuffle(experimental_images)

    return training_image, experimental_images


def prepare_block_stimulus(images, win, config, folder):
    result = []
    for image in images:
        stim = visual.image.ImageStim(win=win, image=os.path.join("images", folder, image), pos=config["stimulus_pos"],
                                      size=config["stimulus_size"], interpolate=True)
        if image.find("_") != -1:
            image_id = int(image.split("_")[0])
        else:
            image_id = int(image.split(".")[0])
        result.append({"image_ID": image_id,
                       "stimulus": stim,
                       "image_name": image})
    return result
