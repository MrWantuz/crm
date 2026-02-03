import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from datetime import datetime

# --- НАСТРОЙКА ПОЛЬЗОВАТЕЛЕЙ ---
# Здесь ты прописываешь логины, имена и пароли для сотрудников
credentials = {
    "usernames": {
        "admin": {
            "name": "Администратор",
            "password": "admin123"  # Поменяй на свой
        },
        "master1": {
            "name": "Мария (Мастер)",
            "password": "pass456"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "crm_cookie",
    "auth_key",
    cookie_expiry_days=30
)

# Вызов формы входа
name, authentication_status, username = authenticator.login('Вход в CRM', 'main')

# --- ПРОВЕРКА СТАТУСА АВТОРИЗАЦИИ ---
if authentication_status == False:
    st.error('Неверный логин или пароль')
elif authentication_status == None:
    st.warning('Пожалуйста, введите логин и пароль')
elif authentication_status:
    # --- ЕСЛИ ВХОД УСПЕШЕН, ПОКАЗЫВАЕМ CRM ---
    
    with st.sidebar:
        st.write(f"Добро пожаловать, **{name}**!")
        authenticator.logout('Выйти', 'sidebar')
        st.divider()
        menu = st.radio("Навигация", ["📅 Журнал записей", "👥 Клиенты", "📊 Отчеты"])

    # Инициализация данных (как в прошлом примере)
    if 'db_appointments' not in st.session_state:
        st.session_state.db_appointments = pd.DataFrame(columns=["Клиент", "Услуга", "Мастер", "Дата", "Время"])

    if menu == "📅 Журнал записей":
        st.header("Рабочий график")
        
        # Разделение прав: Админ видит всех, мастер - только себя
        if username == "admin":
            view_mode = st.selectbox("Сотрудник", ["Все", "Мария", "Алексей"])
        else:
            st.info(f"Вы просматриваете записи для: {name}")

        # Форма записи
        with st.expander("➕ Добавить новую запись"):
            with st.form("new_order"):
                client = st.text_input("Имя клиента")
                service = st.selectbox("Услуга", ["Стрижка", "Маникюр"])
                date = st.date_input("Дата")
                time = st.time_input("Время")
                if st.form_submit_button("Сохранить"):
                    new_entry = pd.DataFrame([[client, service, name, str(date), str(time)]], 
                                             columns=st.session_state.db_appointments.columns)
                    st.session_state.db_appointments = pd.concat([st.session_state.db_appointments, new_entry], ignore_index=True)
                    st.success("Записано!")

        st.dataframe(st.session_state.db_appointments, use_container_width=True)

    elif menu == "👥 Клиенты":
        st.header("База клиентов")
        st.table(st.session_state.db_appointments[["Клиент"]].drop_duplicates())

    elif menu == "📊 Отчеты":
        if username == "admin":
            st.header("Финансовый отчет")
            st.bar_chart(st.session_state.db_appointments["Мастер"].value_counts())
        else:
            st.error("У вас нет прав для просмотра этого раздела.")
