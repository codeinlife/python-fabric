#!/usr/local/bin/python3
# ........._\____
# ......../__|___\__
# .......(0)____(0)_\
'''
Developer: Mike LIM
File name: fabfile.py
Version : 2.5.3.0
Release Date: 07/2017
Last Update: 03/2020

Usage: fab [function:params]

Available commands:
	[DEPLOY]
	* deploy
		dp => fab dp:br=client-live,cl=linkID,cm='commit message',t=1(option)

	[SYNC]
	* pyo, pac7 (ev15 nad nc), and pac8

Updated:
	* removed pysftp module so now it can use fabric put operation (because no more a Windows OS) - 11/09/19
	* added EV1.5 function - 11/10/19
	* added EV1.5 file upload confirmation prompt - 11/11/19
    * added getpass: prompt password every time uploading files - 03/11/20 - commented for now
    * EV1.5 nc - file will be copied to direct servers - 03/18/20

SSH config file: ~/.ssh/config
# fabric ssh
Host ad30
    user xxxxxx
    hostname 172.31.100.115
    port 22
    IdentityFile ~/.ssh/id_rsa
    #ServerAliveCountMax 5
    #ServerAliveInterval 600
    TCPKeepAlive yes
'''

import os
import sys
import time
import warnings
import logging
import paramiko
from getpass import getpass
from fabric.api import env, sudo, task, local, run, put, lcd, cd
from inplayservers import get_server_information, get_all_link_id

logging.getLogger('paramiko.transport').addHandler(logging.StreamHandler())

# disable all warnings
warnings.filterwarnings('ignore')

# write paramiko log
# paramiko.util.log_to_file("/tmp/paramiko.log")

#########################################################################
##
# ENV VARIABLES: env - with host key
# check ~/.ssh/config
##
#########################################################################
env.use_ssh_config = True
env.hosts = ['ad30']
env.key_filename = '/Users/xxxxxx/.ssh/id_rsa'

#########################################################################
##
# BASE FOLDERS
##
#########################################################################
# local dir (check your local path)
GLOBAL_LOCAL_DIR = ''
GLOBAL_EV15_LOCAL_DIR = ''

# remote dir
NETCOMMERCE_REMOTE_DIR = ''
PAC_REMOTE_DIR = ''
PAC_REMOTE_STAGING_DIR = ''
EV15_REMOTE_DIR = ''

#########################################################################
##
# GET SERVERS
##
#########################################################################
@task
def get_servers(cl=None, o=None, c=None):
    '''
    => fab get_servers:cl=linkID,c=1 or o=1
    c=1 : just show the servers
    o=1 : show only one server
    '''
    evlist_full = []
    if not cl:
        print('fab get_servers:cl=linkID')
    else:
        try:
            evlist = get_server_information()[''+cl+'']
            for i in range(len(evlist)):
                evlist[i] = str(evlist[i])
                evlist_full.append(evlist[i])
            if c:
                print(evlist_full)
            elif o:
                return(evlist_full[0])
            else:
                return evlist_full
        except:
            pass

#########################################################################
##
# THIS FUNCTION WILL RETURN ALL UNTRACKED AND TRACKED FILES
##
#########################################################################
@task
def list_all_files(cl=None):
    '''
    => this will return both untracked and tracked files
    '''
    worked_files = []
    if cl is not None:
        with lcd(GLOBAL_LOCAL_DIR + '/%s' % cl):
            # new files
            untracked = local(
                'git ls-files -o --exclude-standard', capture=True)
            for untracked_line in untracked.splitlines():
                worked_files.append(untracked_line)

            # modified files
            tracked = local('git ls-files -m', capture=True)
            for tracked_line in tracked.splitlines():
                worked_files.append(tracked_line)
    else:
        with lcd(GLOBAL_EV15_LOCAL_DIR):
            # new files
            untracked = local(
                'git ls-files -o --exclude-standard', capture=True)
            for untracked_line in untracked.splitlines():
                worked_files.append(untracked_line)

            # modified files
            tracked = local('git ls-files -m', capture=True)
            for tracked_line in tracked.splitlines():
                worked_files.append(tracked_line)

    return worked_files

#########################################################################
##
# DEPLOY NETDESKTOP, NETMOBILE, PAC7
##
#########################################################################
@task
def dp(t=None, v=None, st=None, ss=None, **kwargs):
    '''
    [upload and deploy] => fab dp:params
        **kwargs - MUST have keywords cl, br, and cm
        * if you are using staging server then can pass the st as st=60 or st=57-59 for multiple servers
        * even st is true it does not support git commit and push for staging
        * ss - single server that can pass ss=41
    '''

    # variable declaration
    is_ev15_mode = False
    is_evpac7_mode = False

    # get length kwargs
    kwargsTotal = len(kwargs.keys())

    if kwargsTotal == 1:
        # will be ev1.5 mode
        is_ev15_mode = True

        if 'br' in kwargs and kwargs['br'] is not None:
            br = kwargs['br']
        else:
            print('br keyword does not exist!')
            sys.exit(0)

        if br != 'master':
            print('The branch is not a master!')
            sys.exit(0)
    elif kwargsTotal == 2:
        # will be legacy pac7 mode
        is_evpac7_mode = True

        # default commit None
        cm = None

        if 'cl' in kwargs and kwargs['cl'] is not None:
            cl = kwargs['cl']
        else:
            print('cl keyword does not exist!')
            sys.exit(0)

        if 'br' in kwargs and kwargs['br'] is not None:
            br = kwargs['br']
        else:
            print('br keyword does not exist!')
            sys.exit(0)
    elif kwargsTotal == 3:
        # will be legacy pac7 mode
        is_evpac7_mode = True

        if 'cl' in kwargs and kwargs['cl'] is not None:
            cl = kwargs['cl']
        else:
            print('cl keyword does not exist!')
            sys.exit(0)

        if 'br' in kwargs and kwargs['br'] is not None:
            br = kwargs['br']
        else:
            print('br keyword does not exist!')
            sys.exit(0)

        if 'cm' in kwargs and kwargs['cm'] is not None:
            cm = kwargs['cm']
        else:
            print('cm keyword does not exist!')
            sys.exit(0)

    # default True
    is_c_answer = True

    # line break
    line_break_1 = '-=' * 40
    line_break_2 = '-*' * 40

    if is_ev15_mode and br == 'master':
        # get all files that need to be uploaded
        get_files = list_all_files()

        is_ev15_nc_sync = False
        is_ev15_pac7_sync = False
        is_ev15_sync_process = False

        try:
            with lcd(GLOBAL_EV15_LOCAL_DIR):
                # check git status
                result = local('git status', capture=True)

                if v:
                    print(result)
                    print('\n')

                print(line_break_1)
                if t:
                    print(
                        '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')
                else:
                    if len(get_files) > 0:
                        print('\nEV1.5 UPLOADING ... \n')
                    else:
                        print('\nNO CHANGES ADDED TO COMMIT ... \n')
                print(line_break_1 + '\n')

                # check files
                for i in range(len(get_files)):
                    # variables
                    local_chk_files = get_files[i]
                    # local path - html and www [dekstop or mobile]
                    local_chk_dir = GLOBAL_EV15_LOCAL_DIR + '/' + local_chk_files
                    print(local_chk_dir + '\n')

                ev15_answer = input(
                    '\nAre those files you trying to upload? (y/n) ')
                if ev15_answer.lower() == 'n' or ev15_answer.upper() == 'N':
                    is_ev15_sync_process = False
                else:
                    is_ev15_sync_process = True

                if is_ev15_sync_process:
                    print('\n')
                    # upload files
                    for x in range(len(get_files)):
                        try:
                            # variables
                            local_files = get_files[x]
                            ev_nc_pac7 = local_files.split('/')[0]

                            # local path - EV1.5
                            local_dir = GLOBAL_EV15_LOCAL_DIR + '/' + local_files

                            if ev_nc_pac7 == 'pac7':  # remote path - pac7
                                remote_dir = EV15_REMOTE_DIR + local_files

                                # sync EV1.5 pac7
                                is_ev15_pac7_sync = True

                                if t:
                                    print('%s \n     => %s \n' %
                                          (local_dir, remote_dir))
                                else:
                                    put(local_dir, remote_dir)
                                    print('\n')
                            elif ev_nc_pac7 == 'nc':  # remote path - nc
                                remote_dir = EV15_REMOTE_DIR + local_files
                                ev_nc_client = local_files.split('/')[3]
                                remote_nc_files = '/'.join(
                                    local_files.split('/')[4:])

                                # sync EV1.5 nc - copy files to direct servers so no need to sync
                                is_ev15_nc_sync = False

                                # get servers
                                if ev_nc_client == 'test12-80':
                                    servers = ['ev243']
                                else:
                                    servers = get_servers(ev_nc_client)

                                for y in range(len(servers)):
                                    remote_dir = NETCOMMERCE_REMOTE_DIR + \
                                        '/%s' % servers[y] + '/html/evenue15/custom' + \
                                        '/%s' % ev_nc_client + '/' + remote_nc_files

                                    if t:
                                        print('%s \n     => %s \n' %
                                              (local_dir, remote_dir))
                                    else:
                                        put(local_dir, remote_dir)
                                        print('\n')
                        except Exception as e:
                            print('\nEV1.5 error ...')
                            print(e)
                print(line_break_1)

                # sync EV1.5 pac7
                if is_ev15_pac7_sync:
                    print(line_break_2)
                    if t:
                        print(
                            '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')
                    else:
                        print('\nEV1.5 PAC7 SYNCING ... \n')
                    print(line_break_2 + '\n')

                    if t:
                        print('/home/webdev/scripts/p7sync master prod \n')
                    else:
                        print('/home/webdev/scripts/p7sync master prod \n')
                        with cd('/home/webdev'):
                            run('p7sync master prod')
                    print('\n')

                # sync EV1.5 nc
                if is_ev15_nc_sync:
                    print(line_break_2)
                    if t:
                        print(
                            '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')
                    else:
                        print('\nEV1.5 NC SYNCING ... \n')
                    print(line_break_2 + '\n')

                    if t:
                        print(
                            '/home/webdev/scripts/ev15sync master prod %s \n' % ev_nc_client)
                    else:
                        print(
                            '/home/webdev/scripts/ev15sync master prod %s \n' % ev_nc_client)
                        run('/home/webdev/scripts/ev15sync master prod %s' %
                            ev_nc_client)
                    print('\n')
                print(line_break_2)
        except Exception as e:
            print('\nOops ...')
            print(e)
    elif is_evpac7_mode and not cm:
        # will have the play server(s) manually
        # can be used for staging server as well - be careful for the live pac7 remote server
        if st:
            evlist_passed = []
            # python 3 - use 'list' in order to map a list
            evlist_passed = list(map('ev{0}'.format, st.split('-')))
            servers = evlist_passed
        elif ss:
            one_server_passed = []
            one_server_passed = list(map('ev{0}'.format, ss.split('-')))
            servers = one_server_passed
        else:
            # get all in play servers
            servers = get_servers(cl)

        # print(servers)
        # get all files that need to be uploaded
        get_files = list_all_files(cl)

        # pac7 sync default False
        is_pac7_sync = False

        # default false
        is_folder_error = False
        is_non_ev15_sync_process = False

        # upload files
        if not (cl and br):
            print('Usage: fab dp:br=client-live,cl=linkID')
        else:
            try:
                with lcd(GLOBAL_LOCAL_DIR + '/%s' % cl):
                    # check git status
                    result = local('git status', capture=True)

                    if v:
                        print(result)
                        print('\n')

                    if 'On branch client-live' not in result.stdout:
                        c_answer = input(
                            '\nYour branch is not a client-live. Do you want to upload files? (y/n) ')
                        if c_answer.lower() == 'n' or c_answer.upper() == 'N':
                            is_c_answer = False
                        else:
                            is_c_answer = True
                    else:
                        if br != 'client-live':
                            print(
                                '\nI think there is a typo in branch name ... please check!\n')
                            sys.exit(0)

                    if is_c_answer:
                        print(line_break_1)
                        if t:
                            print(
                                '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')
                        else:
                            if len(get_files) > 0:
                                print('\nUPLOADING ... \n')
                            else:
                                print('\nNO CHANGES ADDED TO COMMIT ... \n')
                        print(line_break_1 + '\n')

                        # check files
                        for i in range(len(get_files)):
                            # variables
                            local_chk_files = get_files[i]
                            # local path - html and www [dekstop or mobile]
                            local_chk_dir = GLOBAL_LOCAL_DIR + '/%s' % cl + '/' + local_chk_files
                            print(local_chk_dir + '\n')

                        non_ev15_answer = input(
                            '\nAre those files you trying to upload? (y/n) ')
                        if non_ev15_answer.lower() == 'n' or non_ev15_answer.upper() == 'N':
                            is_non_ev15_sync_process = False
                        else:
                            is_non_ev15_sync_process = True

                        # get password from user
                        # env.password = getpass('Enter the password for %s: ' % env.hosts[0])

                        if is_non_ev15_sync_process:
                            print('\n')
                            # upload files
                            for x in range(len(get_files)):
                                try:
                                    # variables
                                    local_files = get_files[x]
                                    remote_files = '/'.join(
                                        local_files.split('/')[2:])
                                    remote_pac7_files = '/'.join(
                                        local_files.split('/')[1:])
                                    dt_mb = local_files.split('/')[0]
                                    html_www = local_files.split('/')[1]

                                    # local path - html and www [dekstop or mobile]
                                    local_dir = GLOBAL_LOCAL_DIR + '/%s' % cl + '/' + local_files

                                    # remote path - html and www [dekstop or mobile]
                                    if dt_mb == 'netMobile' or dt_mb == 'netDesktop':
                                        for y in range(len(servers)):
                                            if dt_mb == 'netMobile':
                                                remote_dir = NETCOMMERCE_REMOTE_DIR + \
                                                    '/%s' % servers[y] + '/' + html_www + \
                                                    '/linkID=m-' + '%s' % cl + '/' + remote_files
                                            elif dt_mb == 'netDesktop':
                                                remote_dir = NETCOMMERCE_REMOTE_DIR + \
                                                    '/%s' % servers[y] + '/' + html_www + \
                                                    '/linkID=' + '%s' % cl + '/' + remote_files

                                            if t:
                                                print('%s \n     => %s \n' %
                                                      (local_dir, remote_dir))
                                            else:
                                                put(local_dir, remote_dir)
                                                print('\n')
                                    # remote path - pac7
                                    elif dt_mb == 'pac7.2':
                                        # if st is true then will copy files to staging folder
                                        if st:
                                            remote_dir = PAC_REMOTE_STAGING_DIR + '%s' % cl + '/' + remote_pac7_files
                                        else:
                                            remote_dir = PAC_REMOTE_DIR + '%s' % cl + '/' + remote_pac7_files
                                        is_pac7_sync = True

                                        if t:
                                            print('%s \n     => %s \n' %
                                                  (local_dir, remote_dir))
                                        else:
                                            put(local_dir, remote_dir)
                                            print('\n')
                                except:
                                    # will throw an error if the folder does not exist
                                    is_folder_error = True
                                    print('ERROR! - need to create folder(s) manually first on remote server\n     >> ' +
                                          os.path.basename(os.path.dirname(remote_dir)) + '\n')
                                    pass
                        print(line_break_1)

                        # sync
                        if is_pac7_sync and not is_folder_error:
                            print(line_break_2)
                            if t:
                                print(
                                    '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')
                            else:
                                print('\nSYNCING ... \n')
                            print(line_break_2 + '\n')

                            # if st is true then will sync the staging folder
                            if t:
                                if st:
                                    print(
                                        '/home/webdev/scripts/rsync-customize-stg ev_%s \n' % cl)
                                else:
                                    print(
                                        '/home/webdev/scripts/rsync-evenue7.2 ev_%s \n' % cl)
                            else:
                                if st:
                                    print(
                                        '/home/webdev/scripts/rsync-customize-stg ev_%s \n' % cl)
                                    run('/home/webdev/scripts/rsync-customize-stg ev_%s' % cl)
                                else:
                                    print(
                                        '/home/webdev/scripts/rsync-evenue7.2 ev_%s \n' % cl)
                                    run('/home/webdev/scripts/rsync-evenue7.2 ev_%s' % cl)
                            print('\n')
                        print(line_break_2)
            except Exception as e:
                print('\nOops ...')
                print(e)
    elif is_evpac7_mode and cm:
        # deploy to bitbucket
        if not (cl and br and cm):
            print(
                "Usage: fab dp:br=client-live,cl=linkID,cm='cc#123456 - updated cart banner'")
        else:
            try:
                with lcd(GLOBAL_LOCAL_DIR + '/%s' % cl):
                    # check git status
                    result = local('git status', capture=True)
                    print('\n')

                    if v:
                        print(result)
                        print('\n')

                    if 'On branch client-live' not in result.stdout:
                        c_answer = input(
                            '\nYour branch is not a client-live. Do you want to deploy? (y/n) ')
                        if c_answer.lower() == 'n' or c_answer.upper() == 'N':
                            is_c_answer = False
                        else:
                            is_c_answer = True
                    else:
                        if br != 'client-live':
                            print(
                                '\nI think there is a typo in branch name ... please check!\n')
                            sys.exit(0)

                    if is_c_answer:
                        print(line_break_2)
                        if t:
                            print(
                                '\nWARNING! --- THIS IS NOT IN TASK --- THIS IS NOT IN TASK --- WARNING! \n')

                        print('\nPrepare to commit (net commerce) %s \n' % cl)
                        print(line_break_2)
                        time.sleep(0.2)

                        # commit
                        if t:
                            if br == 'client-live':
                                print('git stash')
                                print('git pull origin %s' % br)
                                print('git stash pop')

                            print('git add .')
                            print('git commit -m "%s"' % cm)
                            print('git push origin %s \n' % br)
                        else:
                            if br == 'client-live':
                                local('git stash')
                                local('git pull origin %s' % br)
                                local('git stash pop')

                            local('git add .')
                            local('git commit -m "%s"' % cm)
                            local('git push origin %s' % br)
                            print('\n')
                        print(line_break_2)
            except Exception as e:
                print('\nOops ...')
                print(e)

#########################################################################
##
# SYNC PYO
##
#########################################################################
@task
def syncpyo(acctid=None):
    '''
    [sync pyo] => fab syncpyo:params
    '''
    if not acctid:
        print('Usage: fab syncpyo:acctid=dataAccountID')
    else:
        # sync
        print('\n\n')
        print('Prepare to sync ... %s' % acctid)
        time.sleep(0.2)
        print('/home/webdev/scripts/rsync-seatmap-v3 %s' % acctid)
        run('/home/webdev/scripts/rsync-seatmap-v3 %s' % acctid)
        print('\n\n')

#########################################################################
##
# SYNC EV1.5, NonEV1.5, and Pac8
##
#########################################################################
@task
def syncpac7(cl=None):
    '''
    [sync pac7] => fab syncpac7 or syncpac7:cl=linkID
    '''
    if not cl:
        print('\n\n')
        print('Prepare to sync ... \n')
        time.sleep(0.2)
        print('/home/webdev/scripts/p7sync master prod \n')
        run('/home/webdev/scripts/p7sync master prod')
        print('\n\n')
    else:
        print('\n\n')
        print('Prepare to sync ... %s \n' % cl)
        time.sleep(0.2)
        print('/home/webdev/scripts/rsync-evenue7.2 ev_%s \n' % cl)
        run('/home/webdev/scripts/rsync-evenue7.2 ev_%s' % cl)
        print('\n\n')


@task
def syncnc(cl=None):
    '''
    [sync nc] => fab syncnc:params
    '''
    if not cl:
        print('Usage: fab syncnc:cl=linkID')
    else:
        # sync
        print('\n\n')
        print('Prepare to sync ... \n' % cl)
        time.sleep(0.2)
        print('/home/webdev/scripts/ev15sync master prod %s \n' % cl)
        run('/home/webdev/scripts/ev15sync master prod %s' % cl)
        print('\n\n')


@task
def syncpac8(cl=None):
    '''
    [sync pac8] => fab syncpac8:params
    '''
    if not cl:
        print('Usage: fab syncpac8:cl=linkID')
    else:
        # sync
        print('\n\n')
        print('Prepare to sync ... %s \n' % cl)
        time.sleep(0.2)
        print('/home/webdev/scripts/rsync-pac8 ev_%s \n' % cl)
        run('/home/webdev/scripts/rsync-pac8 ev_%s' % cl)
        print('\n\n')
