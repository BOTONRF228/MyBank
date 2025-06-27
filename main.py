from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, CardTransition
from kivy.uix.image import Image, AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.modalview import ModalView
from kivy.utils import platform
from kivy.properties import (StringProperty, NumericProperty, ListProperty, 
                           ObjectProperty, BooleanProperty, DictProperty)
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse, Triangle
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.effects.scroll import ScrollEffect
from kivy.lang import Builder
import json
import os
import random
from datetime import datetime, timedelta
import webbrowser
from math import sin, cos, radians
import csv
from plyer import notification
from kivy.storage.jsonstore import JsonStore

# Установка размера окна для эмуляции мобильного устройства
Window.size = (360, 640)
Window.clearcolor = (0.97, 0.97, 0.98, 1)  # Светло-серый фон

# Мультиязычная поддержка
translations = {
    'en': {
        'login': 'Login',
        'welcome': 'Welcome',
        'balance': 'Balance',
        'transfer': 'Transfer',
        'history': 'History',
        # ... другие переводы
    },
    'ru': {
        'login': 'Вход',
        'welcome': 'Добро пожаловать',
        'balance': 'Баланс',
        'transfer': 'Перевод',
        'history': 'История',
        # ... другие переводы
    }
}

class LanguageManager:
    def __init__(self):
        self.store = JsonStore('language.json')
        self.current_lang = 'ru'  # язык по умолчанию
        
        try:
            if self.store.exists('language'):
                self.current_lang = self.store.get('language')['lang']
        except:
            pass
    
    def set_language(self, lang):
        self.current_lang = lang
        self.store.put('language', lang=lang)
    
    def get(self, key):
        return translations[self.current_lang].get(key, key)

# Инициализация менеджера языков
language_manager = LanguageManager()

if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.INTERNET, 
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.RECEIVE_BOOT_COMPLETED,
        Permission.VIBRATE,
        Permission.WAKE_LOCK
    ])
    
    # Фикс для полноэкранного режима
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    
    @run_on_ui_thread
    def hide_status_bar():
        WindowManager = autoclass('android.view.WindowManager$LayoutParams')
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        window = activity.getWindow()
        window.addFlags(WindowManager.FLAG_FULLSCREEN)
    
    hide_status_bar()

    # Для push-уведомлений на Android
    from plyer import notification

# Глобальные стили (остаются без изменений)
Builder.load_string('''
... (ваш текущий код стилей остается без изменений)
''')

class BankAccount:
    def __init__(self, account_file='accounts.json'):
        self.account_file = account_file
        self.accounts = self.load_accounts()
        self.categories = {
            'food': {'name': 'Еда', 'icon': '🍔', 'color': [0.9, 0.2, 0.2, 1], 'custom': False},
            'transport': {'name': 'Транспорт', 'icon': '🚕', 'color': [0.2, 0.5, 0.9, 1], 'custom': False},
            # ... остальные стандартные категории
        }
        self.load_custom_categories()
    
    def load_custom_categories(self):
        try:
            with open('custom_categories.json', 'r') as f:
                custom_cats = json.load(f)
                for cat_id, cat in custom_cats.items():
                    self.categories[cat_id] = cat
        except:
            pass
    
    def save_custom_categories(self):
        custom_cats = {k: v for k, v in self.categories.items() if v.get('custom', False)}
        with open('custom_categories.json', 'w') as f:
            json.dump(custom_cats, f, indent=4, ensure_ascii=False)
    
    def add_custom_category(self, name, icon, color):
        cat_id = f"custom_{len([c for c in self.categories if c.startswith('custom_')])}"
        self.categories[cat_id] = {
            'name': name,
            'icon': icon,
            'color': color,
            'custom': True
        }
        self.save_custom_categories()
        return cat_id
    
    def export_data(self, username, format='csv'):
        account = self.accounts.get(username)
        if not account:
            return False
        
        filename = f"mybank_export_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == 'csv':
            filename += '.csv'
            transactions = account.get('transactions', [])
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Amount', 'Description', 'Category'])
                
                for t in transactions:
                    writer.writerow([
                        t['date'],
                        t['amount'],
                        t['description'],
                        self.categories.get(t.get('category', 'other'), {}).get('name', 'Other')
                    ])
            
            return filename
        
        elif format == 'json':
            filename += '.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(account, f, indent=4, ensure_ascii=False)
            
            return filename
        
        return False
    
    def send_push_notification(self, username, title, message):
        if platform == 'android':
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name='MyBank',
                    timeout=10
                )
            except:
                pass
        else:
            print(f"Notification: {title} - {message}")
    
    # ... остальные методы класса BankAccount остаются без изменений

class MainScreen(Screen):
    def show_export_options(self, instance):
        modal = ModalView(size_hint=(0.8, 0.4))
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = Label(
            text="Экспорт данных",
            font_size=sp(18),
            bold=True,
            size_hint=(1, None),
            height=dp(40)
        )
        
        csv_btn = CustomButton(
            text="Экспорт в CSV",
            on_press=lambda x: self.export_data('csv'))
        
        json_btn = CustomButton(
            text="Экспорт в JSON",
            on_press=lambda x: self.export_data('json'))
        
        close_btn = OutlineButton(
            text="Закрыть",
            on_press=lambda x: modal.dismiss())
        
        layout.add_widget(title)
        layout.add_widget(csv_btn)
        layout.add_widget(json_btn)
        layout.add_widget(close_btn)
        modal.add_widget(layout)
        modal.open()
    
    def export_data(self, format):
        filename = self.bank.export_data(self.current_user, format)
        if filename:
            self.show_message(f"Данные экспортированы в {filename}")
        else:
            self.show_message("Ошибка экспорта данных")

class AnalyticsScreen(Screen):
    def show_category_management(self, instance):
        modal = ModalView(size_hint=(0.9, 0.7))
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = Label(
            text="Управление категориями",
            font_size=sp(18),
            bold=True,
            size_hint=(1, None),
            height=dp(40))
        
        scroll = ScrollView(size_hint=(1, 0.7))
        content = GridLayout(cols=1, size_hint=(1, None), spacing=dp(10))
        content.bind(minimum_height=content.setter('height'))
        
        # Существующие категории
        for cat_id, cat in self.bank.categories.items():
            if cat.get('custom', False):  # Показываем только кастомные
                item = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(60))
                
                icon = Label(
                    text=cat['icon'],
                    font_size=sp(20),
                    size_hint=(None, 1),
                    width=dp(40))
                
                name = Label(
                    text=cat['name'],
                    font_size=sp(16),
                    size_hint=(0.6, 1),
                    halign='left'))
                
                delete_btn = IconButton(
                    text="🗑️",
                    on_press=lambda x, c=cat_id: self.delete_category(c)))
                
                item.add_widget(icon)
                item.add_widget(name)
                item.add_widget(delete_btn)
                content.add_widget(item)
        
        scroll.add_widget(content)
        
        # Форма добавления новой категории
        add_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(200)))
        
        self.new_cat_name = TextInput(
            hint_text="Название категории",
            size_hint=(1, None),
            height=dp(50)))
        
        self.new_cat_icon = TextInput(
            hint_text="Эмодзи (например, 🍔)",
            size_hint=(1, None),
            height=dp(50)))
        
        add_btn = CustomButton(
            text="Добавить категорию",
            on_press=self.add_new_category))
        
        add_layout.add_widget(self.new_cat_name)
        add_layout.add_widget(self.new_cat_icon)
        add_layout.add_widget(add_btn)
        
        close_btn = OutlineButton(
            text="Закрыть",
            on_press=lambda x: modal.dismiss()))
        
        layout.add_widget(title)
        layout.add_widget(scroll)
        layout.add_widget(add_layout)
        layout.add_widget(close_btn)
        modal.add_widget(layout)
        modal.open()
    
    def add_new_category(self, instance):
        name = self.new_cat_name.text.strip()
        icon = self.new_cat_icon.text.strip()
        
        if name and icon:
            color = [random.random(), random.random(), random.random(), 1]
            self.bank.add_custom_category(name, icon, color)
            self.update_stats()
            self.new_cat_name.text = ""
            self.new_cat_icon.text = ""
    
    def delete_category(self, cat_id):
        if cat_id.startswith('custom_'):
            del self.bank.categories[cat_id]
            self.bank.save_custom_categories()
            self.update_stats()

class BankApp(App):
    def build(self):
        self.title = "MyBank"
        self.icon = ""  # Путь к иконке приложения
        self.bank = BankAccount()
        
        # Инициализация уведомлений
        if platform == 'android':
            from android import AndroidService
            service = AndroidService('MyBank Notifications', 'running')
            service.start('service started')
        
        sm = ScreenManager(transition=CardTransition())
        
        sm.add_widget(LoginScreen(name='login', bank=self.bank))
        sm.add_widget(RegisterScreen(name='register', bank=self.bank))
        sm.add_widget(MainScreen(name='main', bank=self.bank))
        sm.add_widget(TransferScreen(name='transfer', bank=self.bank))
        sm.add_widget(HistoryScreen(name='history', bank=self.bank))
        sm.add_widget(AnalyticsScreen(name='analytics', bank=self.bank))
        sm.add_widget(ProfileScreen(name='profile', bank=self.bank))
        sm.add_widget(PaymentsScreen(name='payments', bank=self.bank))
        
        return sm
    
    def on_pause(self):
        # Сохраняем состояние при паузе (для мобильных устройств)
        return True
    
    def on_resume(self):
        # Восстанавливаем состояние при возобновлении
        pass

if __name__ == '__main__':
    BankApp().run()