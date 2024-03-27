import cv2
from pyzbar.pyzbar import decode
import json
import requests
import winsound
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

api_token = config['default']['api_token']
survey_id = config['default']['survey_id']
datacenter = config['default']['datacenter']


# Function to read QR code from webcam
def read_qr_code():
    # Initialize webcam
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)

    last_qr_data = None

    while True:
        # Read frame from webcam
        ret, frame = cap.read()

        frame = cv2.resize(frame, (640, 480))

        # Decode QR code
        qr_codes = decode(frame)

        # Display the frame
        cv2.imshow("QR Code Scanner", frame)

        # Check if QR code is detected
        if qr_codes:
            # Extract QR code data
            qr_data = qr_codes[0].data.decode("utf-8")

            # prevent scanning the same qr code again
            if qr_data != last_qr_data:
                winsound.PlaySound('scan.wav', winsound.SND_FILENAME)
            
                print("QR Code Data:", qr_data)

                email = get_survey_data(qr_data)

                if email is not None:
                    print("Email:", email)
                    print()
                    winsound.PlaySound('ok.wav', winsound.SND_FILENAME)
                    with open('recorded.txt', 'a') as f:
                        f.write(email + '\n')

                else:
                    winsound.PlaySound('error.wav', winsound.SND_FILENAME)
               
            last_qr_data = qr_data
              
        # Check for key press to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release webcam and close window
    cap.release()
    cv2.destroyAllWindows()


def get_webcam_indices(max_index=10):
    indices = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            indices.append(index)
        cap.release()
    return indices

def get_survey_data(response_id):
    url = f'https://{datacenter}.qualtrics.com/API/v3/surveys/{survey_id}/responses/{response_id}'
    headers = {
        "X-API-TOKEN": api_token
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    survey_data = response.json()
    return survey_data['result']['values']['QID1_TEXT']

if __name__ == "__main__":

    # webcam_indices = get_webcam_indices()
    # print("Webcam indices:", webcam_indices)

    read_qr_code()
