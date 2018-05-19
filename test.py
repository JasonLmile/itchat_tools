import itchat
from itchat.content import *
import turing_robot
import random
import time

#一个key为名字,value为对应请求userid的字典
username = dict()
user_msg = dict()


#发送消息提示
def helpmsg():
    global username
    hint = "选择模式:\n\
1.开启机器人回复\n\
2(+'@'+'你想要使用的人的名称').对其他人开启自动回复\n\
q(+'@'+'取消名称').取消某人的自动回复\n\
q1.退出模式1\n\
q2.退出模式2"
    
    msg = "目前开启自动回复的有:\n"
    for name in username:
        name = str(name)
        if name == 'filehelper':
            name = "文件传输助手"
        msg += str(name) + ' '

    itchat.send(hint,toUserName='filehelper')
    itchat.send(msg,toUserName='filehelper')

@itchat.msg_register(TEXT,isGroupChat=True)
def group_reply(msg):
    """群消息@我的自动回复 """
    if msg['isAt']:
        itchat.send("收到",['RecommendInfo']['UserName'])

#通过与消息助手命令行交互,更新username列表
@itchat.msg_register(TEXT)
def dealMsg(msg):
    """ 判断是否消息来自消息助手,否则转入auto_reply()函数自动回复 """
    global username,user_msg
    req = str(msg["Text"])
    replyname = msg["FromUserName"] 
    #判断是否需要自动回复
    isNeed = True
    id = 123456

    if msg['ToUserName'] == "filehelper":
        replyname = "filehelper"
        isNeed = False
        #如果发出信息问号就发送消息提示
        if '?' == req or '？' == req:
            helpmsg()
        
        #1表示开启与机器人对话
        elif req == '1':
            username.update({'filehelper':id})

        elif '2@' in req:
            nickname = req.split('@')[1]
            while id in username.values() and username.values():
                id = random.randrange(999999)
            
            username.update({nickname:id})
            
        elif req == 'q1':
            username.pop('filehelper')

        elif req == 'q2':
            if 'filehelper' in username:
                username = ['filehelper']
            else:
                username.clear()
        
        elif 'q@' in req:
            nickname = req.split('@')[1]
            username.pop(nickname)

        #如果不满足以上条件就传入自动回复
        else:
            isNeed = True
    
    if isNeed:
        storeRevoke(msg)
        auto_reply(req,replyname)
            
def auto_reply(msg,UserName):
    """ @UserName 对应好友的一段字符串
    如果是来自消息助手就转入交互状态,如果是好友就判断是否要自动回复 """
    global username
    
    if UserName == 'filehelper':
        if 'filehelper'  in username:    
            reply = turing_robot.reply(msg)
            itchat.send(reply,toUserName=UserName)
    
    else:
        info = itchat.search_friends(userName=UserName)
        #返回值为字典
        remarkname = info["RemarkName"]
        nickname = info["NickName"]

        name = ''
        if remarkname in username:
            name = remarkname
        elif nickname in username:
            name = nickname

        if name:
            reply = turing_robot.reply(msg,username[name])
            itchat.send(reply,toUserName=UserName)
            
            tips = "来自%s的消息已自动回复" % name
            itchat.send(tips,toUserName="filehelper")

import re
@itchat.msg_register(NOTE)
def isRevoke(msg):
    """是否消息撤回了"""
    text = msg['Text']
    revoke = re.match(r'.*?撤回了一条消息',text)
    
    if revoke:
        name = revoke.group().split('撤回')[0]
        name = re.sub('\W','',name)
        xml = str(msg['Content'])
        pattern = re.compile('<msgid>(.*?)</msgid>')
        string = re.search(pattern,xml).group()
        
        revokeMsgId = re.sub('\D','',string)
        revoke_msg = name+" 撤回了一条消息"+':\n'
        timestamp = user_msg[revokeMsgId]['Time']
        timemsg = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))
        
        itchat.send(revoke_msg,toUserName="filehelper")
        itchat.send(timemsg +':\n' +user_msg[revokeMsgId]['Content'],toUserName='filehelper')

        files = os.listdir(createDir)
        Content = user_msg[revokeMsgId]['Content']
        
        if Content in files:
            filename = os.path.join(createDir,Content)
            file = '@fil@%s' % filename
            print(itchat.send(msg=file,toUserName='filehelper'))
            os.remove(filename)

import os
workDir = os.getcwd()
createDir = os.path.join(workDir,"Recvfile")
if not os.path.exists(createDir):
    os.mkdir(createDir)

def storeRevoke(msg):
    """存储并定时更新可能撤回的消息"""
    global user_msg
 
    #收到信息时间与现在时间做比较,超过两分钟就删除
    now = int(time.time())
    for user in user_msg:
        if user_msg[user]['Time'] <= now-120:
            user_msg.pop(user)
    
    MsgId = msg['MsgId']
    type = msg['Type']
    Time = int(time.time())
    
    #Content中存储文件或者内容
    if type == "Text":
        Content = msg["Content"]
    elif type == 'Card':
        Content = msg['RecommendInfo']['NickName'] + '的名片'
    elif type == 'Sharing':
        Content = msg['Text'] + msg['url']
    else:
        Content = msg['FileName']
        msg['Text'](os.path.join(createDir,Content))


    user_msg.update({MsgId:{'Content':Content,"Time":Time}})

@itchat.msg_register([PICTURE,SHARING,ATTACHMENT,VIDEO,RECORDING,CARD])
def OtherMsg(msg):
    storeRevoke(msg)

itchat.auto_login(hotReload=True)
itchat.run()