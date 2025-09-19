import os
from openai import OpenAI
from dotenv import load_dotenv

# Tải API key từ file .env
load_dotenv()

# Khởi tạo client OpenAI
# Thư viện sẽ tự động tìm key trong biến môi trường OPENAI_API_KEY
try:
    client = OpenAI()
except Exception as e:
    print(f"Lỗi khi khởi tạo OpenAI client: {e}")
    client = None

def ask_question(prompt: str) -> str:
    """
    Hàm này nhận một câu hỏi, gửi đến OpenAI và trả về câu trả lời.
    """
    if not client:
        return "Lỗi: OpenAI client chưa được khởi tạo. Vui lòng kiểm tra API key."

    try:
        print(f"Đang gửi câu hỏi đến OpenAI: {prompt}")
        
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Bạn có thể đổi sang "gpt-4o" nếu muốn
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful research assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        answer = chat_completion.choices[0].message.content
        return answer
    
    except Exception as e:
        print(f"Đã có lỗi xảy ra khi gọi API OpenAI: {e}")
        return "Xin lỗi, đã có lỗi xảy ra khi kết nối tới OpenAI."
