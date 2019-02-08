import itchat,random,json,time,os
from itchat.content import *
from functools import reduce

def generate_msg(myName,isReply=False,toName=None):
    msgs_0=['元宵节快乐！','新春快乐！']
    msgs_1=['真诚地','诚挚地',]
    msgs_2=['身体健康，','万事顺心，','吉祥如意，','喜气洋洋，','龙凤呈祥，',
            '万事大吉，','合乐融融，','鸿运当头，','福禄寿禧，','岁岁平安，']
    toName=toName if toName else '您'
    msg_0=random.choice(msgs_0)
    msg_0='谢谢！' if isReply else msg_0
    myName=myName+'也' if isReply else myName
    msg_1=myName+random.choice(msgs_1)+'祝'+toName
    msg_2=''.join(random.sample(msgs_2,6))[:-1]+'！'
    return msg_0+msg_1+msg_2

def zhufu(myName,useName=True):
    friends=itchat.get_friends()
    assert len(friends)>0
    times=0
    for friend in friends:
        name=friend['RemarkName']
        if name=='':
            continue
        username=friend['UserName']
        nickname=friend['NickName']
        if os.path.exists('already_list'):
            with open('already_list','r',encoding='utf8') as f:
                already_list=f.readlines()
            already_list=[i.rstrip('\n') for i in already_list]
        else:
            already_list=[]
        if nickname in already_list:
            continue
        appellations=['总','老师','医生','叔','妈','爸','爷爷','奶奶','姥姥','姥爷',
                      '外公','外婆','姑姑','姑父','舅舅','舅妈','姑妈','姐姐',
                      '哥哥','弟弟','妹妹']
        if not any([i in name for i in appellations]):
            sex=friend['Sex']
            if sex==1:
                name+='老哥'
            elif sex==2:
                name+='老姐'
        name=name if useName else None
        text=generate_msg(myName,toName=name)
        #print(text)
        itchat.send(msg=text,toUserName=username)
        times+=1
        with open('already_list','a',encoding='utf8') as f:
            f.write('%s\n'%nickname)
        time.sleep(random.uniform(1,3))
    return times

@itchat.msg_register([TEXT])
def zhufu_reply(msg):
    text_box={}
    sender=msg['FromUserName']
    sender=itchat.search_friends(userName=sender)['NickName']
    text=msg['Text']
    text_box[sender]='%s'%text
    with open('text_box','a',encoding='utf8') as f:
        f.write(json.dumps(text_box)+'\n')
    list_exist=False
    if os.path.exists('already_list'):
        list_exist=True
        with open('already_list','r',encoding='utf8') as f:
            already_list=f.readlines()
        already_list=[i.rstrip('\n') for i in already_list]
    else:
        already_list=[]
    if msg['ToUserName']=='filehelper':
        order_add=text.startswith('添加 ')
        order_cut=text.startswith('移除 ')
        order_return=any([i in text for i in ['查看名单','返回名单']])
        order_remove='删除名单' in text
        order_bn='开始祝福' in text
        confirm_ya=any([i==text for i in ['是','y','Y']])
        confirm_no=any([i==text for i in ['不','否','n','N']])
        global confirm_bn
        if order_add or order_cut:
            order_remarkname=text[3:]
            order_friend=itchat.search_friends(name=order_remarkname)
            if len(order_friend)!=0:
                order_nickname=order_friend[0]['NickName']
                if order_add:
                    should_add=True
                    if list_exist:
                        if any([order_nickname in i for i in already_list]):
                            should_add=False
                            itchat.send('名单中已存在此人',toUserName='filehelper')
                    if should_add:
                        with open('already_list','a',encoding='utf8') as f:
                            f.write('%s\n'%order_nickname)
                        itchat.send('成功添加：%s'%order_nickname,toUserName='filehelper')
                else:
                    if list_exist:
                        length_list=len(already_list)
                        already_list=[i+'\n' for i in already_list if not order_nickname in i]
                        if length_list==len(already_list):
                            itchat.send('错误，名单中不存在此人',toUserName='filehelper')
                        else:
                            with open('already_list','w',encoding='utf8') as f:
                                f.writelines(already_list)
                            itchat.send('成功移除：%s'%order_nickname,toUserName='filehelper')
                    else:
                        itchat.send('错误，尚未建立名单',toUserName='filehelper')
            elif len(order_friend)==0:
                itchat.send('错误，无人对应此备注名',toUserName='filehelper')
            else:
                itchat.send('错误，多人对应此备注名',toUserName='filehelper')
        elif order_return:
            if list_exist:
                length_list=len(already_list)
                if length_list>0:
                    for i in range(length_list):
                        nickname=already_list[i]
                        friend=itchat.search_friends(name=nickname)
                        if len(friend)==0:
                            itchat.send('无效昵称：%s'%nickname,toUserName='filehelper')
                        elif len(friend)==1:
                            remarkname=friend[0]['RemarkName']
                            already_list[i]=remarkname+'@'+nickname
                        else:
                            itchat.send('昵称：%s 对应多个账号'%nickname,toUserName='filehelper')
                    already_list='名单(备注/昵称)：'+reduce(lambda x,y:x+'，'+y,already_list)
                    itchat.send(already_list,toUserName='filehelper')
                else:
                    itchat.send('名单为空，可通过"添加 备注名"进行添加',toUserName='filehelper')
            else:
                itchat.send('错误，尚未建立名单',toUserName='filehelper')
        elif order_remove:
            if list_exist:
                os.remove('already_list')
                itchat.send('成功删除名单',toUserName='filehelper')
            else:
                itchat.send('错误，尚未建立名单',toUserName='filehelper')
        elif order_bn or not confirm_bn:
            if confirm_ya:
                times=zhufu(myName,useRemarkName)
                confim_bn=True
                itchat.send('成功祝福%d人，可"返回名单"查看'%times,toUserName='filehelper')
            elif confirm_no:
                confim_bn=True
                itchat.send('取消成功',toUserName='filehelper')
            else:
                itchat.send('确认：是否祝福？',toUserName='filehelper')
                confirm_bn=False
        else:
            itchat.send('错误，请确认格式为: "添加/移除 备注名"或"返回名单"',toUserName='filehelper')
    if sender in already_list:
        return
    if any([i in text for i in ['新年','乐','祝','福','寿']]):
        reply=generate_msg(myName,True)
        time.sleep(3)
        with open('already_list','a',encoding='utf8') as f:
            f.write('%s\n'%sender)
        return reply

if __name__=='__main__':
    useRemarkName=True#是否以好友备注名进行祝福
    myName=input('请输入用作回复时的名字：')
    itchat.auto_login(enableCmdQR=1)
    myNickName=itchat.search_friends()['NickName']
    if not os.path.exists(myNickName):
        os.mkdir(myNickName)
    os.chdir(myNickName)
    confirm_bn=True#用于二次确认
    itchat.run()
