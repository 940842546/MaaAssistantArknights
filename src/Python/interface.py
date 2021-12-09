import ctypes
import os
import json
import pathlib
from message import Message


class Asst:
    CallBackType = ctypes.CFUNCTYPE(
        None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)
    """
    回调函数，使用实例可参照my_callback

    :params:
        ``param1 message``: 消息类型
        ``param2 details``: gbk json string
        ``param3 arg``:     自定义参数
    """

    def __init__(self, dirname: str, callback: CallBackType, arg=None):
        """
        :params:
            ``dirname``:    DLL及资源所在文件夹路径
            ``callback``:   回调函数
            ``arg``:        自定义参数
        """
        self.__dllpath = pathlib.Path(dirname) / 'MeoAssistance.dll'
        self.__dll = ctypes.WinDLL(str(self.__dllpath))

        self.__dll.AsstCreateEx.restype = ctypes.c_void_p
        self.__dll.AsstCreateEx.argtypes = (ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p,)
        self.__ptr = self.__dll.AsstCreateEx(dirname.encode('utf-8'), callback, arg)

    def __del__(self):
        self.__dll.AsstDestroy.argtypes = (ctypes.c_void_p,)
        self.__dll.AsstDestroy(self.__ptr)

    def catch_default(self) -> bool:
        """
        连接配置文件中的默认选项（模拟器or安卓手机）

        :return: 是否连接成功
        """
        self.__dll.AsstCatchDefault.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstCatchDefault(self.__ptr)

    def catch_emulator(self) -> bool:
        """
        连接模拟器

        :return: 是否连接成功
        """
        self.__dll.AsstCatchEmulator.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstCatchEmulator(self.__ptr)

    def catch_custom(self, address: str) -> bool:
        """
        连接自定义设备

        :return: 是否连接成功
        """
        self.__dll.AsstCatchCustom.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p,)
        return self.__dll.AsstCatchCustom(self.__ptr, address.encode('utf-8'))

    def append_fight(self, max_medicine: int, max_stone: int, max_times: int) -> bool:
        """
        添加刷理智任务

        :params:
            ``max_medicine``:       最多吃多少理智药
            ``max_stone``:          最多吃多少源石
            ``max_times``:          最多刷多少
        """
        self.__dll.AsstAppendFight.argtypes = (
            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int,)
        return self.__dll.AsstAppendFight(self.__ptr, max_medicine, max_stone, max_times)

    def append_award(self) -> bool:
        """
        添加领取每日奖励任务
        """
        self.__dll.AsstAppendAward.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstAppendAward(self.__ptr)

    def append_visit(self) -> bool:
        """
        添加访问好友任务
        """
        self.__dll.AsstAppendVisit.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstAppendVisit(self.__ptr)

    def append_mall(self, with_shopping: bool) -> bool:
        """
        添加信用商店任务

        :params:
            ``with_shopping``:    是否信用商店购物
        """
        self.__dll.AsstAppendMall.argtypes = (ctypes.c_void_p, ctypes.c_bool)
        return self.__dll.AsstAppendMall(self.__ptr, with_shopping)

    def append_infrast(self, work_mode: int, order_list: list, uses_of_drones: str, dorm_threshold: float) -> bool:
        """
        添加基建任务

        :params:
            ``work_mode``:          工作模式，当前仅支持传 1
            ``order_list``:         换班顺序，str list，例如 [ "Mfg", "Trade", "Control", "Power", "Reception", "Office", "Dorm"]
            ``uses_of_drones``:     无人机用途，支持以下之一："_NotUse"、"Money"、"SyntheticJade"、"CombatRecord"、"PureGold"、"OriginStone"、"Chip"
            ``dorm_threshold``:     宿舍心情阈值，取值 [0, 1.0]
        """
        order_byte_list = []

        for item in order_list:
            order_byte_list.append(item.encode('utf-8'))

        order_len = len(order_byte_list)
        order_arr = (ctypes.c_char_p * order_len)()
        order_arr[:] = order_byte_list

        self.__dll.AsstAppendInfrast.argtypes = (
            ctypes.c_void_p, ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p), ctypes.c_int,
            ctypes.c_char_p, ctypes.c_double,)
        return self.__dll.AsstAppendInfrast(self.__ptr, work_mode,
                                            order_arr, order_len,
                                            uses_of_drones.encode('utf-8'), dorm_threshold)

    def append_recruit(self, max_times: int, select_level: list, confirm_level: list, need_refresh: bool) -> bool:
        """
        添加自动公招任务

        :params:
            ``max_times``:       自动公招次数
            ``select_level``:    要点击的Tags等级（例如3级Tags不选也可以直接确认），int list
            ``confirm_level``:   要确认开始招募的Tags等级，int list
            ``need_refresh``:    是否刷新3级Tags
        """
        select_len = len(select_level)
        select_arr = (ctypes.c_int * select_len)()
        select_arr[:] = select_level

        confirm_len = len(confirm_level)
        confirm_arr = (ctypes.c_int * confirm_len)()
        confirm_arr[:] = confirm_level

        self.__dll.AsstAppendRecruit.argtypes = (
            ctypes.c_void_p, ctypes.c_int,
            ctypes.POINTER(ctypes.c_int), ctypes.c_int,
            ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_bool,)
        return self.__dll.AsstAppendRecruit(self.__ptr, max_times,
                                            select_arr, select_len,
                                            confirm_arr, confirm_len, need_refresh)

    def start(self) -> bool:
        """
        开始任务
        """
        self.__dll.AsstStart.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstStart(self.__ptr)

    def start_recurit_calc(self, select_level: list, set_time: bool) -> bool:
        """
        进行公招计算

        :params:
            ``select_level``:    要点击的Tags等级，int list
            ``set_time``:        是否要点击9小时
        """
        select_len = len(select_level)
        select_arr = (ctypes.c_int * select_len)()
        select_arr[:] = select_level

        self.__dll.AsstStartRecruitCalc.argtypes = (
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_bool,)
        return self.__dll.AsstStartRecruitCalc(self.__ptr, select_arr, select_len, set_time)

    def stop(self) -> bool:
        """
        停止并清空所有任务
        """
        self.__dll.AsstStop.argtypes = (ctypes.c_void_p,)
        return self.__dll.AsstStop(self.__ptr)

    def set_penguin_id(self, id: str) -> bool:
        """
        设置企鹅物流ID

        :params:
            ``id``:     企鹅物流ID，仅数字部分
        """
        self.__dll.AsstSetPenguinId.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p)
        return self.__dll.AsstSetPenguinId(self.__ptr, id.encode('utf-8'))

    def get_version(self) -> str:
        """
        获取DLL版本号

        :return: 版本号
        """
        self.__dll.AsstGetVersion.restype = ctypes.c_char_p
        return self.__dll.AsstGetVersion().decode('utf-8')


if __name__ == "__main__":

    @Asst.CallBackType
    def my_callback(msg, details, arg):
        d = json.loads(details.decode('gbk'))
        print(Message(msg), d, arg)

    dirname: str = (pathlib.Path.cwd().parent.parent / 'x64' / 'Release').__str__()
    asst = Asst(dirname=dirname, callback=my_callback)

    print('version', asst.get_version())

    if asst.catch_default():
        print('连接成功')
    else:
        print('连接失败')
        os.system.exit()

    # asst.append_fight(0, 0, 1)
    asst.append_infrast(1, [ "Mfg", "Trade", "Control", "Power", "Reception", "Office", "Dorm"], "Money", 0.3)
    # asst.append_award()
    asst.start()

    # asst.start_recurit_clac([4, 5, 6], True)

    while True:
        pass
