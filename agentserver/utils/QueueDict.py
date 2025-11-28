from collections import deque


class QueueDict:
    def __init__(self):
        # 初始化一个空字典，用于存储队列
        self.queues = {}

    def add_queue(self, key):
        """
        添加一个新的队列到字典中
        :param key: 队列的键名
        """
        if key not in self.queues:
            # 创建一个最大长度为20的双端队列
            self.queues[key] = deque(maxlen=10)

    def enqueue(self, key, value):
        """
        向指定队列中添加元素
        :param key: 队列的键名
        :param value: 要添加的值
        """
        if key not in self.queues:
            # 如果队列不存在，先创建
            self.add_queue(key)
        # 添加元素到队列右侧（尾部）
        self.queues[key].append(value)

    def dequeue(self, key):
        """
        从指定队列中取出元素
        :param key: 队列的键名
        :return: 取出的元素，如果队列为空返回None
        """
        if key not in self.queues:
            return None
        try:
            # 从队列左侧（头部）取出元素
            return self.queues[key].popleft()
        except IndexError:
            # 队列为空
            return None

    def get_queue(self, key):
        """
        获取指定队列的所有元素（不改变原队列）
        :param key: 队列的键名
        :return: 队列元素的列表，如果队列不存在返回None
        """
        if key not in self.queues:
            return None
        return list(self.queues[key])

    def size(self, key):
        """
        获取指定队列的当前大小
        :param key: 队列的键名
        :return: 队列大小，如果队列不存在返回0
        """
        if key not in self.queues:
            return 0
        return len(self.queues[key])
