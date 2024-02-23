import math
from abstractions import Table, Bucket, BucketRef, bucket_size

colisions = 0
overflows = 0

with open('words.txt', 'r') as load:
    load_size = len(load.readlines())
    buckets_amount = math.ceil(load_size/bucket_size)
    buckets = [Bucket() for _ in range(buckets_amount)]
    table = Table(load_size, int(input("Quantidade de registros por página: ")))
    table.load_pages(load)

def hash_string(s):
    hash = 0
    for byte in [ord(char) for char in s]:
        hash = (31 * hash + byte) % buckets_amount
    return hash

for p in range(table.pages_amount):
    for line in table.pages[p]:
        i = hash_string(line)
        if len(buckets[i].refs) < bucket_size:
            buckets[i].refs.append(BucketRef(line, p))
        else:
            colisions += 1

            temp = buckets[i]
            while temp.overflow_ref != None:
                temp = temp.overflow_ref
            
            if len(temp.refs) < bucket_size:
                temp.refs.append(BucketRef(line, p))
            else:
                overflows += 1
                temp.overflow_ref = Bucket()
                temp.overflow_ref.refs.append(BucketRef(line, p))

print("Quantidade de colisões:", colisions)
print("Quantidade de overflows:", overflows)

# Funcionalidade de busca
search = input("Pesquise uma palavra: ")
bucket_index = hash_string(search)
search_bucket = buckets[bucket_index]

found = False
while search_bucket != None:
    for ref in search_bucket.refs:
        if ref.line == search:
            print("A palavra se encontra na página", ref.page + 1)
            found = True
            break
    if found:
        break
    search_bucket = search_bucket.overflow_ref