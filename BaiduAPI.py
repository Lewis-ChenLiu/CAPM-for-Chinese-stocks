import sys, json, base64, time, ssl
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode, quote_plus
from func_timeout import func_set_timeout


# 百度API相关参数设置
ssl._create_default_https_context = ssl._create_unverified_context
API_KEY = 'Hb4Y9o8tjI4DY9kOek3iYUDZ'
SECRET_KEY = 'aGHZx3XTjEQcYBVOG1PDCseIyKop9wX5'
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
USE_URL = "https://aip.baidubce.com/rpc/2.0/nlp/v1/depparser"


# 获取token
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    
    result_str = result_str.decode()
    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()


def trans(string):
	if string != None:
		return str(string)
	else:
		return 'None'


# 进行请求
def request(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        result_str = result_str.decode()
        return result_str
    except URLError as err:
        print(err)


# 处理请求结果，筛选停用词及词性
@func_set_timeout(10)
def make_request(url, text, seq='\n'):
    outlist = [text]

    response = request(url, json.dumps({
        'text': text,
    }))

    data = json.loads(response)
    if 'error_code' not in data or data['error_code'] == 0:
        for item in data['items']:
            outlist.append(trans(item['id'])+' && '+trans(item['word'])+' && '+trans(item['postag'])+' && '+trans(item['head'])+' && '+trans(item['deprel']))
        outlist.append('--END--\n')
    else:
        print(response)

    # 防止qps超限
    time.sleep(0.6)
    return seq.join(outlist)