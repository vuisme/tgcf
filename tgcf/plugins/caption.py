import logging
import re
import requests
from tgcf.plugins import TgcfMessage, TgcfPlugin

class TgcfCaption(TgcfPlugin):
    id_ = "caption"

    def __init__(self, data) -> None:
        self.caption = data
        logging.info(self.caption)

    def extract_card_number(self, text):
        # Giả sử số thẻ là chuỗi gồm 16 chữ số liên tục
        match = re.search(r'\b\d{16}\b', text)
        if match:
            return match.group(0)
        return None

    def query_api(self, card_number):
        # URL API và endpoint
        api_url = f"http://binbase:5000/api/bin/{card_number}"
        
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()  # Giả sử API trả về dữ liệu JSON
        except requests.RequestException as e:
            logging.error(f"API request failed: {e}")
            return {"error": "Unable to retrieve BIN data"}

    def modify(self, tm: TgcfMessage) -> TgcfMessage:
        # Trích xuất số thẻ từ tin nhắn
        card_number = self.extract_card_number(tm.text)
        
        if card_number:
            logging.info(f"Card number extracted: {card_number}")
            # Gửi yêu cầu tới API để lấy dữ liệu BIN
            api_data = self.query_api(card_number[:6])  # Sử dụng 6 ký tự đầu làm BIN
            logging.info(f"API data received: {api_data}")

            # Kiểm tra xem API có trả về lỗi hay không
            if "error" not in api_data:
                # Tạo chuỗi footer với định dạng Markdown và icon cho Telegram
                footer_md = (
                    f"**💳 Brand**: {api_data.get('Brand', 'N/A')}\n"
                    f"**🏦 Issuer**: {api_data.get('Issuer', 'N/A')}\n"
                    f"**💼 Type**: {api_data.get('Type', 'N/A')}\n"
                    f"**🔍 Category**: {api_data.get('Category', 'N/A')}\n"
                    f"**🌍 Country**: {api_data.get('CountryName', 'N/A')}"
                )

                # Sử dụng phép gán = thay vì +=
                self.caption.footer = footer_md 
            else:
                self.caption.footer = f"Error: {api_data['error']}" 
        
        # Chèn header và footer vào tin nhắn
        tm.text = f"{self.caption.header}{tm.text}\n\n{self.caption.footer}"
        return tm
