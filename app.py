import streamlit as st
from streamlit_option_menu import option_menu
import requests

BACKEND_URL = "http://localhost:8000"

def login(username: str, password: str):
    """FastAPIバックエンドに対してログインし、トークンを取得する"""
    response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

def get_protected_data(token: str):
    """認証トークンを使用して保護されたデータを取得する"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BACKEND_URL}/protected-endpoint", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def register_user(name: str, email: str, password: str):
    """バックエンドに新しいユーザーを登録する"""
    response = requests.post(f"{BACKEND_URL}/users/", json={"name": name, "email": email, "password": password})
    return response
    
    
# StreamlitアプリケーションのUI
st.title("認証デモアプリ")

# メニュー欄
with st.sidebar:
    selected = option_menu('Main Menu', ['ログイン', 'ユーザー登録'],
                           icons=['door-open', 'person-plus-fill'],
                           menu_icon='cast',
                           default_index=0)

if selected == 'ログイン':
    with st.form('input_data'):
        st.markdown('### ログインフォーム')
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")

        if st.form_submit_button('ログイン', type='primary', use_container_width=True):
            token = login(username, password)
            if token:
                st.success("ログイン成功!")
                # トークンを使用して保護されたデータを取得する例
                protected_data = get_protected_data(token)
                st.write(protected_data)
                st.markdown('# ログインが成功しました！！')
            else:
                st.error("ログイン失敗。ユーザー名またはパスワードが間違っています。")

elif selected == 'ユーザー登録':
    with st.form('input_data'):
        st.markdown('### ユーザー登録フォーム')
        username = st.text_input('ユーザー名', key='register_name')
        email = st.text_input('メールアドレス', key='register_email')
        password = st.text_input('パスワード', type='password', key='register_password')

        if st.form_submit_button('登録', type='primary', use_container_width=True):
            response = register_user(username, email, password)
            if response.status_code == 200:
                st.success('ユーザー登録が完了しました')
            else:
                st.error('ユーザー登録に失敗しました')
                st.text(response)
                st.json(response)