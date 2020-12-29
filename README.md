# SOVSUB
A blockchain application developed for secure online voting system in python.

## Instructions to run
Clone the project,

```sh
$ git clone https://github.com/Sathish-Kanna/SOVSUB.git
```

Install the dependencies,

```sh
$ cd SOVSUB
$ pip install -r requirements.txt
```

Start a blockchain node server,

```sh
# 
$ python manage.py runserver
```

the first instance of our application is now up 
and running at port 8000.

Here are a few screenshots

1. casting vote

![image.png](https://github.com/Sathish-Kanna/SOVSUB/raw/master/screenshots/1.png)

2. Requesting the node to mine

![image.png](https://github.com/Sathish-Kanna/SOVSUB/raw/master/screenshots/2.png)

3. Resyncing with the chain for updated data

![image.png](https://github.com/Sathish-Kanna/SOVSUB/raw/master/screenshots/3.png)

To register multiple nodes use `miner/register_with/` 
endpoint to register a new node. 

Here's a sample scenario that you might wanna try,

```sh
# Make sure you have nodes up by start the server
# in specific domain 
$ python manage.py runserver 127.0.0.1:8000
# spinning up new nodes
$ python manage.py runserver 127.0.0.1:8001
$ python manage.py runserver 127.0.0.1:8002
```

You can use the following cURL requests to register
the nodes with the already registered nodes.

```sh
curl -X POST \
  http://127.0.0.1:8001/reg \
  -H 'Content-Type: application/json' \
  -d '{"register_with_node": "127.0.0.1:8001","node_address": "127.0.0.1:8001"}'
```
```sh
curl -X POST \
  http://127.0.0.1:8002/reg \
  -H 'Content-Type: application/json' \
  -d '{"register_with_node": "127.0.0.1:8001", "node_address": "127.0.0.1:8002"}'
```
```sh
curl -X POST \
  http://127.0.0.1:8003/reg \
  -H 'Content-Type: application/json' \
  -d '{"register_with_node": "127.0.0.1:8002", "node_address": "127.0.0.1:8003"}'
```

By this the node at "node_address" is registered 
with "register_with_node" and other registered nodes
of "register_with_node".

Once you do all this, you can run the application,
create transactions (cast vote via the web inteface),
and once you mine the transactions, all the nodes
in the network will update the chain. The chain of 
the nodes can also be inspected by inovking 
`/miner/chain` endpoint using cURL.

```sh
$ curl -X GET http://localhost:8001/miner/chain
$ curl -X GET http://localhost:8002/miner/chain
```
