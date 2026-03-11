import os
import time
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 1. 各種設定（APIキーなどをここに入力します）
# ==========================================

# --- Google Drive の設定 ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
DRIVE_FOLDER_ID = '1EAy5zG828wOdHoxVs3cGt-k8GB6hQrp_' # 自動投稿用動画、2026、0305

# --- Instagram (Meta Graph API) の設定 ---
IG_ACCESS_TOKEN = 'ここにInstagram Graph APIのアクセストークンを入れます'
IG_ACCOUNT_ID = 'ここにInstagramのアカウントIDを入れます'

# ==========================================

def upload_to_drive(file_path, file_name):
    """Google Driveに動画をアップロードする関数"""
    print(f"Google Driveへのアップロードを開始します: {file_name}")
    creds = None
    # 既存のトークンがあれば読み込む
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 有効な証明書がない場合はログインして取得（初回はブラウザが開きます）
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 次回のためにトークンを保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID] if DRIVE_FOLDER_ID else []
    }
    media = MediaFileUpload(file_path, mimetype='video/mp4', resumable=True)
    
    # アップロードの実行
    file = service.files().create(body=file_metadata,
                               media_body=media,
                               fields='id').execute()
    print(f"Driveアップロード完了 (File ID: {file.get('id')})")
    return file.get('id')

def post_to_instagram(video_url, caption):
    """Instagramに動画(Reels)をアップロードして投稿する関数"""
    print(f"Instagramへの投稿を開始します...")
    
    # 1. 動画のコンテナ（投稿の準備枠）を作成
    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media"
    payload = {
        'video_url': video_url,
        'caption': caption,
        'media_type': 'REELS',
        'access_token': IG_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=payload)
    result = response.json()
    
    if 'id' not in result:
        print("エラー: コンテナ作成に失敗しました:", result)
        return
        
    container_id = result['id']
    print(f"コンテナ作成完了 (Container ID: {container_id})")

    # 2. Instagram側の動画の処理が終わるまで待つ
    print("動画の処理完了を待機中...")
    status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={IG_ACCESS_TOKEN}"
    while True:
        status_res = requests.get(status_url).json()
        status = status_res.get('status_code')
        if status == 'FINISHED':
            break
        elif status == 'ERROR':
            print("エラー: 動画の処理に失敗しました。")
            return
        time.sleep(5) # 5秒待って再確認

    # 3. 投稿（公開）を実行
    publish_url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media_publish"
    publish_payload = {
        'creation_id': container_id,
        'access_token': IG_ACCESS_TOKEN
    }
    publish_res = requests.post(publish_url, data=publish_payload)
    publish_result = publish_res.json()
    
    if 'id' in publish_result:
        print("🎉 Instagramへの投稿が完了しました！")
    else:
        print("エラー: 投稿の公開に失敗しました:", publish_result)

if __name__ == "__main__":
    # --- 実行する動画の設定 ---
    VIDEO_PATH = 'sora_generated_video.mp4' # 自動生成された動画のパス
    FILE_NAME = 'My_AI_Generated_Video.mp4'
    CAPTION = 'Soraで生成した動画です！ #自動投稿 #AI #Sora'
    
    # Instagramはインターネット上のURLから動画を取得するため、公開されたURLが必要です。
    # ※ 実際には自身のサーバーなどに置かれた動画のURLを指定します。
    PUBLIC_VIDEO_URL = 'ここに動画の公開URLを入れます'

    # 1. Google Driveに保存
    upload_to_drive(VIDEO_PATH, FILE_NAME)
    
    # 2. Instagramに投稿
    # post_to_instagram(PUBLIC_VIDEO_URL, CAPTION)
    
    print("APIキーなどの設定が完了したら、コメントアウトを外して実行してください。")
