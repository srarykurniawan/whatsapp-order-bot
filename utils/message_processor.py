import re
import json
from datetime import datetime

class MessageProcessor:
    def __init__(self):
        self.greeting_keywords = ['halo', 'hai', 'hello', 'hi', 'selamat']
        self.order_keywords = ['pesan', 'order', 'mau', 'ingin', 'beli']
        self.menu_items = {
            'nasi goreng': 25000,
            'ayam bakar': 35000,
            'mie goreng': 20000,
            'es teh': 5000,
            'es jeruk': 6000
        }
    
    def process_message(self, message, sender):
        message_lower = message.lower()
        
        # Cek jika pesan adalah greeting
        if any(word in message_lower for word in self.greeting_keywords):
            return self._generate_greeting_response(sender)
        
        # Cek jika pesan berisi order
        elif any(word in message_lower for word in self.order_keywords):
            return self._process_order(message_lower, sender)
        
        # Cek status pesanan
        elif 'status' in message_lower or 'kapan' in message_lower:
            return "Terima kasih telah menghubungi kami. Untuk mengecek status pesanan, silakan berikan nomor pesanan Anda."
        
        # Default response
        else:
            return "Terima kasih telah menghubungi kami. Silakan pesan dengan menyebutkan menu yang Anda inginkan."
    
    def _generate_greeting_response(self, sender):
        return f"Halo! Terima kasih telah menghubungi kami. Ada yang bisa saya bantu untuk dipesan?"
    
    def _process_order(self, message, sender):
        # Ekstrak items dari pesan
        found_items = []
        for item, price in self.menu_items.items():
            if item in message:
                # Coba ekstrak jumlah
                pattern = r'(\d+)\s*' + re.escape(item)
                match = re.search(pattern, message)
                quantity = int(match.group(1)) if match else 1
                found_items.append((item, quantity, price))
        
        if found_items:
            # Format response
            response = "Terima kasih atas pesanan Anda:\n"
            total = 0
            for item, quantity, price in found_items:
                item_total = quantity * price
                response += f"- {quantity} {item} @ Rp {price:,} = Rp {item_total:,}\n"
                total += item_total
            
            response += f"\nTotal: Rp {total:,}\n"
            response += "Silakan konfirmasi dengan mengetik 'ya' untuk memesan atau 'tidak' untuk membatalkan."
            
            return response
        else:
            return "Maaf, saya tidak mengerti pesanan Anda. Silakan sebutkan menu yang ingin dipesan. Menu kami: nasi goreng (Rp 25,000), ayam bakar (Rp 35,000), mie goreng (Rp 20,000), es teh (Rp 5,000), es jeruk (Rp 6,000)."