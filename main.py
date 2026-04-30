import flet as ft
import datetime
import traceback

# 运动消耗系数库 (METs)
MET_DICT = {
    "跑步": 8.0, "力量训练": 5.0, "骑车": 6.0, 
    "游泳": 7.0, "瑜伽": 3.0, "走路": 3.5, "跳绳": 10.0
}

def main(page: ft.Page):
    # 【防弹衣机制】如果发生任何错误，拦截它，不要白屏！
    try:
        page.title = "智能健身管家"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.scroll = ft.ScrollMode.AUTO
        page.padding = 20

        # 安全的状态管理：使用字典避免安卓环境下的作用域崩溃
        app_state = {
            "selected_date": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        # ----- 数据读取 -----
        def get_profile():
            return page.client_storage.get("user_profile")

        def get_daily_data(date_str):
            data = page.client_storage.get(f"day_{date_str}")
            return data if data else {"workouts": [], "total_cal": 0}

        # ----- UI 组件预定义 -----
        progress_ring = ft.ProgressRing(width=80, height=80, stroke_width=8, color="orange", value=0)
        consumed_text = ft.Text("已消耗: 0 千卡", size=20, weight="bold")
        target_text = ft.Text("目标消耗: --", size=14, color="grey")
        status_text = ft.Text("", size=16, weight="bold")
        history_list = ft.Column()
        date_display = ft.Text(app_state["selected_date"], size=18, weight="bold", color="blue")

        # ----- 刷新界面逻辑 -----
        def refresh_ui():
            profile = get_profile()
            if not profile: return
            
            date_str = app_state["selected_date"]
            date_display.value = f"选定日期: {date_str}"
            
            day_data = get_daily_data(date_str)
            target = profile.get("target", 2000)
            consumed = day_data["total_cal"]
            
            consumed_text.value = f"已消耗: {consumed} 千卡"
            target_text.value = f"目标消耗: {target} 千卡"
            progress_ring.value = min(consumed / target, 1.0) if target > 0 else 0
            
            count = len(day_data["workouts"])
            status_text.value = f"🟢 今日健身 {count} 次" if count > 0 else "🔴 今日未健身"
            status_text.color = "green" if count > 0 else "red"
            
            history_list.controls.clear()
            for w in day_data["workouts"]:
                history_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CHECK_CIRCLE, color="green"),
                        title=ft.Text(f"{w['type']} {w['duration']}分钟"), 
                        trailing=ft.Text(f"🔥 {w['calories']} 千卡", weight="bold")
                    )
                )
            page.update()

        # ----- 视图 1：档案设置页 -----
        def show_profile_setup():
            page.clean()
            gender_drop = ft.Dropdown(label="性别", options=[ft.dropdown.Option("男"), ft.dropdown.Option("女")])
            weight_input = ft.TextField(label="体重 (kg)", keyboard_type="number")
            
            def save_and_go(e):
                if gender_drop.value and weight_input.value:
                    try:
                        w = float(weight_input.value)
                        target = int(w * 33) # 估算每日目标消耗
                        page.client_storage.set("user_profile", {"gender": gender_drop.value, "weight": w, "target": target})
                        show_main_page()
                    except ValueError:
                        # 防止输入非数字导致崩溃
                        page.snack_bar = ft.SnackBar(ft.Text("⚠️ 体重必须填写数字！"))
                        page.snack_bar.open = True
                        page.update()
                
            page.add(
                ft.Text("欢迎！请先设置身体档案", size=24, weight="bold"),
                gender_drop, weight_input,
                ft.ElevatedButton("保存并开始使用", on_click=save_and_go, width=float("inf"), bgcolor="blue", color="white")
            )

        # ----- 视图 2：主功能页 -----
        def show_main_page():
            page.clean()
            ex_drop = ft.Dropdown(label="运动项目", options=[ft.dropdown.Option(k) for k in MET_DICT.keys()], expand=2)
            dur_input = ft.TextField(label="多少分钟", keyboard_type="number", expand=1)
            
            def add_event(e):
                if ex_drop.value and dur_input.value:
                    try:
                        dur = int(dur_input.value)
                        profile = get_profile()
                        met = MET_DICT[ex_drop.value]
                        cal = int(met * profile["weight"] * (dur/60))
                        
                        date_str = app_state["selected_date"]
                        data = get_daily_data(date_str)
                        data["workouts"].append({"type": ex_drop.value, "duration": dur, "calories": cal})
                        data["total_cal"] += cal
                        page.client_storage.set(f"day_{date_str}", data)
                        
                        ex_drop.value = None
                        dur_input.value = ""
                        refresh_ui()
                    except ValueError:
                        page.snack_bar = ft.SnackBar(ft.Text("⚠️ 时间必须填写整数数字！"))
                        page.snack_bar.open = True
                        page.update()
            
            def on_date_picked(e):
                app_state["selected_date"] = e.control.value.strftime("%Y-%m-%d")
                refresh_ui()

            dp = ft.DatePicker(on_change=on_date_picked)
            page.overlay.append(dp)

            page.add(
                ft.Text("📊 消耗看板", size=20, weight="bold"),
                ft.Container(
                    padding=15, bgcolor="#F5F5F5", border_radius=15,
                    content=ft.Row([progress_ring, ft.Column([consumed_text, target_text])])
                ),
                ft.Divider(height=20),
                ft.Row([ex_drop, dur_input]),
                ft.ElevatedButton("打卡计算热量", icon=ft.icons.BOLT, on_click=add_event, width=float("inf"), bgcolor="black", color="white"),
                ft.Divider(height=20),
                ft.Row([
                    ft.Text("📅 日历与记录", size=18, weight="bold"), 
                    ft.IconButton(ft.icons.CALENDAR_MONTH, icon_color="blue", on_click=lambda _: dp.pick_date())
                ], alignment="spaceBetween"),
                date_display,
                status_text,
                history_list
            )
            refresh_ui()

        # ----- 启动检查 -----
        if not get_profile():
            show_profile_setup()
        else:
            show_main_page()

    except Exception as e:
        # 黑匣子：如果崩溃，清空屏幕，把红色警告和错误代码印上去
        page.clean()
        page.add(
            ft.Text("🚨 糟糕，程序遇到了问题！", color="red", weight="bold", size=24),
            ft.Text("请截图发给开发人员：", weight="bold"),
            ft.Text(traceback.format_exc(), size=12, color="grey")
        )

ft.app(target=main)
