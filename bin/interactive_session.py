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
from rich.console import Console
from _genie_pdfs_ import PDF

console = Console(width=90)
# from _graph_node import Noder

def genieContext(exp_dict, default_sections):
    name = exp_dict.get('--name')
    home_dir = exp_dict.get('--home')
    output_path = home_dir+'/letters/'+name+'/'+name+'.txt'
    default_sections = default_sections[:]
    company_name = input('\nplease enter company name:\n')
    job_title= input('\nplease enter job title:\n')
    job_location = input('\nenter location:\n')
    global_group = dict(companyName=company_name, jobTitle=job_title, jobLocation=job_location)

    def clear_cover_letter():
        f = open(home_dir+"/letters/"+name+"/"+name+".txt", "w")
        f.close()

    def update_letter_section(var_dict, section):
        with open(home_dir+"/letters/"+name+"/"+section+".txt", "w+") as letter, open(home_dir+"/sections/"+section+"/boiler", 'r') as boiler:
            boiler_part = boiler.read()
            for custom_tag,custom_part in var_dict.items():
                boiler_part = boiler_part.replace(custom_tag,custom_part.rstrip('\n'))
            letter.write(boiler_part+'\n')

    def update_cover_letter(section):
        clear_cover_letter()
        index = default_sections.index(section)
        for sec in default_sections[:index+1]:
            with open(home_dir+"/letters/"+name+"/"+sec+".txt", 'r') as sectionfile, open(home_dir+"/letters/"+name+"/"+name+".txt", 'a') as letter:
                tmp = sectionfile.read()
                final_section = tmp.replace('_','')
                letter.write(final_section.format(company=company_name))

    def produce_pdf():
        update_cover_letter(default_sections[-1])
        pdf_filename = output_path[:-4]+'.pdf'
        pdf = PDF()
        pdf.generate_page(output_path)
        pdf.output(pdf_filename, 'F').encode('latin-1')
        os.system('open '+pdf_filename)

    def add_custom(name,choice_file, sentance_type):
        while True:
            sentance = input('\nENTER SENTANCE:\n')
            console.print("\nEnter [bold green]y[/bold green] to confirm or [bold bright_red]c[/bold bright_red] to cancel or [bold yellow]r[/bold yellow] to cancel:\n")
            if sentance_type == 'bullets':
                sentance = '* '+sentance
            console.print(sentance)
            console.print("\n")
            confirmation = input('> ')

            if confirmation == 'y':
                with open(home_dir + "/sections/" + name + "/" + choice_file, "a") as choice_group:
                    choice_group.write(sentance+'\n')
                return sentance

            elif confirmation == 'r':
                continue

            elif confirmation == 'c':
                console.print("\ncancelled custom sentance\n")
                break


    def readboiler(name):
        """ returns a dict of custom values  """
        dynamic_sentances=[]
        with open(name+'/boiler', 'r') as boiler_file:
            boiler = boiler_file.read()
            console.print("\n[italic yellow]Boiler for [bold yellow]" + name.upper() + "[/bold yellow] section:[/italic yellow]\n")
            console.print(boiler.replace('__','[bold red]').replace('_', '[/bold red]'))
            dynamic_sentances = re.findall(r"__([A-Za-z0-9\-:]+)_", boiler)

        custom_dict = {}
        for sentance_tag in dynamic_sentances:
            choice_file,sentance_type = sentance_tag.split(':')
            if choice_file in global_group.keys():
                custom_dict.update({sentance_tag:global_group.get(choice_file)})
                continue


            custom_part = ''
            with open(name+'/'+choice_file, 'r') as f:
                choice_list = [choice for choice in f.readlines()]
                prompt_bit = "Choose a"
                while True:
                    console.print('\n[italic green3]'+prompt_bit+' custom sentance[/italic green3] for '+'[bold red]'+choice_file+'[/bold red] tag:\n')

                    for key,choice in enumerate(choice_list, 1):
                        console.print(str(key)+' -> '+choice+'\n')

                    user_choice = input('> ')
                    user_choice = user_choice.rstrip(' ')

                    if user_choice == 'n':
                       break

                    if user_choice == 'other':
                        custom_sentance = add_custom(name,choice_file,sentance_type)
                        # in case user cancelled:
                        if len(custom_sentance) > 0:
                            if sentance_type == 'bullets':
                                custom_part = custom_part+' '+custom_sentance+'\n'
                            else:
                                custom_part = custom_part+' '+custom_sentance

                        if sentance_type == 'single':
                            break
                        continue

                    try:
                        if int(user_choice) == 0:
                            console.print('\n\n[bold red] ** CHOICE [bold blue]'+user_choice+'[/bold blue] NOT VALID ** [/bold red]')
                            continue
                        choice = choice_list.pop(int(user_choice)-1)

                    except (ValueError, IndexError) as e:
                        console.print('\n'+e+'\n')
                        console.print('\n\n[bold red] ** CHOICE [bold blue]'+user_choice+'[/bold blue] NOT VALID ** [/bold red]')

                    choice = choice.lstrip('0123456789')
                    if sentance_type == 'bullets':
                        custom_part = custom_part+' '+choice
                    elif sentance_type == 'sequence':
                        custom_part = custom_part + ' ' + choice.rstrip('\n')
                    else:
                        custom_part = custom_part + ' ' + choice.rstrip('\n')
                        break
                    # if no more choices then break
                    if not len(choice_list):
                        break

                    prompt_bit = "Choose [bold]ANOTHER[/bold]"

                custom_dict.update({sentance_tag:custom_part.lstrip(' ')})

        return custom_dict


    def genie_steps(cmd):

        def abstract_section(section):
            variable_dict = readboiler(section)
            update_letter_section(variable_dict, section)
            update_cover_letter(section)

        def generate_letter():
            produce_pdf()


        decorated_step = dict(abstract_section=abstract_section, generate_letter=generate_letter)
        return_function = decorated_step.get(cmd)
        return return_function

    return genie_steps


def main(interactive_dict):
    console.print(interactive_dict)
    os.chdir(str(interactive_dict.get('--home')) + '/sections')
    default_steps = ['intro', 'overview', 'janus', 'background', 'skills', 'summary']
    letter_context = genieContext(interactive_dict, default_steps)
    try:
        if input("enter 'print' to generate pdf, otherwise hit enter\n") == 'print':
            generate_letter = letter_context('generate_letter')
            generate_letter()
            return

        while default_steps:
            section_function = letter_context('abstract_section')
            section_function(default_steps.pop(0))

        generate_letter = letter_context('generate_letter')
        generate_letter()

    except (RuntimeError, TypeError, NameError, IndexError) as e:
        traceback.print_exc()
        console.print("error -> ", e)



if __name__ == '__main__':
    console.print(sys.argv)
    args = sys.argv[1:]
    i_dict = {args[x]: args[x + 1] for x in range(0, len(args) - 1) if x % 2 == 0}
    main(i_dict)
    sys.exit()

