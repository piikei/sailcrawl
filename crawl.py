import requests
import os
from bs4 import BeautifulSoup
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM, SUBSCRIBERS

urls = {
    'sattelite_images': {
        'Ammassalik': 'http://ocean.dmi.dk/arctic/ammassalik_frame_content_short.php'
    },
    'icecharts': {

    }
}

known_urls_file = 'known_urls.txt'

def load_known_urls():
    if not os.path.isfile(known_urls_file):
        return set()

    with open(known_urls_file) as f:
        return set(f.readlines())

def save_known_urls(known_urls):
    with open(known_urls_file, 'w') as f:
        f.write('\n'.join(known_urls))


def crawl_for_newest_images(type, url):
    if type == 'sattelite_images':
        return crawl_for_newest_sattelite_images(url)
    elif type == 'icecharts':
        return crawl_for_newest_icecharts(url)
    else:
        raise ValueError('Unknown image type: ' + str(type))


def crawl_for_newest_sattelite_images(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    input_elements = soup.findAll('input', type='image')

    images = []
    for input_element in input_elements:
        preview_url = input_element['src']
        main_url = 'http://ocean.dmi.dk/arctic/' + preview_url.replace('/small/', '/').replace('.small.', '.')
        images.append({
            'url': main_url,
            'description': input_element.parent.parent.find('span').get_text()
        })

    return images


def crawl_for_newest_icecharts(url):
    return []


def identify_new_images(images, known_urls):
    new_images = []
    for image in images:
        if image['url'] not in known_urls:
            new_images.append(image)

    return new_images


def find_recipients(type, name):
    recipients = []
    for subscriber in SUBSCRIBERS:
        if name in subscriber[type]:
            recipients.append(subscriber)
    return recipients


def notify_recipients(recipients, new_images):
    for recipient in recipients:
        for new_image in new_images:
            pass

def download_images(images):
    for image in images:
        filename = image['url'].rsplit('/', 1)[1]
        print(filename)


# Thanks https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
def send_mail(send_to, subject, text, files=None):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
    smtp.login(SMTP_USER, SMTP_PASS)

    smtp.sendmail(SMTP_FROM, send_to, msg.as_string())
    smtp.close()


def main():
    known_urls = load_known_urls()

    for image_type, place_url_map in urls.items():
        for place_name, place_url in place_url_map.items():
            recipients = find_recipients(image_type, place_name)
            if len(recipients) == 0:
                # Only crawl for images that someone requested
                continue

            images = crawl_for_newest_sattelite_images(place_url)
            new_images = identify_new_images(images, known_urls)
            download_images(new_images)
            notify_recipients(recipients, new_images)
            # Save the new urls immediately to avoid resending if the script crashes
            known_urls.update(i['url'] for i in new_images)
            save_known_urls(known_urls)
        


if __name__ == '__main__':
    main()



