# BlockMesh Network Autoreferral Bot
Automatic referral script for BlockMesh Network Account using proxies.

# Installation
- Install Python For Windows: [Python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)
- For Unix:
```bash
apt install python3 python3-pip -y
```
- Install requirements, Windows:
```bash
pip install -r requirements.txt
```
- Unix:
```bash
pip3 install -r requirements.txt
```
### Run the Bot
- Replace the proxies example in ```proxies.txt``` to your own proxies with format:
```bash
http://host:port
http://user:pass@host:port
```
>only http proxies support for now, if you want to run without proxies, just remove proxies.txt content or delete proxies.txt
#### Run command:
- Windows:
```bash
python main.py
```
- Unix
```bash
python3 main.py
```
- Insert your full referral URL, example: ``https://app.blockmesh.xyz/register?invite_code=XXXXXXXXXX``
- Enter how many referrals you want
- Result account generated will be saved to ``accounts.txt``

### Source
https://github.com/im-hanzou
