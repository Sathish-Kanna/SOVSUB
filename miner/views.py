import json
from requests import post as request_post
from requests import get as request_get

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from appmain.models import KeyModel
from support.signature import verify
from support.blockchain_platform import Block
from support.blockchain_platform import Blockchain

app = __name__
# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()
trcr_ip = "127.0.0.1:8000"


# endpoint to submit a new transaction.
# This will be used by our application to add new data (posts) to the blockchain
# /new_transaction
@csrf_exempt
def set_new_transaction(request, *args, **kwargs):
    tx_data = request.POST
    required_fields = ["data", "signature"]

    for field in required_fields:
        if not tx_data.get(field):
            return HttpResponse("Invalid transaction data", 404)
    data = eval(tx_data.get('data'))
    signature = tx_data.get('signature')
    pukey = KeyModel.objects.get(temp_id=data.get('tempid')).__dict__.get("pukey")

    if verify(pukey, data, signature) and pukey:
        data["signature"] = signature
        blockchain.add_new_transaction(str(data))

        # remove the KeyModel of that voter so next time the user can't vote
        keymodel = KeyModel.objects.get(temp_id=data.get('tempid'))
        keymodel.delete()
        return HttpResponse("Success", 201)
    else:
        return HttpResponse("Unauthorized transaction data", 401)


# endpoint to submit a new transaction.
# This will be used by our application to add new data (posts) to the blockchain
# /update_transaction
@csrf_exempt
def update_transaction(request, *args, **kwargs):
    global peers
    if not peers:
        chain = request_post("http://" + trcr_ip + "/miner/chain/", data=request.POST).json()
        peers = set(chain['peers'])

    for peer in peers:
        request_post("http://" + peer + "/miner/new_transaction/", data=request.POST)
    return HttpResponse("Unauthorized transaction data", 200)


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query all the posts to display.
# /chain
@csrf_exempt
def get_chain(request, *args, **kwargs):
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    return HttpResponse(json.dumps({
        "length": len(chain_data),
        "chain": chain_data,
        "peers": list(peers)}))


# endpoint to request the node to mine the unconfirmed transactions (if any).
# We'll be using it to initiate a command to mine from our application itself.
# /mine
def mine_unconfirmed_transactions(request, *args, **kwargs):
    result = blockchain.mine()
    if not result:
        return HttpResponse("No transactions to mine")
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return HttpResponse("Block #{} is mined.".format(blockchain.last_block.height))


# endpoint to add new peers to the network.
# /register_node
@csrf_exempt
def register_new_peers(request, *args, **kwargs):
    node_address = request.POST.get("node_address")
    if not node_address:
        node_address = eval(request.body.decode("utf-8")).get("node_address")
        if not node_address:
            return HttpResponse("Invalid data", 400)

    # Add the node to the peer list
    peers.add(node_address)

    # Return the peers list to the newly registered node
    # so that he can sync
    return HttpResponse(json.dumps({"peers": list(peers)}))


# endpoint to add a block mined by someone else to the node's chain.
# The block is first verified by the node and then added to the chain.
# /add_block
@csrf_exempt
def verify_and_add_block(request, *args, **kwargs):
    if request.POST:
        block_data = request.POST
    else:
        block_data = eval(request.body.decode("utf-8"))
    block = Block(block_data["height"],
                  block_data["transactions"],
                  block_data["cumulated"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    for transaction in block.transactions:
        if transaction in blockchain.unconfirmed_transactions:
            blockchain.unconfirmed_transactions.remove(transaction)

    if not added:
        return HttpResponse("The block was discarded by the node", 400)

    return HttpResponse("Block added to the chain", 201)


# endpoint to query unconfirmed transactions
# /pending_tx
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def register_with_existing_node(request):
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    cn_adr = request.get("current_node_address")
    rwn_adr = request.get("register_with_node_address")

    data = {"node_address": cn_adr}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    url = "http://" + rwn_adr + "/miner/register_node/"
    response = request_post(url, data=json.dumps(data), headers=headers)

    rtn_response = {'status_code': response.status_code, 'content': "Registration successful"}

    if response.status_code == 200:
        global peers
        # update peers
        peers.add(rwn_adr)

        new_peers = set(json.loads(response.content)['peers']) - peers
        while new_peers:
            peer = new_peers.pop()
            url = "http://" + peer + "/miner/register_node/"
            response = request_post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                peers.add(peer)
                new_peers.update(set(json.loads(response.content)['peers']) - peers)
            else:
                rtn_response = {'node': peer, 'status_code': response.status_code, 'content': "Unsuccessful Registration"}
    else:
        # if something goes wrong, pass it on to the API response
        rtn_response = {'node': rwn_adr, 'status_code': response.status_code, 'content': "Unsuccessful Registration"}
    # update chain
    get_longest_chain()
    return rtn_response


def get_longest_chain():
    global blockchain
    response_chain = request_post("http://" + trcr_ip + "/miner/chain/").json()
    local_peers = set(response_chain['peers'])

    longest_chain = None
    current_len = len(blockchain.chain)
    for peer in local_peers:
        response = request_get("http://" + peer + "/miner/chain").json()
        response_len = response['length']
        response_chain = response['chain']
        if response_len > current_len and blockchain.check_chain_validity(response_chain):
            current_len = response_len
            longest_chain = response_chain
    if longest_chain:
        blockchain = Blockchain(longest_chain)
    return blockchain


def create_chain_from_dump(chain_dump):
    for idx, block_data in enumerate(chain_dump):
        if idx <= blockchain.last_block.height:
            continue  # skip genesis block
        block = Block(block_data["height"],
                      block_data["transactions"],
                      block_data["cumulated"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return blockchain


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain
    current_chain = blockchain.chain
    longest_chain = get_longest_chain()

    if len(longest_chain.chain) > len(current_chain):
        blockchain = Blockchain(longest_chain)
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "http://{}/miner/add_block/".format(peer)
        headers = {'Content-Type': "application/json"}
        request_post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)


def get_result():
    return get_longest_chain().last_block.cumulated


def get_all_transactions():
    transactions = []
    for block in get_longest_chain().chain:
        transactions.append(block.transactions)
    return transactions
