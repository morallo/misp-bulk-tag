#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymisp import PyMISP
from keys import misp_url, misp_key
import argparse
import logging
from requests.packages import urllib3
import warnings

# Ignore warnings caused by certificate not having SubjectAltName field set.
warnings.simplefilter('ignore', urllib3.exceptions.SubjectAltNameWarning)

parser = argparse.ArgumentParser(description='Apply tags in bulk')
parser.add_argument('filter_tag', help="filter to get the events for which the action will be performed (currently, only tag name or ID are supported)")
parser.add_argument('action', choices=['add', 'delete', 'replace'],help="action to perform (add, delete, replace)")
parser.add_argument('target_tag', help="tag to which the action is applied (name or ID)")
parser.add_argument('-d', '--debug', action='store_true', default=False, help="Enable debug mode (print all replies from server)")
parser.add_argument('--loglevel', choices=['debug','info','warning','error','critical'], default="warning", help="Verbosity for console output. Default: warning")
parser.add_argument('--no-ssl-verify', dest='sslverify', action='store_false', default=True, help="Disable MISP ssl certificate verification")
parser.add_argument('--ca-bundle', default='/etc/ssl/certs/ca-certificates.crt', help="Certificate chain to use for certificate verification. Uses /etc/ssl/certs/ca-certificates.crt by default")
args = parser.parse_args()

# LOGGING configuration

logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

try:
    journal = logging.getLogger('misp_bulk_tag')
    jrnl_format = logging.Formatter(fmt="%(asctime)s\t%(message)s")
    jrnl_handler= logging.FileHandler('journal.log')
    jrnl_handler.setFormatter(jrnl_format)
    jrnl_handler.setLevel(logging.INFO)
    journal.addHandler(jrnl_handler)

except Exception:
    logging.error('Could not configure journal file. Aborting.')
    raise

def init(misp_url,misp_key,sslverify,ca_bundle='',debug=args.debug):

    if (ca_bundle and sslverify):
        ssl = ca_bundle
    else:
        ssl = sslverify
    
    return PyMISP(misp_url, misp_key, ssl, 'json', debug)

def add_tag(event,tag):
    response = misp.add_tag({'Event': event},tag)
    if response['saved']:
        journal.info("\t".join((event['id'],'add',tag)))
        return 1        
    else:
        logging.warning("Error adding tag {} for event {}. Reason: {} No tags will be removed.".format(tag, event['id'],response['errors']))
        return 0
def delete_tag(event,tag):
    response = misp.remove_tag({'Event': event},tag)
    if response['saved']:
        journal.info("\t".join((event['id'],'remove',tag)))
    else:
        logging.warning("Error removing tag {} from event {}. Reason: {}").format(tag, event['id'], response['errors'])

if __name__ == '__main__':
    
    misp = init(misp_url,misp_key,args.sslverify,ca_bundle=args.ca_bundle)

    # events = misp.search(tags=args.filter_tag)
    events = misp.search_index(tag=args.filter_tag)

    if 'errors' in events or not events['response']:
        error_message = events.get('message', "No events matched the provided tag")
        logging.error(error_message)
        exit()
    elif 'response' in events:
        events = events['response']
    
    logging.info("{} events found with the tag {}".format(len(events), args.filter_tag))
    
    for event in events:
        #Dirty hack for different pymisp behaviour in Python2 vs Python3
        if 'Event' in event:
            event = event['Event']

        if args.action == 'add':
            success = add_tag(event,args.target_tag)

        elif args.action == 'replace':
            success = add_tag(event,args.target_tag)
            if success: delete_tag(event,args.filter_tag)

        elif args.action in ('delete'):
            success = delete_tag(event,args.target_tag)

        else:
            # This should never happen
            logging.error('Unknown action specified.')
