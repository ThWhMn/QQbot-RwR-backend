# rwr-profile-server
python编写的一个游戏RunWithRifles服务器存档管理系统

## 配置

修改`config.json`文件中的

`mod_resource_path`：模组资源文件夹路径

`server_profiles_path`：服务器存档文件夹路径

`admin_token`：使用docker的情况下，上传公钥时需要配置

## 运行

### 直接运行

```
python app.py
```

### Docker运行

1. 生成运行脚本
```
python gen_docker.py
```
Windows系统将生成一个run.bat，Linux系统则是run.sh，同时之前的config.json将转移到config_bak.json，新的config.json将转移至docker内。

也生成一个run_remove.bat或者sh，用于一次性移除第2步生成的image和container。

还生成一个run_bak.bat或sh，用于将config_bak.json覆盖回config.json

**在运行完这一步之后，所有的改动都应该在config_bak.json内进行，否则重新build时，config.json的改动都会被config_bak覆盖**

2. 运行脚本
```
run.bat
```

如果要重新build，需要从第一步重新开始，config_bak.json不需要手动删除，直接运行第一步即可。

3. 删除容器和镜像
```
remove.bat
```

## 鉴权

1. 客户端生成公私密钥
```
> ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (C:\Users\myself/.ssh/id_rsa): test
```
生成成功后会在本地得到私钥文件test，和公钥文件test.pub

2. 管理员上传公钥文件

直接运行或Docker运行都执行下列脚本上传
```
python example_insert_pubkey.py username_or_uid path_to_pub_key
```
如果返回
```
{'status': 'success'}
```
则上传成功

3. 客户端建立Session并登录，例子可以参考test.py中Test类的login函数。

4. 同一Session调用API。

## 接口说明

所有POST参数都要以json格式发送

### 

请求参数：
- 必须
- 非必须

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，另带results参数，不带results
    - 如果是failure，则另带error_msg参数

### POST /insert_pubkey

请求参数：
- 必须
    - uid，字符串类型，代表公钥对应的用户名，在数据库中将作为主键
    - pubkey，字符串类型，一般以"ssh-keygen"开头。
- 非必须
    - admin_token，字符串类型，如果是向本地127.0.0.1发送请求，不需要带admin_token。如果不是，则需要

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，不带results
    - 如果是failure，则另带error_msg参数

### POST /login

请求参数：
- 必须
    - 第一次请求需携带uid，字符串类型，服务将查找uid对应的公钥，并对一个随机字符串加密，将加密结果返回给客户端
    - 第二次请求需携带d，字符串类型，是第一次请求时获取的加密信息的解密结果

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，不带results
    - 如果是failure，则另带error_msg参数

### GET /search_key_by_key

请求参数：
- 必须
    - key，字符串类型，要查找的key的子串

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，另带results参数，是list[
    [
        [key, name, text, class, nextkey],[item1,item2]
    ]
]的类型，class为"0"
    - 如果是failure，则另带error_msg参数

### GET /search_key_by_name

请求参数：
- 必须
    - name，字符串类型，要查找的name或者text的子串

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，另带results参数，是list
[
    [
        [key, name, text, class, nextkey],[item1,item2]
    ]
]的类型，class为"0"
    - 如果是failure，则另带error_msg参数

### GET /search_id_by_name

请求参数：
- 必须
    - name，字符串类型，要查找的玩家的昵称的子串

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，另带results参数，是list[tuple(id, name)]的类型
    - 如果是failure，则另带error_msg参数

### GET /give_id_key

请求参数：
- 必须
    - id，整型，通过search_id_by_name获得的id
    - key，字符串类型，通过search_key_by_name或search_key_by_key获得的key
    - cls，字符串类型，1stweapon, 2stweapon, throwable, armor, drop
- 非必须
    - dst，字符串类型，stash或backpack，默认stash
    - num，整型，要给的数量，默认1

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，不带results
    - 如果是failure，则另带error_msg参数

### GET /delete_id_key

从仓库、背包、手中依次删除，直到达到num

请求参数：
- 必须
    - id，整型，通过search_id_by_name获得的id
    - key，字符串类型，通过search_key_by_name或search_key_by_key获得的key
- 非必须
    - num，整型，要给的数量，默认1，如果是-1则全删

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，带results，整型，为删掉的数量
    - 如果是failure，则另带error_msg参数

### GET /refresh_key

请求参数：
无

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，不带results
    - 如果是failure，则另带error_msg参数

### GET /make_deal

请求参数：
- 必须
    - id_buyer，买家id，整型，通过search_id_by_name获得的id
    - id_seller，卖家id，整型，通过search_id_by_name获得的id
    - key，字符串类型，通过search_key_by_name或search_key_by_key获得的key
    - price，浮点数类型，交易物品的价格

响应：
- status，字符串类型，分两类，success和failure
    - 如果是success，另带results参数，为此次交易的操作记录
    - 如果是failure，则另带error_msg参数

