import smtplib

try:
    # 建立連線到 Gmail SMTP 服務器
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # 啟用 TLS 加密
    # 使用 Gmail 帳號和應用程式專用密碼登入
    server.login('forworkjayjay@gmail.com', 'kaoe tpvv qsbm kiaq')
    print("SMTP 連線成功，可以發送郵件")
    server.quit()  # 結束連線
except Exception as e:
    print("SMTP 錯誤:", e)