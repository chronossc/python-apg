# coding: utf-8

# This module provide a simple api do Automated Password Generator - http://www.adel.nursat.kz/apg/

import os, string, time, subprocess, datetime

# Check possible paths
APG_BIN_PATHS = ['/usr/bin/apg']
APG_BIN = None

if 'APG_BIN_PATH' in os.environ:
    apgbin = os.environ['APG_BIN_PATH']
    if not os.path.isfile(apgbin):
        raise ImproperlyConfigured,u"Please, fix your APG_BIN_PATH, %s isn't a valid file." % apgbin
    elif not os.access(apgbin,os.X_OK):
        raise ImproperlyConfigured,u"Please, fix your APG_BIN_PATH file, %s isn't executable." % apgbin
    else:
        APG_BIN = apgbin
else:
    for apgbin in APG_BIN_PATHS:
        if os.path.isfile(apgbin) and os.access(apgbin,os.X_OK):
            APG_BIN = apgbin
            break

if APG_BIN is None:
    raise ImproperlyConfigured,u"Please, install APG or set environment variable APG_BIN_PATH. None of prefedined apg paths can be found."

DEFAULT_APG_KWARGS = {
    'modes': 'sCN',
    'exclude_chars': string.punctuation, # only for username
    'algorithm': 'pronounceable',
    'number_of_passwords': 5,
    'min_size': 8,
    'seed':'',
}
def escape_to_bash(s):
    return s.replace("!","\!").replace('"','\\"').replace("`","\`")

def create_apg_passwords(**kwargs):
    """
    A wrapper to call apg.
    @modes = See modes in "man apg", default 'sCN'
    @algorithm = random or pronounceable, default pronounceable
    @number_of_passwords = number of passwords to generate, can be slow after 500, default 5
    @min_size = minimal size for passwords, default 8
    @seed = Custom seed, it will be appended with number of secods from Epoch, even if is blank string
    @exclude_chars = You can set a number of chars to avoid in passwords
    """
    params = DEFAULT_APG_KWARGS.copy()
    params.update(kwargs)

    cmd_entries = [APG_BIN,"-q"]

    if params['modes']:
        cmd_entries.append("-M %s" % params['modes'].replace("!","\!").replace('"','\"').replace("`","\`"))

    if params['algorithm']:
        if params['algorithm'] == 'pronounceable':
            cmd_entries.append("-a 1")
        elif params['algorithm'] == 'random':
            cmd_entries.append("-a 0")
        else:
            raise Warning,u"create_apg_passwords: Unknow algorithm parameter, using default (pronounceable)."

    if params['number_of_passwords']:

        try:
            int(params['number_of_passwords'])
        except ValueError:
            params['number_of_passwords'] = 1
            raise Warning,u"create_apg_passwords: number_of_passwords isn't a integer, assuming 1 as value."

        if int(params['number_of_passwords']) < 1:
            params['number_of_passwords'] = 1
            raise Warning,u"create_apg_passwords: number_of_passwords is less than 1, assuming 1 as value."

        cmd_entries.append("-n %s" % int(params['number_of_passwords']))

    if params['min_size']:

        try:
            int(params['min_size'])
        except ValueError:
            params['min_size'] = 8
            raise Warning,u"create_apg_passwords: min_size isn't a integer, assuming 8 as value."

        if int(params['min_size']) < 1:
            params['min_size'] = 8
            raise Warning,u"create_apg_passwords: min_size is less than 1, assuming 8 as value."

        cmd_entries.append("-m %s" % int(params['min_size']))

    if params['exclude_chars']:
        # escape characters that can break bash command
        cmd_entries.append(" -E \"%s\"" % escape_to_bash(params['exclude_chars']))

    seed = params.get('seed','')+str(time.time())
    cmd_entries.append("-c \"%s\"" % escape_to_bash(seed))

    n = datetime.datetime.now
    s = n()
    pwds = subprocess.check_output(u' '.join(cmd_entries),shell=True)[:-1].split('\n')
    print n() - s
    return pwds

def create_apg_usernames(size=8,number_of_usernames=1,seed=''):
    """
    A wrapper to pass excluded names for username
    """
    return create_apg_passwords(exclude_chars=string.punctuation,size=8,number_of_passwords=number_of_usernames,seed=seed)

if __name__ == '__main__':
    print create_apg_passwords(number_of_passwords=10)
    print create_apg_usernames(number_of_usernames=10,seed='philipe.rp@gmail.com')