import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 读取日程表数据
with open('schedule.json', 'r') as file:
    schedule = json.load(file)

# 获取当前日期和本周的周一日期
today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

# 准备数据
events = []

# 处理 dailyRecurringEvents
for event in schedule['dailyRecurringEvents']:
    for i in range(7):
        event_date = start_of_week + timedelta(days=i)
        events.append({
            'eventName': event['eventName'],
            'date': event_date,
            'startTime': datetime.strptime(event['startTime'], '%H:%M').time(),
            'endTime': datetime.strptime(event['endTime'], '%H:%M').time()
        })

# 处理 weeklyRecurringEvents
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
for event in schedule['weeklyRecurringEvents']:
    for day in event['daysOfWeek']:
        event_date = start_of_week + timedelta(days=days_of_week.index(day))
        events.append({
            'eventName': event['eventName'],
            'date': event_date,
            'startTime': datetime.strptime(event['startTime'], '%H:%M').time(),
            'endTime': datetime.strptime(event['endTime'], '%H:%M').time()
        })

# 处理 oneTimeEvents
for event in schedule['oneTimeEvents']:
    event_date = datetime.strptime(event['date'], '%Y-%m-%d')
    if start_of_week <= event_date <= end_of_week:
        events.append({
            'eventName': event['eventName'],
            'date': event_date,
            'startTime': datetime.strptime(event['startTime'], '%H:%M').time(),
            'endTime': datetime.strptime(event['endTime'], '%H:%M').time()
        })

# 创建 DataFrame
df = pd.DataFrame(events)

# 设置图形
fig, ax = plt.subplots(figsize=(12, 8))

# 设置 x 轴和 y 轴的刻度
ax.set_xticks([start_of_week + timedelta(days=i) for i in range(7)])
ax.set_xticklabels([days_of_week[i] for i in range(7)])
ax.set_yticks([i for i in range(24)])
ax.set_yticklabels([f'{i:02d}:00' for i in range(24)])
ax.invert_yaxis()  # 反转 y 轴
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# 绘制每个事件
colors = plt.get_cmap('tab20', len(df))  # 使用颜色映射
for idx, event in df.iterrows():
    start_time = event['startTime'].hour + event['startTime'].minute / 60.0
    end_time = event['endTime'].hour + event['endTime'].minute / 60.0
    event_date = event['date']
    ax.fill_betweenx(
        [start_time, end_time],
        event_date - timedelta(hours=6),
        event_date + timedelta(hours=6),
        color=colors(idx),
        alpha=0.6
    )
    ax.text(
        event_date,
        (start_time + end_time) / 2,
        event['eventName'],
        ha='center',
        va='center',
        color='black',
        fontsize=9,
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
    )

# 设置轴标签和标题
ax.set_xlabel('Date')
ax.set_ylabel('Time')
ax.set_title('Weekly Schedule', fontsize=20, pad=40)  # 放大标题并增加间距

# 增加顶部的日期标签
for i in range(7):
    date_label = (start_of_week + timedelta(days=i)).strftime('%m/%d')
    ax.text(
        start_of_week + timedelta(days=i),
        0,  # 放在紧贴图表的位置
        date_label,
        ha='center',
        va='top',
        fontsize=10,
        fontweight='bold'
    )

# 调整布局
plt.tight_layout(rect=[0, 0, 1, 0.95])  # 为标题留出更多空间
plt.show()
