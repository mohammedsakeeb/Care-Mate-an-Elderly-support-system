

import serial
import openpyxl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(file_path):
    from_email = 'your email addresss'
    to_email = 'to address'
    subject = 'health data'
    body = 'Please find attached the health data.'

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(file_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + file_path)
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email,'aqcf lhhd aojm tajr')
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.flush()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['BPM', 'Temperature', 'ECG'])

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            data = line.split()
            if len(data) == 3:
                bpm, temp, ecg = data
                print(f'BPM: {bpm}, Temperature: {temp}, ECG: {ecg}')
                ws.append([bpm, temp, ecg])
                wb.save('health_data.xlsx')
                send_email('health_data.xlsx')

