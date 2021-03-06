from wxpy import *
import requests
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import jieba


bot = Bot(cache_path=True)
bot.enable_puid('wxpy_puid.pkl')

friends ={}

api_key='af6e96a10a2340e7bbe011f630a8c070'
posturl = 'http://openapi.tuling123.com/openapi/api/v2'

help_msg = '''Hello there, I am duoduo. My owner is now away, you are welcome to talk to me! \r\nI can answer below questins. Type specific number to know related info.\n
        1. Hello.
        2. how are you
        3. random talk with tuling robot...
        4. random talk with apiai robot

    if need immediate help, call my owner at cell number xxxx  
    
                 '''
def get_corpus(corpus_path = './hy.txt', sep='##'):
    if os.path.exists(corpus_path):
        try:
            with open(corpus_path, 'r') as f:
                for doc in f:
                    tmp = doc.split(sep)
                    if len(tmp) == 2:
                        yield tmp[0], tmp[1]
                    else:
                        continue
        except:
            return None
    else:
        return None

@bot.register(msg_types = [TEXT,PICTURE], except_self=False)
def auto_reply(msg):
    #print(msg.chat.name)
    
    if msg.chat.name not in friends:
        friends[msg.chat.name] = 0
        return help_msg
    mode = friends[msg.chat.name]
    if mode == 0:
        if '1' == msg.text:
            return 'Hello'
        elif '2' == msg.text:
            friends[msg.chat.name] = 2
            return 'You now can ask me questions about HY business. Enter "quit" to exit.'
        elif '3' == msg.text:
            friends[msg.chat.name] = 3
            return 'what do you want to talk about to tuling robot? Enter "quit" to exit.'
        elif '4' == msg.text:
            friends[msg.chat.name] = 4
            return 'what do you want to talk about to apiai robot?'
        else:
            return help_msg
    elif mode == 2:
        if '退出'== msg.text or 'quit' == msg.text:
            friends[msg.chat.name] = 0
            return help_msg
        else:
            corpus, answer = get_corpus()
            if corpus:
                tf = TfidfVectorizer(token_pattern='(?u)\\b\\w+\\b')
                mat = tf.fit_transform(corpus)
                msg_vect = tf.transform([' '.join(jieba.cut_for_search(msg.text))])
                sim = linear_kernel(mat, msg_vect)
                most_sim = sorted(enumerate(sim), lambda x : x[1][0], reverse =True)[0]
                return answer[most_sim[0]]
            else:
                friends[msg.chat.name] = 0
                return 'NO corpus found! \r\n' + help_msg

    elif mode == 3:
        if '退出'== msg.text or 'quit' == msg.text:
            friends[msg.chat.name] = 0
            return help_msg
        else:
            if msg.file_name:
                print(msg.file_name)
                msg.get_file(msg.file_name)
                data={
                'reqType': 1,
                'perception': {
                    'inputImage': {
                        'url':msg.file_name
                    }
                },
                'userInfo': {
                    'apiKey': api_key,
                    'userId': msg.chat.puid
                }
            }
            else:
                data={
                    'reqType': 0,
                    'perception': {
                        'inputText': {
                            'text':msg.text,
                        },
                    },
                    'userInfo': {
                        'apiKey': api_key,
                        'userId': msg.chat.puid
                    }
                }
            
            jsondata = json.dumps(data)
            print(jsondata)
            s = requests.post(posturl, data=jsondata).json()
            print(s)
            responses = []
            #print(s['intent']['code'])
            if s['intent']['code'] < 20000:
                for result in s['results']:
                    resultType = result['resultType']
                    print(resultType)
                    if resultType == 'text':
                        responses.append(result['values']['text'])
                    elif resultType == 'news':
                        news = result['values']['news']
                        for nw in news:
                            responses.append(nw['name'] + ':' + nw['detailurl'])
                    elif resultType =='url':
                        responses.append(result['values']['url'])
                    elif resultType == 'image':
                        img_url = result['values']['image']
                        r = requests.get(img_url, stream = True)
                        img_name = img_url.split('/')[-1]
                        with open(img_name, 'wb') as img:
                            for cnt in r.iter_content():
                                img.write(cnt)
                        msg.reply_image(img_name)
                        os.remove(img_name)
                    elif resultType =='voice':
                        return 'currently not supported type ' + resultType
                    elif resultType =='video':
                        return 'currently not supported type ' + resultType
                    else:
                        return 'unknown result type {} returned'.format(resultType)
                
                return '\r\n'.join(responses)

            else:
                return 'error met with code {}'.format(s['intent']['code']) 
    elif mode == 4:
        return 'you are talking to a apiai robot... NOT IMPLEMENTED YET.'
    else:
        pass #should not be here.
'''
@bot.register()
def print_messages(msg):
    print(msg) 
'''


embed()