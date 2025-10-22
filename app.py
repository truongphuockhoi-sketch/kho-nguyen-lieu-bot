import os
import pandas as pd
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Cấu hình Line Bot
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# URL Google Sheets của bạn
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/1h4K0_GwNux1XDNJ0lnMhULqxekqjiV8HdUfBrhL3OoQ/gviz/tq?tqx=out:csv&sheet=Sheet1"

def search_material(keyword):
    """Tìm kiếm nguyên liệu theo TÊN - Tối ưu hoá"""
    try:
        # Đọc trực tiếp từ Google Sheets
        df = pd.read_csv(GOOGLE_SHEETS_URL)
        
        # Chuẩn hóa từ khóa - CHẤP NHẬN cả hoa và thường
        keyword = str(keyword).strip().lower()
        
        print(f"🔍 Tìm kiếm: '{keyword}'")
        print(f"📊 Tổng số dòng dữ liệu: {len(df)}")
        
        # Tìm kiếm LINH HOẠT theo TÊN
        if keyword == "test":
            return "✅ Bot Kho Nguyên Liệu hoạt động tốt!"
        elif keyword == "help":
            return """📋 HƯỚNG DẪN SỬ DỤNG:
• RBF, Cám, Cám gạo - Tìm theo tên nguyên liệu
• Mã số (135011, 135018,...) - Tìm theo mã
• TEST - Kiểm tra bot
• HELP - Hướng dẫn

💡 Gõ tên nguyên liệu (không phân biệt hoa/thường)"""
        else:
            # Tìm kiếm THEO TÊN - không phân biệt hoa/thường
            mask = df['Name'].str.lower().str.contains(keyword, na=False)
        
        results = df[mask]
        
        if results.empty:
            return f"❌ Không tìm thấy '{keyword}'. Thử tên khác hoặc 'HELP'"
        
        # Format kết quả - MỖI DÒNG RIÊNG LẺ
        response = f"📦 KẾT QUẢ: '{keyword.upper()}'\n"
        response += f"📊 Tìm thấy: {len(results)} dòng\n\n"
        
        # HIỂN THỊ TẤT CẢ KẾT QUẢ - KHÔNG GIỚI HẠN
        for i, (_, row) in enumerate(results.iterrows(), 1):
            response += f"📍 DÒNG {i}:\n"
            response += f"┌─ 🏷️ MÃ: {row['Code']}\n"
            response += f"├─ 📛 TÊN: {row['Name']}\n"
            response += f"├─ 🔒 LOCK: {row['LOCK']}\n"
            response += f"├─ 🔢 SỐ LƯỢNG: {row['Quantity']}\n"
            response += f"├─ ⚖️ TRỌNG LƯỢNG: {row['Weight']} kg\n"
            response += f"├─ 📅 NGÀY NHẬP: {row['Date in']}\n"
            response += f"└─ ⏳ TUỔI KHO: {row['Storage Age']} ngày\n\n"
            
        return response
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return f"⚠️ Lỗi hệ thống: {str(e)}"

# Webhook cho Line Bot
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"📨 Tin nhắn: {user_message}")
    reply_text = search_material(user_message)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

@app.route("/")
def home():
    return "✅ Bot Kho Nguyên Liệu - Phiên bản Google Sheets"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
