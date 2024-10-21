# utils/qr_generator.py
import qrcode
import os
from config import BASE_DIR  # Убедитесь, что BASE_DIR определен в config.py

async def generate_qr_code(user_id: int, event_id: int, category: str) -> str:
    data = f"user_id:{user_id};event_id:{event_id};category:{category}"
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Создание директории для хранения QR-кодов, если её нет
    qr_dir = os.path.join(BASE_DIR, 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Сохранение QR-кода
    qr_path = os.path.join(qr_dir, f"ticket_{user_id}_{event_id}.png")
    img.save(qr_path)
    
    return qr_path
