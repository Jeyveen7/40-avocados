#!/bin/env python

# Generate 40 things.
# Vanessa Sochat @vsoch
# October 30, 2018
# Halloweenie!

import os
import requests
import sys
import yaml

## Helper Functions

def read_file(filename, mode="r", readlines=True):
    '''write_file will open a file, "filename" and write content, "content"
       and properly close the file
    '''
    with open(filename, mode) as filey:
        if readlines is True:
            content = filey.readlines()
        else:
            content = filey.read()
    return content


def write_file(filename, content, mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
       and properly close the file
    '''
    with open(filename, mode) as filey:
        filey.writelines(content)
    return filename


# Yaml

def read_yaml(filename, mode='r', quiet=False):
    '''read a yaml file, only including sections between dashes
    '''
    stream = read_file(filename, mode, readlines=False)
    return _read_yaml(stream, quiet=quiet)


def write_yaml(yaml_dict, filename, mode="w"):
    '''write a dictionary to yaml file
 
       Parameters
       ==========
       yaml_dict: the dict to print to yaml
       filename: the output file to write to
       pretty_print: if True, will use nicer formatting
    '''
    with open(filename, mode) as filey:
        filey.writelines(yaml.dump(yaml_dict))
    return filename

   
def _read_yaml(section, quiet=False):
    '''read yaml from a string, either read from file (read_frontmatter) or 
       from yml file proper (read_yaml)

       Parameters
       ==========
       section: a string of unparsed yaml content.
    '''
    metadata = {}
    docs = yaml.load_all(section)
    for doc in docs:
        if isinstance(doc, dict):
            for k,v in doc.items():
                if not quiet:
                    print('%s: %s' %(k,v))
                metadata[k] = v
    return metadata


## Generation

def generate_grid(image, url, number=40):
    '''generate the grid, meaning the grid-item classes to embed some
       number of times.

       Parameters
       ==========
       image: the image url to put in img src
       number: the number of grid-items to produce of the image
       url: the url for the grid-item to link to.
    '''
    element = '<div class="grid-item"><a href="%s"><img src="%s"/></a></div>\n'
    for iter in range(number):
        element += element
    return element

def generate_lookup(thing):
    '''convert of list of dicts to a single dict. I know, I know.
    '''
    lookup = dict()
    [lookup.update(item) for item in thing]
    return lookup


def generate_html(file_name, subs):
    '''write the grid html content to a file_name

       Parameters
       ==========
       file_name the name to write of the file, folder must exist
       subs: a dictionary of subs, where key is the template string, value 
             is the content to fill in.
    '''
    template = read_file('_template.html', readlines=False)
    for key, content in subs.items():
        template = template.replace("{{ %s }}" % key, content)

    # 5. Write template
    write_file(file_name, template)
    return file_name


def main(yaml_file, output_dir):

    # 1. Read in the things.yml file
    data = read_yaml(yaml_file)

    # 2. Generate a page per thing

    for name,thing in data['things'].items():

        print('Generating %s!' % name)
        thing = generate_lookup(thing)

        # 3. Metadata and Image
        number = int(thing.get("number", 40))

        # Number must be greater than or equal to 1
        number = max(number, 1)
        url = thing.get('url', "https://vsoch.github.io/40-avocados/")
        image = thing.get('image')

        # Test that image is defined
        if image is None:
            print('Missing image definition for %s in things.yml.' % name)
            sys.exit(1)

        # Test that image exists
        if requests.get(image).status_code != 200:
            print('Error with %s, image status not 200!.' % name)
            sys.exit(1)

        # 4. Fill Template
        grid = generate_grid(image, url, number)
        file_name = '%s/%s/index.html' % (output_dir, name.lower())
        os.mkdir(os.path.dirname(file_name))

        # 5. Write file
        generate_html(file_name, {"name": name,
                                  "grid": grid,
                                  "number": number}) 


    # Finally, an index.html. Redundant, yes, I'm tired
    grid = ''
    
    for name,thing in data['things'].items():
        url = "https://vsoch.github.io/40-avocados/%s" % name.lower()
        image = thing.get('image')
        grid += generate_grid(image, url, 1)

    generate_html('%s/index.html' % output_dir, {"grid": grid }) 


if __name__ == '__main__':

    # Hacky input parsing!
    yaml_file = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    main(yaml_file, output_dir)
