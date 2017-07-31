import shelve

newdb = shelve.open('bd.dbm')
olddb = shelve.open('relation.dbm')

group = {}
for key in olddb:
    group['id{:0>3}'.format(key)] = olddb[key]

print group

newdb['IS-62'] = group

newdb.close()
