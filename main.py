import flet as ft
import datetime

def main(page: ft.Page):
    page.title = "我的健身日历"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    selected_date = ft.Text(
        value=datetime.datetime.now().strftime("%Y-%m-%d"),
        size=24,
        weight="bold",
        color="blue"
    )

    history_text = ft.Text(value="这一天还没有记录哦...", italic=True, color="grey")

    note_input = ft.TextField(
        label="训练备注 (如：跑步3km / 胸背训练)",
        multiline=True,
        min_lines=3
    )

    def load_data(date_str):
        saved_note = page.client_storage.get(date_str)
        if saved_note:
            history_text.value = saved_note
            history_text.italic = False
            history_text.color = "black"
        else:
            history_text.value = "这一天还没有记录哦..."
            history_text.italic = True
            history_text.color = "grey"
        page.update()

    load_data(selected_date.value)

    def on_date_change(e):
        date_str = e.control.value.strftime("%Y-%m-%d")
        selected_date.value = date_str
        load_data(date_str)
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=datetime.datetime(2025, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
    )
    page.overlay.append(date_picker)

    def save_check_in(e):
        if note_input.value:
            page.client_storage.set(selected_date.value, note_input.value)
            load_data(selected_date.value)
            note_input.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("✅ 打卡成功！已存入日历"))
            page.snack_bar.open = True
            page.update()

    page.add(
        ft.Column([
            ft.Text("📅 选择日期", size=16, color="grey"),
            ft.Row([
                selected_date,
                ft.IconButton(
                    icon=ft.icons.CALENDAR_MONTH,
                    on_click=lambda _: date_picker.pick_date(),
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(),
            
            ft.Text("📝 今日详情", size=18, weight="bold"),
            ft.Container(
                content=history_text,
                padding=15,
                bgcolor="#f0f0f0",
                border_radius=10,
            ),
            
            ft.Divider(),
            
            ft.Text("✍️ 填写备注并打卡", size=18, weight="bold"),
            note_input,
            ft.ElevatedButton(
                "立即打卡",
                icon=ft.icons.DONE_ALL,
                on_click=save_check_in,
                style=ft.ButtonStyle(color="white", bgcolor="blue")
            ),
        ], spacing=20)
    )

ft.app(target=main)
