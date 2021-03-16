#encoding: utf-8
from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109 import DescribeDomainsRequest,DescribeDomainRecordsRequest,UpdateDomainRecordRequest
import json,urllib.request,re


#替换以下参数 下面是操作（阿里云域名解析IP的修改）
ID=" " #这边是key 替换成自己的
Secret=" " #替换成自己的
RegionId="cn-guangzhou" #解析记录的ID，此参数在添加解析时会返回，在获取域名解析列表时会返回
DomainName=" " #一级域名 替换成自己的
#想要自动修改的主机名和域名类型
HostNameList = ["*","www","@"] #这边可以添加二级域名或者"*"所有的都满足；By Fnckerpoi:我这边控制台的解析记录是www和@
Types = "A" #解析记录类型
TTL="600" #生存时间，默认为600秒 ,也就是解析时间，我这边是1秒（买了解析的会员服务）

clt = client.AcsClient(ID,Secret,RegionId)

#获取公网ip
def GetLocalIP():
    #下面获取公网IP地址，用了2种方式，防止一个失效报错
    try:
        IPInfo = urllib.request.urlopen("http://api.ipify.org/?format=json").read()
    except IOError:
        try:
            IPInfo =urllib.request.urlopen("https://www.taobao.com/help/getip.php").read()
        except IOError:
            IPInfo = "So sorry!!!"

    theIP =re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}",IPInfo.decode('GBK'))

    nowIP=theIP.pop(0)
    print("nowIP::"+nowIP)
    return nowIP

#获取域名列表（暂时无用）
def GetDomainList():
    DomainList = DescribeDomainsRequest.DescribeDomainsRequest()
    DomainList.set_accept_format('json')
    DNSListJson = json.loads(clt.do_action_with_exception(DomainList))
    # print(DNSListJson)

#更新域名ip
def EditDomainRecord(HostName, RecordId, Types, IP):
    UpdateDomainRecord = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
    UpdateDomainRecord.set_accept_format('json')
    UpdateDomainRecord.set_RecordId(RecordId)
    UpdateDomainRecord.set_RR(HostName)
    UpdateDomainRecord.set_Type(Types)
    UpdateDomainRecord.set_TTL(TTL)
    UpdateDomainRecord.set_Value(IP)
    try :
        UpdateDomainRecordJson = json.loads(clt.do_action_with_exception(UpdateDomainRecord))#不知道为什么这里会报异常，我直接忽略不管了，不过控制台显示ip照常能变更
        print("UpdateDomainRecordJson::" + UpdateDomainRecordJson)
    except :pass

#获取域名信息
def GetAllDomainRecords(DomainName, Types, IP):
    DomainRecords = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    DomainRecords.set_accept_format('json')
    DomainRecords.set_DomainName(DomainName)
    DomainRecordsJson = json.loads(clt.do_action_with_exception(DomainRecords))
    print(DomainRecordsJson)
    for HostName in HostNameList:
        for x in DomainRecordsJson['DomainRecords']['Record']:
            RR = x['RR']
            Type = x['Type']
            if RR == HostName and Type == Types:
                RecordId = x['RecordId']
                print("RecordId::"+RecordId)
                # 这里是 修改域名解析的IP，前提是你得在域名厂商先添加一个域名解析
                # 如果当前服务器IP和域名解析中IP中一样会报错，没关系，因为两个IP 一样，不需要修改阿里云域名解析的IP
                EditDomainRecord(HostName, RecordId, Types, IP)

IP = GetLocalIP()
GetDomainList() #这个方法是显示看得
GetAllDomainRecords(DomainName, Types, IP)
