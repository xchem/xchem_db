import glob

str_out = ''
for f in glob.glob('./sql/*.sql'):
    to_add = open(f, 'r').read()
    str_out += to_add

with open('init.sql', 'w') as w:
    w.write(str_out)
