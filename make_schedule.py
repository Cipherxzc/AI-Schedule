import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.cm as cm

# 读取JSON文件
def load_schedule_from_file(schedule_path):
    with open(schedule_path, 'r') as file:
        schedule = json.load(file)
    return schedule

# 定义将时间字符串转为分钟数的函数
def time_to_minutes(time_str):
    t = datetime.strptime(time_str, "%H:%M")
    return (t.hour - 6) * 60 + t.minute  # 假设时间轴从6:00开始

# 创建 occupied 数组，用于标记某一天的每分钟是否已经被占用
def initialize_occupied():
    return [[False] * (16 * 60) for _ in range(7)]  # 每天有16小时（6:00 - 22:00），共960分钟

# 检查给定的时间段是否与已有事件冲突
def is_time_available(occupied, day_idx, start_time, end_time):
    return all(not occupied[day_idx][minute] for minute in range(start_time, end_time))

# 将事件时间段标记为已占用
def mark_time_as_occupied(occupied, day_idx, start_time, end_time):
    for minute in range(start_time, end_time):
        occupied[day_idx][minute] = True

# 处理计划表数据并渲染
def render_schedule(schedule, image_path):
    occupied = initialize_occupied()  # 初始化 occupied 数组
    event_color_map = {}  # 记录每个事件的颜色映射

    # 准备数据
    events = []
    fig, ax = plt.subplots(figsize=(12, 8))
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = {day: idx for idx, day in enumerate(days_of_week)}

    # 获取当前日期和本周的周一日期
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # 处理一次性事件
    for event in schedule["oneTimeEvents"]:
        event_date_str = event["date"]
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d")  # 将字符串转换为datetime对象
        if start_of_week <= event_date <= end_of_week:
            start_time = time_to_minutes(event["startTime"])
            end_time = time_to_minutes(event["endTime"])
            day_idx = event_date.weekday()  # 获取事件所在的星期几

            if is_time_available(occupied, day_idx, start_time, end_time):
                mark_time_as_occupied(occupied, day_idx, start_time, end_time)
                events.append({
                    'eventName': event['eventName'],
                    'date': event_date,
                    'startTime': start_time,
                    'endTime': end_time
                })

    # 处理每周重复事件
    for event in schedule["weeklyRecurringEvents"]:
        start_time = time_to_minutes(event["startTime"])
        end_time = time_to_minutes(event["endTime"])
        for day in event["daysOfWeek"]:
            day_idx = day_labels[day]
            event_date = start_of_week + timedelta(days=day_idx)

            if is_time_available(occupied, day_idx, start_time, end_time):
                mark_time_as_occupied(occupied, day_idx, start_time, end_time)
                events.append({
                    'eventName': event['eventName'],
                    'date': event_date,
                    'startTime': start_time,
                    'endTime': end_time
                })

    # 处理每日重复事件
    for event in schedule["dailyRecurringEvents"]:
        start_time = time_to_minutes(event["startTime"])
        end_time = time_to_minutes(event["endTime"])
        for day in range(7):  # 每天都安排这些事件
            event_date = start_of_week + timedelta(days=day)

            if is_time_available(occupied, day, start_time, end_time):
                mark_time_as_occupied(occupied, day, start_time, end_time)
                events.append({
                    'eventName': event['eventName'],
                    'date': event_date,
                    'startTime': start_time,
                    'endTime': end_time
                })

    # 创建 DataFrame
    df = pd.DataFrame(events)

    # 绘制每个事件
    colors = plt.get_cmap('tab20', len(df))  # 使用颜色映射
    for idx, event in df.iterrows():
        event_name = event['eventName']
        start_time = event['startTime']
        end_time = event['endTime']
        event_date = event['date'].weekday()

        # 检查该事件是否已被匹配过颜色
        if event_name in event_color_map:
            event_color = event_color_map[event_name]
        else:
            # 为事件分配新颜色，并存储到字典中
            event_color = colors(idx)
            event_color_map[event_name] = event_color

        # 渲染事件方块
        ax.fill_betweenx(
            [start_time, end_time],
            event_date - 0.5,
            event_date + 0.5,
            color=event_color,
            alpha=0.6
        )
        ax.text(
            event_date,
            (start_time + end_time) / 2,
            event_name,
            ha='center',
            va='center',
            color='black',
            fontsize=9,
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
        )

    # 设置x轴为星期几
    ax.set_xlim(-0.5, 6.5)
    ax.set_xticks(range(7))
    ax.set_xticklabels(days_of_week)

    # 设置y轴为时间（6:00 - 22:00）
    ax.set_yticks(range(0, 16 * 60, 60))  # 每小时显示一个刻度
    ax.set_yticklabels([f"{i}:00" for i in range(6, 22)])
    ax.set_ylim(16 * 60, 0)  # 使 y 轴从上到下排列

    # 设置标签和标题
    ax.set_ylabel("Time of Day")
    ax.set_xlabel("Day of the Week")
    ax.set_title("Weekly Schedule")

    plt.grid(True, axis='y')
    plt.tight_layout()

    # 预留空白区域并设置日期
    fig.subplots_adjust(top=0.85)  # 将图表向下调整，留出顶部空间
    for day_idx in range(7):
        event_date = start_of_week + timedelta(days=day_idx)
        # 在 x 轴上方的位置（每一天的中心）添加日期文本
        ax.text(day_idx, -100, event_date.strftime('%Y-%m-%d'),
            ha='center', va='bottom', fontsize=10, color='black')

    # 显示图表
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # 为标题留出更多空间
    # plt.show()

    plt.savefig(image_path)
    plt.close(fig)

schedule_path = r"./data/schedule.json"  # 使用 r 来避免转义字符
image_path = r"./data/schedule.png"

def make_schedule():
    schedule = load_schedule_from_file(schedule_path)
    render_schedule(schedule, image_path)

if __name__ == "__main__":
    make_schedule()