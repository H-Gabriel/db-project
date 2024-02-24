import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from abstractions import Table, Bucket, BucketRef, max_bucket_size

app = Flask(__name__)
CORS(app)
load = open('words.txt', 'r')
load_size = len(load.readlines())
buckets = None
table = None
buckets_amount = 0

def init_buckets():
    global buckets, buckets_amount
    buckets_amount = math.ceil(load_size/max_bucket_size)
    buckets = [Bucket() for _ in range(buckets_amount)]

def hash_string(s):
    hash = 0
    for byte in [ord(char) for char in s]:
        hash = (31 * hash + byte) % buckets_amount
    return hash

@app.route('/config', methods=['POST'])
def config():
    global table

    data = request.get_json()
    table = Table(load_size, data['records_page'])
    table.load_pages(load)

    return jsonify({'message': 'Configurado com sucesso'})

@app.route('/fill-buckets', methods=['POST'])
def fill_buckets():
    colisions = 0
    overflows = 0
    init_buckets()

    for page_index, page in enumerate(table.pages):
        for line in page:
            i = hash_string(line)

            if len(buckets[i].refs) < max_bucket_size:
                buckets[i].refs.append(BucketRef(line, page_index))
            else:
                colisions += 1

                temp = buckets[i]
                while temp.overflow_ref is not None:
                    temp = temp.overflow_ref
                
                if len(temp.refs) < max_bucket_size:
                    temp.refs.append(BucketRef(line, page_index))
                else:
                    overflows += 1
                    temp.overflow_ref = Bucket()
                    temp.overflow_ref.refs.append(BucketRef(line, page_index))
                
    response_data = {
        'message': 'Buckets preenchidos com sucesso',
        'colisions': colisions,
        'overflows': overflows
    }
    
    return jsonify(response_data), 200

@app.route('/search', methods=['GET'])
def search():
    search = request.args.get('key')
    bucket_index = hash_string(search)
    search_bucket = buckets[bucket_index]

    while search_bucket is not None:
        for ref in search_bucket.refs:
            if ref.line == search:
                return jsonify({'result': f'A palavra se encontra na página {ref.page + 1}'})
        search_bucket = search_bucket.overflow_ref

    return jsonify({'result': 'A palavra não foi encontrada.'})

@app.route('/table-scan', methods=['GET'])
def table_scan():
    table_scan = []
    amount = int(request.args.get('amount'))

    for page in table.pages:
        for line in page:
            table_scan.append(line)
            amount -= 1
            if amount == 0:
                break
        if amount == 0:
            break

    return jsonify({"result": table_scan})

if __name__ == '__main__':
    app.run()