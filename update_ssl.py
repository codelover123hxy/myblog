import requests
import hashlib
from datetime import datetime


def write_file(file_path, data):
    with open(file_path, 'w') as f:
        f.write(data)

def md5(string):
    # 创建一个 MD5 哈希对象
    md5_hash = hashlib.md5()
    # 更新哈希对象的内容（需要将字符串编码为字节）
    md5_hash.update(string.encode('utf-8'))
    # 返回十六进制格式的哈希值
    return md5_hash.hexdigest()

def get_timestamp():
    now = datetime.now()
    # 获取时间戳（以秒为单位）
    timestamp_seconds = now.timestamp()
    # 转换为毫秒
    timestamp_milliseconds = int(timestamp_seconds * 1000)
    return timestamp_milliseconds

# 部署节点Id
apiId = "push-7l13g8j2xprxm9qp"
# API接口密钥
apiKey = "e2cc1a189f562364cdee3e998ac066d4"
# 当前ms时间戳
timestamp = get_timestamp()
# 目标证书ID
certificate_dict = {
    '*.aiyin.club': {
        'certId': 'cert-ny5jx0l5kpkr7m6p',
        'key_file_path': '/etc/nginx/cert/aiyin.club/cert.key',
        'pem_file_path': '/etc/nginx/cert/aiyin.club/fullchain.pem'
    }
}

certificateId = certificate_dict['*.aiyin.club']['certId']

# 用于签名的参数列表
params = [f"apiId={apiId}", f"timestamp={timestamp}", f"certificateId={certificateId}"]

# 用于签名的参数列表：用于请求的参数列表 + API接口密钥
paramsForSign = params + [f"apiKey={apiKey}"]

# 用于签名的参数列表使用字母序进行排序
paramsForSign.sort()

# 用于签名的参数列表使用"&"号进行拼接成用以签名的字符串
stringForSign = "&".join(paramsForSign)
# 以上字符串的32位小写MD5哈希值即为参数签名
sign = md5(stringForSign) 

# 注意最终请求的参数中不包含apiKey
url = f"https://ohttps.com/api/open/getCertificate?sign={sign}&{'&'.join(params)}"
print(url)


def deploy_cert(key_file_path, pem_file_path):
    res = requests.get(url=url).json()
    cert_key = res['payload']['certKey']
    full_chain_certs = res['payload']['fullChainCerts']
    write_file(key_file_path, cert_key)
    write_file(pem_file_path, full_chain_certs)
    print("部署成功")


for key in certificate_dict:
    print(key)
    key_file_path = certificate_dict[key]['key_file_path']
    pem_file_path = certificate_dict[key]['pem_file_path']
    deploy_cert(key_file_path, pem_file_path)
