import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
from flask import Flask, request, Response
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppIntegration:
    def __init__(self):
        self.account_sid = None
        self.auth_token = None
        self.whatsapp_number = None
        self.client = None
        self.flask_app = None
        self.webhook_url = None
        self.message_callback = None
    
    def set_credentials(self, account_sid, auth_token, whatsapp_number, webhook_url=None):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.whatsapp_number = whatsapp_number
        self.webhook_url = webhook_url
        
        try:
            self.client = Client(account_sid, auth_token)
            logger.info("Twilio client berhasil diinisialisasi")
        except Exception as e:
            logger.error(f"Gagal menginisialisasi Twilio client: {e}")
            raise
    
    def send_message(self, to, body):
        if not self.client:
            raise Exception("Twilio client not initialized. Please set credentials first.")
        
        try:
            # Format nomor WhatsApp (pastikan format internasional)
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            message = self.client.messages.create(
                body=body,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=to
            )
            
            logger.info(f"Pesan berhasil dikirim ke {to}: {message.sid}")
            return message.sid
        except TwilioRestException as e:
            logger.error(f"Error mengirim pesan: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def setup_webhook(self, webhook_url):
        """Setup webhook URL untuk Twilio"""
        try:
            # Untuk Twilio, Anda perlu mengatur webhook dari dashboard
            # Fungsi ini hanya untuk logging
            logger.info(f"Webhook URL diatur ke: {webhook_url}")
            logger.info("Silakan atur webhook URL di dashboard Twilio:")
            logger.info("1. Login ke console.twilio.com")
            logger.info("2. Pergi ke WhatsApp > Sandbox Settings")
            logger.info(f"3. Set WHEN A MESSAGE COMES IN to: {webhook_url}")
            self.webhook_url = webhook_url
            return True
        except Exception as e:
            logger.error(f"Error setting up webhook: {e}")
            return False
    
    def start_webhook_server(self, host='0.0.0.0', port=5000, webhook_path='/webhook'):
        """Start Flask server untuk menerima webhook dari Twilio"""
        if not self.webhook_url:
            logger.error("Webhook URL belum diatur")
            return False
        
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route(webhook_path, methods=['POST'])
        def webhook():
            return self._handle_webhook(request)
        
        def run_flask():
            self.flask_app.run(host=host, port=port, debug=False, use_reloader=False)
        
        # Jalankan Flask di thread terpisah
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        
        logger.info(f"Webhook server started on {host}:{port}{webhook_path}")
        return True
    
    def _handle_webhook(self, request):
        """Tangani incoming webhook dari Twilio"""
        try:
            incoming_msg = request.values.get('Body', '').strip()
            sender = request.values.get('From', '')
            message_sid = request.values.get('MessageSid', '')
            
            # Hapus prefix 'whatsapp:' dari nomor pengirim
            if sender.startswith('whatsapp:'):
                sender = sender.replace('whatsapp:', '')
            
            logger.info(f"Pesan masuk dari {sender}: {incoming_msg}")
            
            # Panggil callback function jika diatur
            if self.message_callback:
                response = self.message_callback(incoming_msg, sender)
                if response:
                    self.send_message(sender, response)
            
            return Response(status=200)
        
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return Response(status=500)
    
    def set_message_callback(self, callback_function):
        """Set callback function untuk menangani pesan masuk"""
        self.message_callback = callback_function
        logger.info("Message callback function diatur")
    
    def validate_credentials(self):
        """Validasi Twilio credentials"""
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            return False, "Credentials belum lengkap"
        
        try:
            # Coba dapatkan informasi akun untuk validasi
            account = self.client.api.accounts(self.account_sid).fetch()
            return True, "Credentials valid"
        except TwilioRestException as e:
            return False, f"Credentials tidak valid: {e}"
        except Exception as e:
            return False, f"Error validasi: {e}"