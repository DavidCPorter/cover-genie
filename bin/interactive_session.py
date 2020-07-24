import pdb
import traceback
import pip
import sys
import os
import subprocess
# import _ssh_import as ssh_import
from typing import Set
# from itertools import permutations
import yaml
# from collections import OrderedDict
from jinja2 import Template
import re
# from _graph_node import Noder


def genieContext(exp_dict, default_sections):
    name = exp_dict.get('--name')
    home_dir = exp_dict.get('--home')
    default_sections = default_sections[:]
    company_name = input('please enter company name:\n')
    job_title= input('please enter job title:\n')
    job_location = input('enter location:\n')
    global_group = dict(company_name=company_name, job_title=job_title, job_location=job_location)

    def clear_cover_letter():
        f = open(home_dir+"/letters/"+name+"/"+name+".txt", "w")
        f.close()

    def update_letter_section(var_dict, section):
        with open(home_dir+"/letters/"+name+"/"+section+".txt", "w+") as letter, open(home_dir+"/sections/"+section+"/boiler", 'r') as boiler:
            boiler_part = boiler.read()
            for custom_tag,custom_part in var_dict.items():
                boiler_part = boiler_part.replace(custom_tag,custom_part)
            letter.write(boiler_part)

    def update_cover_letter(section):
        clear_cover_letter()
        index = default_sections.index(section)
        for sec in default_sections[:index]:
            with open(home_dir+"/letters/"+name+"/"+sec+".txt", 'r') as sectionfile, open(home_dir+"/letters/"+name+"/"+name+".txt", 'a') as letter:
                letter.write(sectionfile.read())

    def produce_pdf():
        with open(home_dir+"/letters/"+name+"/"+name+".txt") as file_:
            template = Template(file_.read())
        template = template.render( )

        with open(home_dir+"/letters/"+name+"/"+name+".txt", "w") as letter:
            letter.write(template)

    def readboiler(name):
        """ returns a dict of custom values  """
        dynamic_sentances=[]
        with open(name+'/boiler', 'r') as boiler:
            section = boiler.read()
            print(section)
            dynamic_sentances = re.findall(r"\[([A-Za-z0-9_:]+)\]", section)

        custom_dict = {}
        for sentance_tag in dynamic_sentances:
            choice_file,sentance_type = sentance_tag.split(':')
            if choice_file in global_group.keys():
                custom_dict.update({sentance_tag:global_group.get(choice_file)})
                continue

            custom_part = ''
            with open(name+'/'+choice_file, 'r') as f:
                choice_list = [str(count) + ' -> ' + choice for count, choice in enumerate(f.readlines(), 0)]
                while sentance_type != 'exit':
                    print(choice_list)
                    user_choice = input('> ')
                    user_choice.split()
                    user_choice.replace('  ', ' ')
                    if user_choice == 'done':
                        sentance_type = 'exit'
                        continue

                    choice = choice_list[int(user_choice)]
                    choice = choice.lstrip('0123456789 ->')
                    custom_part = custom_part+' '+choice
                    if sentance_type == 'single':
                        break

                custom_dict.update({sentance_tag:custom_part})

        return custom_dict


    def genie_steps(cmd):

        def abstract_section(section):
            variable_dict = readboiler(section)
            update_letter_section(variable_dict, section)
            update_cover_letter(section)
            pdb.set_trace()


        decorated_step = dict(abstract_section=abstract_section)
        return_function = decorated_step.get(cmd)
        return return_function

    return genie_steps


def main(interactive_dict):
    print(interactive_dict)
    os.chdir(str(interactive_dict.get('--home')) + '/sections')
    default_steps = ['intro', 'overview', 'janus', 'background', 'skills', 'summary']
    letter_context = genieContext(interactive_dict, default_steps)
    try:
        while default_steps:
            section_function = letter_context('abstract_section')
            section_function(default_steps.pop(0))

        produce_pdf(interactive_dict.get('--name'))

    except (RuntimeError, TypeError, NameError, IndexError) as e:
        traceback.print_exc()
        print("error -> ", e)



if __name__ == '__main__':
    print(sys.argv)
    args = sys.argv[1:]
    i_dict = {args[x]: args[x + 1] for x in range(0, len(args) - 1) if x % 2 == 0}
    main(i_dict)
    sys.exit()

