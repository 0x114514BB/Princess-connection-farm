import random
import time

from id_validator import validator

from core.constant import MAIN_BTN, ZHUCAIDAN_BTN, START_UI
from core.pcr_config import debug, captcha_wait_time, captcha_popup, captcha_skip, captcha_senderror, \
    captcha_senderror_times, use_my_id, captcha_sleep_times
from core.safe_u2 import timeout
from core.tkutils import TimeoutMsgBox
from core.usercentre import AutomatorRecorder
from core.utils import random_name
from ._tools import ToolsMixin
from ._base import DEBUG_RECORD
from ._captcha import CaptionSkip


class BadLoginException(Exception): pass


class LoginMixin(ToolsMixin):
    """
    登录插片
    包含登录相关操作的脚本
    """

    def __init__(self):
        super().__init__()
        if not self.log:
            from ._tools import ToolsMixin

    @timeout(180, "start执行超时：超过3分钟")
    @DEBUG_RECORD
    def start(self):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        启动脚本，请确保已进入游戏页面。
        """
        self.phone_privacy()
        while True:
            # 判断jgm进程是否在前台, 最多等待20秒，否则唤醒到前台
            if self.d.app_wait("com.bilibili.priconne", front=True, timeout=1):
                if not self.appRunning:
                    # 从后台换到前台，留一点反应时间
                    time.sleep(1)
                self.appRunning = True
                break
            else:
                self.app = self.d.session("com.bilibili.priconne")
                self.appRunning = False
                continue

    @DEBUG_RECORD
    def do_login(self, ac, pwd):  # 执行登陆逻辑
        """
        :param ac:
        :param pwd:
        :return:
        """
        # 也许你已经注意到，这个整个登陆函数已经成了屎山了，
        # 每次只要出现登陆部分的BUG都要改半天
        # 你永远不知道你程序当前运行在哪个函数里,auth?login_auth?login?do_login?init_home?lock_home?
        # 如果你想知道，建议在config中把disable_timeout_raise给开启，
        # 然后在程序运行时按Ctrl+C，如果你运气好，你会看到你程序卡在哪里。
        # 我放弃了。  新增自动点击“下载”，自动下载新增数据功能， 2020-11-23 By TheAutumnOfRice

        # 结构梳理下为：auth -> login_auth(是否需要实名认证<->login<->do_login[验证码处理]) -> init_home(lock_home)
        for retry in range(300):
            self.log.write_log('info', f"点击事件retry: {retry}")
            self._move_check()
            self.click(945, 13)  # 防止卡住
            if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_other").exists():
                self.d(resourceId="com.bilibili.priconne:id/tv_gsc_other").click()
                self.log.write_log('info', f"点击事件1")
                time.sleep(0.8)
                continue
            if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").exists():
                self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").click()
                self.log.write_log('info', f"点击事件2")
                time.sleep(0.8)
                continue
            # 到登录界面 点头像展开
            
            if self.d(resourceId="com.bilibili.priconne:id/iv_gsc_recode_head").exists():
                self.d(resourceId="com.bilibili.priconne:id/iv_gsc_recode_head").click()
                self.log.write_log('info', f"点击下拉框")
                time.sleep(0.8)
                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_item_name", text=pwd).exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_item_name", text=pwd).click()
                    self.log.write_log('info', f"成功切换账户{ac}，用户名{pwd}")
                    time.sleep(0.4)
                    break
                else:
                    self.log.write_log('info', f"未找到账户{ac}，用户名{pwd}")
                    continue
            # if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").exists():
            #     self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").click()
            #     time.sleep(0.8)
            #     continue
            # if self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").exists():
            #     time.sleep(0.8)
            #     self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").click()
            #     continue
            if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                self.click(687, 72)
                # 防止卡验证码
                continue
            if not self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").exists():
                time.sleep(0.2)
            else:
                break
        else:
            raise Exception("进入登陆页面失败！")

        time.sleep(0.5) 
        self.log.write_log('info', f"即将点击登录！")
        self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login").click()
        time.sleep(1.0)
        '''
        TODO: 根据名称切账户，账户名称用password表示
        d(resourceId="com.bilibili.priconne:id/iv_gsc_recode_head") # 点击登录下拉框

        d(resourceId="com.bilibili.priconne:id/tv_gsc_record_item_name", text="炸鱼810") # 点击登陆记录框
        
        
        // 下面的部分都可以跳过了


        self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").click()
        self.d.clear_text()
        self.d.send_keys(str(ac))
        self.d(resourceId="com.bilibili.priconne:id/et_gsc_account_pwd").click()
        self.d.clear_text()
        self.d.send_keys(str(pwd))
        time.sleep(random.uniform(0.2, 1))
        self.d(resourceId="com.bilibili.priconne:id/tv_gsc_account_login").click()
        time.sleep(1.5)
        toast_message = self.d.toast.get_message()
        # print(toast_message)
        if toast_message == "密码错误":
            raise BadLoginException("密码错误！")
        elif toast_message == "系统检测到您的账号异常，请前往网页主站重新登录并进行验证":
            raise BadLoginException("账号异常！")
        elif toast_message == "密码不安全，请立即修改密码":
            raise BadLoginException("密码不安全！")
        # else:
        #     print(f"toast_message:{toast_message}")
        '''

        while True:
            # 快速响应
            # 很容易在这里卡住
            time.sleep(0.1)
            sc = self.getscreen()
            if self.is_exists(MAIN_BTN["xiazai"], screen=sc):
                self.click(MAIN_BTN["xiazai"])
            if self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                break
            elif self.is_exists(MAIN_BTN["liwu"], screen=sc):
                break
            elif self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                break
            elif self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists():
                return 1  # 说明要进行认证
            elif not self.d(resourceId="com.bilibili.priconne:id/tv_gsc_account_login").exists() and \
                    not self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists():
                break
            elif self.d(resourceId="com.bilibili.priconne:id/vp_gs_announcement").exists():
                # 广告弹窗
                break

        def SkipAuth():
            # 跳过协议
            for _ in range(2):
                # 有两个协议需要同意
                if debug:
                    self.log.write_log('debug', "等待认证")
                while self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    if debug:
                        self.log.write_log('debug', "发现协议")
                    self._move_check()
                    try:
                        r = self.img_where_all(START_UI["xieyihuakuai"], threshold=0.99)
                        self.d.touch.down(r[0], r[1]).sleep(1).up(r[0], r[1])
                    except:
                        # 退化成老办法
                        self.d.touch.down(808, 324).sleep(1).up(808, 324)
                        self.d.touch.down(808, 353).sleep(1).up(808, 353)
                    if self.d(text="请滑动阅读协议内容").exists():
                        self.d(text="同意").click()
                    if self.d(description="请滑动阅读协议内容").exists():
                        # 雷电三
                        self.d(description="同意").click()
                    # time.sleep(6)
                if debug:
                    self.log.write_log('debug', "结束认证")

        def SkipAD():
            if self.d(resourceId="com.bilibili.priconne:id/vp_gs_announcement").exists():
                if debug:
                    self.log.write_log("debug", "发现bilibili的广告弹窗")
                self.click(161, 446)
                self.d(resourceId="com.bilibili.priconne:id/iv_gs_announcement_close").click()
                if debug:
                    self.log.write_log("debug", "广告弹窗处理完成")

        def due_AutoCaptcha(toast=True, blocking=False):
            """
            :param blocking: 堵塞等待结果处理
            :param toast: 抓取toast
            :return -1:代表验证码已经被脚本刷新
            """
            # 处理验证码操作，已经不分前后了
            nonlocal _time
            nonlocal _id
            nonlocal _pop
            if blocking:
                for_times = iter(int, 1)
                # print("死循环开启")
            else:
                for_times = range(0, 1)
            for _ in for_times:
                toast_message = "no message"
                # 答题过的id为str，优先队列执行
                if type(_id) is str and \
                        (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    if self.d(text="提交").exists():
                        self.d(text="提交").click()
                    else:
                        self.d(text="确认").click()
                    _id = -1
                    return -1  # 不清楚验证码是否验证成功，会导致toast无法执行

                if toast:
                    # 这里是验证码登录后
                    toast_message = self.d.toast.get_message()  # 耗时大户
                    # print(toast_message)

                if _id == 0:
                    # time.sleep(1)
                    # 检测到题目id为0就重新验证
                    # 防止卡验证码
                    if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                        self.click(687, 72)
                    _id = -1
                    return -1

                elif self.d(textContains="请点击此处重试").exists():
                    self.log.write_log('info', f">>>{self.account}-请点击此处重试")
                    # 点重试
                    # self.click(482, 315)
                    self.d(text="请点击此处重试").click()
                    return -1

                elif self.d(textContains="异常").exists() or self.d(textContains="返回").exists():
                    self.log.write_log('info', f">>>{self.account}-网络异常，刷新验证码")
                    self.click(476, 262)
                    self.d(text="返回").click()
                    return -1
                # time.sleep(1)
                # sc2 = self.getscreen()
                # p = self.img_equal(sc1, sc2, at=START_UI["imgbox"])
                # print(p)
                # if p <= 0.99:
                #     nonlocal state
                #     self.d(text="提交").click()
                #     state = True
                # else:
                #     state = False
                elif toast_message == "请检查网络,-662":
                    self.log.write_log('info', "请检查网络,-662")
                    # print("请检查网络,-662")
                    if self.d(text="登录").exists():
                        self.d(text="登录").click(timeout=5)
                    # time.sleep(captcha_sleep_times)
                    return -1
                    # raise BadLoginException("请检查网络，-662")
                elif toast_message == "密码错误":
                    raise BadLoginException("密码错误！")
                elif toast_message == "系统检测到您的账号异常，请前往网页主站重新登录并进行验证":
                    raise BadLoginException("账号异常！")

                # 重生验证码
                elif (_time >= 2 or _time == 0) and \
                        (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    # print(_time, "验证码重生")
                    self.log.write_log('info', "验证码刷新")
                    self.click(687, 72)
                    self.d(text="登录").click(timeout=10)
                    _time = 1
                    return -1

                # 单独控件检测应该放在最后
                elif self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").exists():
                    # time.sleep(0.8)
                    if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_phone_terms").exists():
                        if not self.is_exists(START_UI["gouxuan"]):
                            self.lock_img(START_UI["gouxuan"], elseclick=(293, 424), elsedelay=1, retry=2)
                    self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").click(timeout=5)
                    # time.sleep(captcha_sleep_times)
                    return -1

                elif self.d(text="登录").exists():
                    self.d(text="登录").click(timeout=5)
                    return -1

            # 下面代码暂时不管用
            # if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
            #     if _time >= 5:
            #         print("重试次数太多啦，休息15s")
            #         time.sleep(15)
            #         _time = 0
            #         AutoCaptcha()
            #     # 如果次数大于两次，则申诉题目
            #     elif _time > captcha_senderror_times and captcha_senderror:
            #         print("—申诉题目:", _id)
            #         cs.send_error(_id)
            #     _time = + 1
            #     print("验证码登陆验证重来！")
            #     # 如果还有验证码就返回重试
            #     AutoCaptcha()

        SkipAuth()
        SkipAD()
        flag = False
        if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
            flag = True
            _time = 0
            _id = -1  # -1代表没有答题
            _pop = False

            # 初始化接码
            cs = CaptionSkip(self.log)

            def AutoCaptcha():

                nonlocal _time  # 验证码答题次数
                nonlocal _id
                nonlocal _pop
                # time.sleep(1)
                # 这里是判断验证码动画是否加载完毕和截图到达指定位置
                # 不用at，直接全图找更保险.请自行处理验证失败图片抖动的耗时
                screen = None
                # 这里堵塞了，等图像稳定
                if self.wait_for_stable(similarity=1.0, threshold=0.1, delay=0.5, at=(348, 162, 621, 439)):
                    # 原来的 456, 489
                    # 不要了，这是新的分辨率，需要包含游戏一部分截图 636,539
                    screen = self.getscreen()[1:575, 157:793]

                    # 白屏处理
                    find_bw_img = screen[44:492, 94:543]
                    w, b, _, _ = self.img_findgaoliang(find_bw_img)
                    if b == 0:
                        return False
                    elif w > 200000 and b < 5000:
                        return False

                elif not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    return False

                # 再改就屎山了（
                if due_AutoCaptcha(toast=False) == -1:
                    return False

                if self.d(textContains="请在下图依次").exists():
                    self.log.write_log('info', f">>>{self.account}-检测到图字结合题")
                    self.log.write_log('warning', "当出现这玩意时，请仔细核对你的账号密码是否已被更改找回！")
                    # 这是关闭验证码 self.click(674, 74, post_delay=3)
                    # 结果出来为四个字的坐标
                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X6004")
                    for i in range(0, _len):
                        x = int(answer_result[i].split(',')[0]) + 157
                        y = int(answer_result[i].split(',')[1]) + 1
                        if not (94 < x < 371) and not (128 < y < 441):
                            # 左上 94,128 右下 371,441,对返回的结果的范围进行限制
                            if debug:
                                self.log.write_log('debug', ">[范围]刷新验证码")
                            # 刷新验证码
                            answer_result = [255, 439]
                        if answer_result == [255, 439]:
                            self.click(687, 72)
                            # self.d(text="登录").click(timeout=1)
                            self.log.write_log('info', "平台识别不出来，刷新")

                        self.log.write_log('info', f">{self.account}-验证码第{i}坐标识别：{x},{y}")
                        self.click(x, y)
                    _time += 1
                    return True

                elif self.d(textContains="请点击").exists():
                    self.log.write_log('info', f">>>{self.account}-检测到图形题")

                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X6001")
                    # print(answer_result,' ', _len,' ', _id)
                    x = int(answer_result[0]) + 157
                    y = int(answer_result[1]) + 1
                    self.log.write_log('info', f">{self.account}-验证码坐标识别： {x},{y}")
                    # print(type(x))
                    self.click(x, y)
                    if answer_result == [255, 439]:
                        self.click(687, 72)
                        # self.d(text="登录").click(timeout=1)
                        self.log.write_log('info', "平台识别不出来，刷新")
                    else:
                        pass
                        # time.sleep(captcha_sleep_times)
                    _time += 1
                    return True

                elif self.d(textContains="拖动滑块").exists():
                    self.log.write_log('info', f">>>{self.account}-检测到滑块题")
                    answer_result, _len, _id = cs.skip_caption(captcha_img=screen, question_type="X8006")
                    x = int(answer_result[0]) + 157
                    y = int(answer_result[1]) + 1
                    self.log.write_log('info', f">{self.account}-滑块坐标识别：{x}, 386")
                    # print(type(x))
                    # 从322,388 滑动到 x,y
                    self.d.drag_to(322, 388, x, 386, 3.6)
                    if answer_result == [255, 439]:
                        self.click(687, 72)
                        # self.d(text="登录").click(timeout=1)
                        self.log.write_log('info', "平台识别不出来，刷新")
                    else:
                        pass
                        # time.sleep(captcha_sleep_times)
                    _time += 1
                    return True

                else:
                    self.log.write_log('info', f"{self.account}-存在未知领域，无法识别到验证码（或许已经进入主页面了），如有问题请加群带图联系开发者")
                    return False

            manual_captcha = captcha_skip
            if captcha_skip is False:
                exist_geetest = False
                # state = True  # 先这样，10s验证，state几乎已经不适用了
                # 请确保来这之前已经有账户和密码输入！
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    exist_geetest = True
                while exist_geetest:
                    if self.d(className='android.widget.RelativeLayout').exists():
                        try:
                            # print(self.account, "在过验证码")
                            if AutoCaptcha():
                                due_AutoCaptcha(blocking=True)
                        except Exception as e:
                            self.log.write_log('error', f"自动过验证码发生报错:{e}")
                            continue
                        # # time.sleep(5)
                        # if not state:
                        #     manual_captcha = True
                        #     break
                    else:
                        time.sleep(1)
                        if not self.d(className='android.widget.RelativeLayout').exists():
                            self.log.write_log('info', f"{self.account}已经过验证码")
                            SkipAuth()
                            SkipAD()
                            flag = False
                            break
                        elif due_AutoCaptcha() == -1:
                            continue
            else:
                manual_captcha = True
            if manual_captcha:
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    self.log.write_log("error", message='%s账号出现了验证码，请在%d秒内手动输入验证码' % (self.account, captcha_wait_time))
                    if captcha_popup:
                        TimeoutMsgBox("!", f"{self.address}出现验证码\n账号：{self.account}", geo="200x80",
                                      timeout=captcha_wait_time)
                    now_time = time.time()
                    while time.time() - now_time < captcha_wait_time:
                        self._move_check()
                        time.sleep(1)
                        if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                            flag = False
                            break
                    time.sleep(1)
                if not (self.d(text="Geetest").exists() or self.d(description="Geetest").exists()):
                    flag = False
                    SkipAuth()
                    SkipAD()
        if self.d(resourceId="com.bilibili.priconne:id/gsc_rl_realname_web").exists(timeout=0.1):
            return 1  # 说明要进行认证
        if flag:
            return -1
        else:
            return 0  # 正常

    @DEBUG_RECORD
    def login(self, ac, pwd):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        :param ac:
        :param pwd:
        :return:
        """
        error_flag = 0
        try:
            # 看是否跳出主菜单
            self.lock_no_img(ZHUCAIDAN_BTN["bangzhu"], elseclick=[(871, 513), (165, 411), (591, 369), (678, 377)])
            self.lock_no_img('img/ok.bmp', elseclick=[(591, 369)], at=(495, 353, 687, 388))

            try_count = 0
            self.log.write_log("info", "进入login函数")
            while True:
                self._move_check()
                try_count += 1
                if try_count % 5 == 0 and try_count > 10:
                    # 看一下会不会一直点右上角？
                    try:
                        screen_shot_ = self.getscreen()
                        r_list = self.img_where_all(img=MAIN_BTN["guanbi"], screen=screen_shot_)
                        if self.lock_no_img(img=MAIN_BTN["guanbi"], elseclick=(int(r_list[0]), int(r_list[1])),
                                            side_check=self.juqing_kkr):
                            # time.sleep(6)
                            continue
                    except:
                        pass
                    if self.is_exists(MAIN_BTN["liwu"]):
                        # 已经登陆了老哥！
                        # 重 新 来 过
                        self.log.write_log("error", "可能出现了狂点右上角错误，换号")
                        self.lock_img(MAIN_BTN["liwu"], elseclick=MAIN_BTN["zhuye"], elsedelay=1)  # 回首页
                        self.change_acc()
                if try_count > 100:
                    # 点了100次了，重启吧
                    error_flag = 1
                    raise Exception("点了100次右上角了，重启罢！")

                # if self.d(resourceId="com.bilibili.priconne:id/unitySurfaceView").exists():
                #     self.d(resourceId="com.bilibili.priconne:id/unitySurfaceView").click()

                # 看到切账号大头了就可以break了
                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_wel_change").click()
                    self.log.write_log("info", "测试点002")
                    time.sleep(10)
                    break
                '''
                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_other").exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_other").click()
                    time.sleep(2)
                    self.log.write_log("info", "测试点001")
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").exists():
                    self.d(resourceId="com.bilibili.priconne:id/tv_gsc_record_login_change").click()
                    time.sleep(2)
                    self.log.write_log("info", "测试点003")
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").exists():
                    if self.d(resourceId="com.bilibili.priconne:id/tv_gsc_phone_terms").exists():
                        if not self.is_exists(START_UI["gouxuan"]):
                            self.lock_img(START_UI["gouxuan"], elseclick=(293, 424), elsedelay=1, retry=2)
                    self.d(resourceId="com.bilibili.priconne:id/iv_gsc_account_login").click()
                    self.log.write_log("info", "测试点004")
                    time.sleep(2)
                    continue
                if self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").exists():
                    self.d(resourceId="com.bilibili.priconne:id/et_gsc_account").click()
                    break
                '''
                if self.d(text="Geetest").exists() or self.d(description="Geetest").exists():
                    self.click(687, 72)
                    # 防止卡验证码
                    continue
                if self.d(text="请滑动阅读协议内容").exists() or self.d(description="请滑动阅读协议内容").exists():
                    if debug:
                        self.log.write_log('debug', "发现协议")
                    try:
                        r = self.img_where_all(START_UI["xieyihuakuai"], threshold=0.99)
                        self.d.touch.down(r[0], r[1]).sleep(1).up(r[0], r[1])
                    except:
                        # 退化成老办法
                        self.d.touch.down(808, 324).sleep(1).up(808, 324)
                        self.d.touch.down(808, 353).sleep(1).up(808, 353)
                    if self.d(text="请滑动阅读协议内容").exists():
                        self.d(text="同意").click()
                    if self.d(description="请滑动阅读协议内容").exists():
                        # 雷电三
                        self.d(description="同意").click()
                    # time.sleep(6)
                else:
                    # self.click(812, 345)  # 20230215新协议
                    self.click(560, 430)  # 原本是945 13
                    self.click(678, 377)  # 下载
            self.log.write_log("info", "进入do_login")
            return self.do_login(ac, pwd)
        except Exception as e:
            # if error_flag:
            #     raise e
            # # 异常重试登陆逻辑
            # return self.login(ac, pwd)  # 修改无限重复BUG
            raise e  # 应该报错的时候就应该报错，上面会处理的。

    @DEBUG_RECORD
    def auth(self, auth_name, auth_id):
        """
        项目地址:https://github.com/bbpp222006/Princess-connection
        作者：bbpp222006
        协议：MIT License
        :param auth_name:
        :param auth_id:
        :return:
        """

        ORIGIN_MODE = True  # css炸裂之前的版本，设置为True后应付CSS炸裂之后的版本

        if ORIGIN_MODE:
            if self.d(textContains="还剩1次实名认证机会").exists():
                self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                raise Exception("实名仅剩1次验证机会了！")
            time.sleep(5)
            self._move_check()
            # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_name").click()
            self.click(464, 205)
            # self.d.xpath(
            #     '//android.widget.RelativeLayout/android.webkit.WebView[1]/android.webkit.WebView[1]/android.view.View['
            #     '1]/android.view.View[1]/android.view.View[4]/android.widget.EditText[1]').click()
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_name))
            self._move_check()
            self.click(464, 280)
            # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_edit_authentication_id_number").click()
            # self.d.xpath(
            #     '//android.widget.RelativeLayout/android.webkit.WebView[1]/android.webkit.WebView[1]/android.view.View['
            #     '1]/android.view.View[1]/android.view.View[4]/android.widget.EditText[2]').click()
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_id))
            self._move_check()
            if self.d(text="提交实名").exists():
                self.d.xpath('//*[@text="提交实名"]').click()
                # self.d(resourceId="com.bilibili.priconne:id/bsgamesdk_authentication_submit").click()
                self._move_check()
                # self.d(resourceId="com.bilibili.priconne:id/bagamesdk_auth_success_comfirm").click()

            if self.d(text="我知道了").exists():
                self._move_check()
                self.d(text="我知道了").click()
                time.sleep(3)
            else:
                # 阿B实名界面有两个。。。xpath在u2全局查找元素点击上有adb爆炸的bug，先用这个凑合着吧
                if self.d(textContains="还剩1次实名认证机会").exists():
                    self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                    raise Exception("实名仅剩1次验证机会了！")
                time.sleep(5)
                self._move_check()
                self.click(464, 285)
                self._move_check()
                self.d.clear_text()
                self._move_check()
                self.d.send_keys(str(auth_name))
                self._move_check()
                self.click(464, 360)
                self._move_check()
                self.d.clear_text()
                self._move_check()
                self.d.send_keys(str(auth_id))
                self._move_check()
                self.d.xpath('//*[@text="提交实名"]').click()
                self._move_check()
                self.d(text="我知道了").click()
        else:

            # CSS炸裂，变大
            if self.d(textContains="还剩1次实名认证机会").exists():
                self.log.write_log("error", message='%s账号实名仅剩1次验证机会了！' % self.account)
                raise Exception("实名仅剩1次验证机会了！")
            time.sleep(5)
            self._move_check()
            self.d.drag(827, 488, 827, 80, 0.1)
            self._move_check()
            self.d.drag(827, 488, 827, 80, 0.1)
            self.click(431, 91)
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_name))
            self._move_check()
            self.click(460, 217)
            self._move_check()
            self.d.clear_text()
            self._move_check()
            self.d.send_keys(str(auth_id))
            self._move_check()
            self.click(469, 364)  # 提交实名
            time.sleep(3)
            self.click(475, 407)

    @timeout(300, "login_auth登录超时，超过5分钟")
    @DEBUG_RECORD
    def login_auth(self, ac, pwd):

        # CreatIDnum() 可能阿B升级了验证，不推荐使用了，没有合法性校验
        need_auth = self.login(ac=ac, pwd=pwd)
        if need_auth == -1:  # 这里漏了一句，无法检测验证码。
            return -1
        if need_auth == 1:
            if use_my_id:
                real_id = AutomatorRecorder.load("./idcard.json")
                id_list = list(real_id.keys())
                count = random.randint(0, len(id_list) - 1)
                self.auth(auth_name=id_list[count], auth_id=real_id[id_list[count]])
            else:
                birthday = str(random.randint(1970, 1999))
                auth_name, auth_id = random_name(), validator.fake_id(birthday=birthday)
                self.auth(auth_name=auth_name, auth_id=auth_id)

    @DEBUG_RECORD
    def change_acc(self):  # 切换账号
        self.log.write_log("info", message=f'本来是切换账号{self.account}的入口，被我魔改辣--0x114514BB')
        #self.get_zhuye().goto_zhucaidan().back_title().OK()
        # 设备匿名
        #self.phone_privacy()
        # pcr_log(self.account).write_log(level='info', message='%s账号完成任务' % self.account)
        # pcr_log(self.account).server_bot("warning", "%s账号完成任务" % self.account)
