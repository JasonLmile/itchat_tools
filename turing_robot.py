import requests
import json

key = "2f5a4433f46043089026e881aadd5462"
url = "http://www.tuling123.com/openapi/api"

def reply(msg,user_id='12345678'):
    
    params = {"key":key,
                "info":msg,
                "userid":user_id
                }

    req = requests.post(url,data=json.dumps(params))
    res = json.loads(req.text)
    reply = res["text"]

    return reply

if __name__ == "__main__":
    while True:
        msg = input("I : ")
        if msg=='exit':
            break
        print("Reply : "+reply(msg))