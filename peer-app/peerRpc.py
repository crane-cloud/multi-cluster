from jsonrpcserver import Success, method
import  requests
from jsonrpclib import Server
from terms import get_terms, update_term
from termClass import my_term
import os

import signal


@method
def request_vote():
    current_url =  os.getenv('HOST_IP'),
    #get current terms
    # terms_record = get_terms() 
    #class always returns an instance of the app
    # if terms_record is None:
    #     print("failed to retrive current term")
    #     return False
    
    # reqesting_local_term = int(terms_record['current_term'])
    requesting_local_term = my_term.value
    requesting_local_term += 1
    #using ports from inside the container
    print(current_url)
    servers = [{'ip': 'cluster-server'},{'ip': 'cluster-server-2'},{'ip': 'cluster-server-3'}]
    #create peer list
    responses = []
    
    for server in servers:
        link = "http://"+server["ip"]+":5100"
        #response = c.response_to_request(current_url,requesting_local_term)
        response = rpc_call_with_timeout(link, current_url, requesting_local_term, timeout=1)
        if response is not None:
             responses.append(response)
        else:
            reponse.append({"data":{"message":"request time out"}, "recieving_server": server["ip"], "requester_url": current_url, "code":"003", "reponse": False })
        
       
    # since the requester also pings it's own server, its current term is 
    # automatically updated  to the reqesting_local_term
    print(responses)
    #analyse responses
    # code 001 is positive
    # code 002 means their is a higher term thus update local current term to that term
    # check the server file for reference
    positive_count=0
    negative_count=0
    highest_term = requesting_local_term

    for reponse in responses:
        if reponse["code"] == "001":
            positive_count+=1

        if reponse["code"] == "003":
            negative_count+=1
        
        # for much higher term values
        if reponse["code"] == "002":
            if reponse["data"]["term"] > highest_term:
                highest_term = reponse["data"]["term"]
            negative_count+=1
    
    if highest_term > requesting_local_term:
       # update local term
       print('updating to higher term')
       #updated_team_record = update_term(current_url,str(highest_term))
       my_term.value = highest_term 
       print(my_term.value)
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


def rpc_call_with_timeout(link, current_url, requesting_local_term, timeout):
    c = Server(link)
    
    def handler(signum, frame):
        raise TimeoutError("RPC call timed out")

    # set a signal handler for the ALRM signal (SIGALRM)
    signal.signal(signal.SIGALRM, handler)

    try:
        # set a timeout for the function call
        signal.alarm(timeout)
        response = c.response_to_request(current_url, requesting_local_term)
        signal.alarm(0)  # reset the alarm
        return response
    except TimeoutError:
        return None
    
if __name__ == "__main__":
    print('start')
    #globle term instance
    # terms_record = get_terms()
    # print(terms_record)
    request_vote()


