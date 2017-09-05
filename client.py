"""
Created on 05.12.2012
Edited on 05.09.2017

@author: codejitsu, github.com/codejitsu/pyxing
@author: tahesse, githb.com/tahesse/pyxing
"""

from xing import xing
from test.oauth import get_oauth_tokens
from test.oauth_keys import consumer_key, consumer_secret, oauth_token, oauth_token_secret

if __name__ == '__main__':
    from test import oauth_keys as ok
    ok.oauth_token, ok.oauth_token_secret = get_oauth_tokens(consumer_key, consumer_secret)

    xing = xing.Xing(consumer_key, consumer_secret, oauth_token, oauth_token_secret, '1')
    
    print('Calling users.me:')
    me_response = xing.users.me.get()
    
    print('Me: {first_nane} {last_name}\n'.format(**me_response['users'][0]))
    print('Get my contacts:')
    
    contacts = xing.users.me.contacts.get()
    
    if contacts and contacts['contacts']['users']:
        for c in contacts['contacts']['users']:
            contact = xing.users(c['id']).get(fields = 'display_name,photo_urls,id')
            
            if contact:
                print('Contact: id = {}, name = {}'.format(c['id'], contact['users'][0]['display_name']))
            
