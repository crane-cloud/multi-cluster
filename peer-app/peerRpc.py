from jsonrpcserver import Success, method
import  requests
from jsonrpclib import Server
from terms import get_terms, update_term

import os

@method
def send_profile_to_peers():
    current_url =  os.getenv('HOST_IP'),
    #get current terms
    terms_record = get_terms()
    if terms_record is None:
        print("failed to retrive current term")
        return False
    
    reqesting_local_term = int(terms_record['current_term'])
    reqesting_local_term += 1
    #using ports from inside the container
    print(current_url)
    servers = [{'ip': 'cluster-server'},{'ip': 'cluster-server-2'},{'ip': 'cluster-server-3'}]
    #create peer list
    responses = []
    
    for server in servers:
        c = Server("http://"+server["ip"]+":5100")
        response = c.peer_message_response(current_url,reqesting_local_term)
        responses.append(response)
    # since the requester also pings it's own server, its current term is 
    # automatically updated  to the reqesting_local_term
    print(responses)
    #analyse responses
    # code 001 and 002 are postive
    # code 004 means their is a higher term thus update local current term to that term
    # check the server file for reference
    positive_count=0
    negative_count=0
    highest_term = reqesting_local_term

    for reponse in responses:
        if reponse["code"] == "001" or reponse["code"] == "002":
            positive_count+=1

        if reponse["code"] == "003" or reponse["code"] == "005":
            negative_count+=1
        
        # for much higher term values
        if reponse["code"] == "004":
            if reponse["data"]["term"] > highest_term:
                highest_term = reponse["data"]["term"]
            negative_count+=1
    
    if highest_term > reqesting_local_term:
       # update local term
       print('updating to higher term')
       updated_team_record = update_term(current_url,str(highest_term))
       print(updated_team_record)
       return True

    if positive_count > negative_count:
        print("Proceed to vote request")   
        return True
    elif positive_count is negative_count:
       print("inconclusive")
       return False
    else:
       print("failed process")
       return False 

if __name__ == "__main__":
    print('start')
    # terms_record = get_terms()
    # print(terms_record)
    send_profile_to_peers()


