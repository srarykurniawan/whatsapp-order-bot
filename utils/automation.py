import re
from datetime import datetime

class AutomationRules:
    def __init__(self):
        self.rules = {
            'greeting': {
                'pattern': r'(halo|hai|hello|hi|selamat)',
                'response': 'Halo! Terima kasih telah menghubungi kami. Ada yang bisa saya bantu?'
            },
            'order': {
                'pattern': r'(pesan|order|mau|ingin|beli|pesan)',
                'response': 'Silakan sebutkan menu yang ingin dipesan. Kami memiliki nasi goreng, ayam bakar, mie goreng, es teh, dan es jeruk.'
            },
            'thanks': {
                'pattern': r'(terima kasih|makasih|thanks|thank you)',
                'response': 'Sama-sama! Terima kasih telah berbelanja di toko kami. 😊'
            },
            'delivery': {
                'pattern': r'(kapan sampai|estimasi|berapa lama|delivery)',
                'response': 'Pesanan biasanya sampai dalam 30-45 menit. Terima kasih atas kesabarannya!'
            }
        }
    
    def process_message(self, message):
        """Process incoming message and return automated response"""
        message_lower = message.lower()
        
        for rule_name, rule in self.rules.items():
            if re.search(rule['pattern'], message_lower):
                return rule['response']
        
        # Default response jika tidak ada rule yang cocok
        return "Terima kasih telah menghubungi kami. Silakan ketik 'menu' untuk melihat daftar menu atau 'help' untuk bantuan."