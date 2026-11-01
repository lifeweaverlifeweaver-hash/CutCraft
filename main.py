from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.parse
import requests

app = FastAPI()

# Позволяваме на вашия GitHub сайт да праща заявки към сървъра
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderRequest(BaseModel):
    email: str
    refCode: str
    price: str
    type: str
    iban: str
    owner: str

@app.post("/api/create-order")
async def create_order(order: OrderRequest):
    # 1. Настройки за Имейл до lifeweaverlifeweaver@gmail.com
    sender_email = "lifeweaverlifeweaver@gmail.com"
    # ВАЖНО: Тук се слага генерираната Google App Password (парола за приложение), а не вашата обикновена парола за Gmail
    email_password = "ТУК_ВЪВЕДЕТЕ_GOOGLE_APP_PASSWORD" 
    
    subject = f"Нова поръчка в CutCraft - {order.refCode}"
    body = (
        f"Здравейте, получена е нова поръчка в CutCraft!\n\n"
        f"Тип мебел: {order.type}\n"
        f"Имейл на клиента: {order.email}\n"
        f"Сума за плащане: {order.price}\n"
        f"Референтен номер (основание): {order.refCode}\n\n"
        f"Данни за превод:\n"
        f"Получател: {order.owner}\n"
        f"IBAN: {order.iban}\n"
        f"BIC: ESPYBGS1"
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, sender_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Грешка при имейл: {e}")

    # 2. Настройки за Viber известие към 0884468329
    owner_phone = "0884468329"
    viber_message = (
        f"🔔 *Нова поръчка в CutCraft!*\n\n"
        f"👤 Клиент: {order.email}\n"
        f"💰 Сума: {order.price}\n"
        f"🔖 Реф: {order.refCode}\n"
        f"🏦 Очаква се превод по IBAN."
    )
    
    try:
        encoded_msg = urllib.parse.quote(viber_message)
        # Може да се използва безплатен шлюз като CallMeBot или друг HTTP API за Viber
        viber_url = f"https://api.callmebot.com/viber/send.php?phone={owner_phone}&text={encoded_msg}&apikey=YOUR_API_KEY"
        requests.get(viber_url)
    except Exception as e:
        print(f"Грешка при Viber: {e}")

    return {"status": "success", "message": "Поръчката е регистрирана и известията са изпратени!"}
