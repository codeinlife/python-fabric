#!/usr/local/bin/python3
# ........._\____
# ......../__|___\__
# .......(0)____(0)_\
import sys
import pip
from subprocess import call


'''
Developer: Mike LIM - 10/2017 - setup.py - Version: 1.0.0

Desciprtion: This script will install all modules and packages dependencies as well for webdev automation tool

Usage: python setup.py
'''


def install_packages(requirements):
    return_value = call([sys.executable, '-m', 'pip',
                         'install', '-r', requirements, '--user'])
    if return_value is not 0:
        raise Exception('Unable to install one or more packages')


def setup(name, requirements):
    try:
        print('\n#--------------------- ' + name + ' ---------------------#\n')
        print('\nInstalling packages\n')
        print('\n#--------------------- ' + name + ' ---------------------#\n')
        install_packages(requirements)
        print('\n#--------------------- ' + name + ' ---------------------#\n')
        print('\nInstalling packages are done\n')
        print('\n#--------------------- ' + name + ' ---------------------#\n')
    except Exception as inst:
        print('The following error ocurred: ' + str(inst))


if __name__ == "__main__":
    setup('webdev_automation', 'requirements.dsl')