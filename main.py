import flet as ft
import datetime

# 运动消耗系数库 (METs)
MET_DICT = {
    "跑步": 8.0, "力量训练": 5.0, "骑车": 6.0, 
    "游泳": 7.0, "瑜伽": 3.0, "走路": 3.5, "跳绳": 10.0
}

def main(page: ft.Page):
    page.title = "智能健身管家"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ==================== 数据处理模块 ====================
    def get_profile():
        return page.client_storage.get("user_profile")

    def save_profile(gender, age, height, weight):
        # 使用 Mifflin-St Jeor 公式计算基础代谢 (BMR) 并估算日常消耗目标
        if gender == "男":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        target_cal = int(bmr * 1.5) # 假设中度活动量
        
        profile = {
            "gender": gender, "age": age, "height": height, 
            "weight": weight, "target": target_cal
        }
        page.client_storage.set("user_profile", profile)
        return profile

    def get_daily_data(date_str):
        data = page.client_storage.get(f"day_{date_str}")
        if not data:
            return {"workouts": [], "total_cal": 0}
        return data

    def save_workout(date_str, exercise_type, duration_min):
        profile = get_profile()
        weight = profile["weight"]
        # 计算消耗公式：MET * 体重(kg) * 时间(小时)
        met = MET_DICT[exercise_type]
        calories_burned = int(met * weight * (duration_min / 60))
        
        day_data = get_daily_data(date_str)
        day_data["workouts"].append({
            "type": exercise_type,
            "duration": duration_min,
            "calories": calories_burned
        })
        day_data["total_cal"] += calories_burned
        page.client_storage.set(f"day_{date_str}", day_data)

    # ==================== UI 刷新逻辑 ====================
    selected_date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    def refresh_dashboard():
        profile = get_profile()
        day_data = get_daily_data(selected_date_str)
        
        target = profile["target"]
        consumed = day_data["total_cal"]
        workout_count = len(day_data["workouts"])
        
        # 更新仪表盘数据
        target_text.value = f"目标消耗: {target} 千卡"
        consumed_text.value = f"已消耗: {consumed} 千卡"
        progress_ring.value = min(consumed / target, 1.0) if target > 0 else 0
        
        # 更新日历状态文本
        date_display.value = selected_date_str
        if workout_count == 0:
            status_text.value = "🔴 今日未健身"
            status_text.color = "red"
        else:
            status_text.value = f"🟢 今日已健身 (共 {workout_count} 次)"
            status_text.color = "green"
            
        # 更新运动清单
        history_list.controls.clear()
        if workout_count == 0:
            history_list.controls.append(ft.Text("还没有运动记录，快去动起来吧！", color="grey"))
        else:
            for w in day_data["workouts"]:
                history_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.FITNESS_CENTER),
                        title=ft.Text(f"{w['type']} - {w['duration']}分钟"),
                        trailing=ft.Text(f"🔥 {w['calories']} 千卡", color="orange", weight="bold")
                    )
                )
        page.update()

    # ==================== 视图 1：首次档案设置 ====================
    gender_drop = ft.Dropdown(options=[ft.dropdown.Option("男"), ft.dropdown.Option("女")], label="性别")
    age_input = ft.TextField(label="年龄", keyboard_type="number")
    height_input = ft.TextField(label="身高 (cm)", keyboard_type="number")
    weight_input = ft.TextField(label="体重 (kg)", keyboard_type="number")

    def on_submit_profile(e):
        if all([gender_drop.value, age_input.value, height_input.value, weight_input.value]):
            save_profile(
                gender_drop.value, int(age_input.value),
                float(height_input.value), float(weight_input.value)
            )
            page.views.pop()
            page.go("/main")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("请填完所有基础信息哦！"))
            page.snack_bar.open = True
            page.update()

    profile_view = ft.View(
        "/profile",
        [
            ft.Text("欢迎来到智能健身", size=30, weight="bold"),
            ft.Text("为了精准计算热量，请告诉我你的身体密码：", color="grey"),
            gender_drop, age_input, height_input, weight_input,
            ft.ElevatedButton("生成我的专属健身计划", on_click=on_submit_profile, width=float("inf"), bgcolor="blue", color="white")
        ]
    )

    # ==================== 视图 2：主界面 ====================
    # 仪表盘 UI
    progress_ring = ft.ProgressRing(width=100, height=100, stroke_width=10, color="orange")
    target_text = ft.Text(size=14, color="grey")
    consumed_text = ft.Text(size=20, weight="bold")
    
    dashboard_card = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Row([
                progress_ring,
                ft.Column([consumed_text, target_text])
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
        )
    )

    # 录入运动 UI
    exercise_drop = ft.Dropdown(
        label="做了什么运动？",
        options=[ft.dropdown.Option(k) for k in MET_DICT.keys()],
        expand=1
    )
    duration_input = ft.TextField(label="多少分钟？", keyboard_type="number", expand=1)

    def on_add_workout(e):
        if exercise_drop.value and duration_input.value:
            save_workout(selected_date_str, exercise_drop.value, int(duration_input.value))
            exercise_drop.value = None
            duration_input.value = ""
            refresh_dashboard()
            page.snack_bar = ft.SnackBar(ft.Text("✅ 记录成功，热量已更新！"))
            page.snack_bar.open = True
            page.update()

    # 日历与状态 UI
    date_display = ft.Text(size=20, weight="bold")
    status_text = ft.Text(size=16)
    history_list = ft.Column()

    def on_date_change(e):
        nonlocal selected_date_str
        selected_date_str = e.control.value.strftime("%Y-%m-%d")
        refresh_dashboard()

    date_picker = ft.DatePicker(on_change=on_date_change)
    page.overlay.append(date_picker)

    main_view = ft.View(
        "/main",
        [
            # 顶部仪表盘
            ft.Text("📊 今日消耗看板", size=18, weight="bold"),
            dashboard_card,
            ft.Divider(height=20, thickness=1),
            
            # 中部：添加运动
            ft.Text("➕ 记一笔运动", size=18, weight="bold"),
            ft.Row([exercise_drop, duration_input]),
            ft.ElevatedButton("计算并打卡", icon=ft.icons.BOLT, on_click=on_add_workout, width=float("inf"), bgcolor="black", color="white"),
            ft.Divider(height=20, thickness=1),
            
            # 底部：历史日历
            ft.Row([
                ft.Text("📅 打卡日历", size=18, weight="bold"),
                ft.IconButton(icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: date_picker.pick_date(), icon_color="blue")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            date_display,
            status_text,
            ft.Container(
                content=history_list, padding=10, bgcolor="#F5F5F5", border_radius=10
            )
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # ==================== 路由控制 ====================
    def route_change(route):
        page.views.clear()
        if not get_profile():
            page.views.append(profile_view)
        else:
            page.views.append(main_view)
            refresh_dashboard()
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

ft.app(target=main)
