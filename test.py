import itchat
from itchat.content import *
import turing_robot
import random

#一个key为名字,value为对应请求userid的字典
username = dict()

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

#群消息@我的自动回复
@itchat.msg_register(TEXT,isGroupChat=True)
def aotu_reply(msg):
    if msg['isAt']:
        itchat.send("收到",['RecommendInfo']['UserName'])

#通过与消息助手命令行交互,更新username列表
@itchat.msg_register(TEXT)
def test(msg):
    global username
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
        auto_reply(req,replyname)
            
#检查是否位于列表中决定是否自动回复
def auto_reply(msg,UserName):
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

itchat.auto_login(hotReload=True)
itchat.run()