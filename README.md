# MISP bulk tag

## Description

This script performs bulk tagging operations over MISP.

## Setup

- `git clone https://github.intra.cert.corp/morallo/misp-bulk-tag`
- Create a file "keys.py" with the following content:
```
misp_url = 'https://<your_misp_url>'
misp_key = '<your_misp_API_key>'
```

TODO: use ~/.misp_api_key

## Usage

```
$ ./misp_bulk_tag.py -h
usage: misp_bulk_tag.py [-h] [-d]
                        [--loglevel {debug,info,warning,error,critical}]
                        [--no-ssl-verify] [--ca-bundle CA_BUNDLE]
                        filter_tag {add,delete,replace} target_tag

Apply tags in bulk

positional arguments:
  filter_tag            filter to get the events for which the action will be
                        performed (currently, only tag name or ID are
                        supported)
  {add,delete,replace}  action to perform (add, delete, replace)
  target_tag            tag to which the action is applied (name or ID)

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug mode (print all replies from server)
  --loglevel {debug,info,warning,error,critical}
                        Verbosity for console output. Default: warning
  --no-ssl-verify       Disable MISP ssl certificate verification
  --ca-bundle CA_BUNDLE
                        Certificate chain to use for certificate verification.
                        Uses /etc/ssl/certs/ca-certificates.crt by default
```

## Safety

- When replacing, the script will not remove the previous tag if the new one is not applied successfully
- All operations are logged in the file `journal.log`, using python `logging` module. The tab separated format is:
  `<timestamp>   <event_id> <operation> <target_tag>`
- If the journal cannot be created/written, the script will exit.

## Credits

Airbus CERT
