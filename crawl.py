import requests
import os
from bs4 import BeautifulSoup
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import json
import argparse

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    
    if 'known_urls_file' not in config:
        base_name = os.path.basename(config_file)
        config['known_urls_file'] = f"known_urls_{os.path.splitext(base_name)[0]}.txt"
        print(f'** Saving Knows Urls to {config['known_urls_file']} **')
    
    return config

def upload_to_nextcloud(file_path, nextcloud_url, username, password):
    with open(file_path, 'rb') as f:
        response = requests.put(
            f"{nextcloud_url}/{os.path.basename(file_path)}",
            data=f,
            auth=(username, password)
        )
    response.raise_for_status()

urls = {
    'sattelite_images': {
        'Ammassalik': 'http://ocean.dmi.dk/arctic/ammassalik_frame_content_short.php',
        'Kangerlussuaq': 'http://ocean.dmi.dk/arctic/kangerlussuaq_frame_content_short.php',
        'Blosseville': 'http://ocean.dmi.dk/arctic/blosseville_frame_content_short.php',
        'Ittoqqortoormiit': 'http://ocean.dmi.dk/arctic/ittoqqortoormiit_frame_content_short.php',
        'Kangertittivaq': 'http://ocean.dmi.dk/arctic/kangertittivaq_frame_content_short.php',
        'Kong Oscar Fjord': 'http://ocean.dmi.dk/arctic/kongoscarfjord_frame_content_short.php',
        'Daneborg': 'http://ocean.dmi.dk/arctic/daneborg_frame_content_short.php',
        'Dove': 'http://ocean.dmi.dk/arctic/dove_frame_content_short.php',
        'Joekelbugt': 'http://ocean.dmi.dk/arctic/joekelbugt_frame_content_short.php',
        'North East Water': 'http://ocean.dmi.dk/arctic/northeastwater_frame_content_short.php',
        'Station Nord': 'http://ocean.dmi.dk/arctic/nord_frame_content_short.php',
        'Cape Morris Jesup': 'http://ocean.dmi.dk/arctic/morrisjessup_frame_content_short.php',
        'Lincoln': 'http://ocean.dmi.dk/arctic/lincoln_frame_content_short.php',
        'Kennedy': 'http://ocean.dmi.dk/arctic/kennedy_frame_content_short.php',
        'Kane': 'http://ocean.dmi.dk/arctic/kane_frame_content_short.php',
        'Qaanaaq': 'http://ocean.dmi.dk/arctic/qaanaaq_frame_content_short.php',
        'Pituffik': 'http://ocean.dmi.dk/arctic/pituffik_frame_content_short.php',
        'Melville': 'http://ocean.dmi.dk/arctic/melville_frame_content_short.php',
        'Upernavik': 'http://ocean.dmi.dk/arctic/upernavik_frame_content_short.php',
        'Uummannaq': 'http://ocean.dmi.dk/arctic/uummannaq_frame_content_short.php',
        'Disko': 'http://ocean.dmi.dk/arctic/disko_frame_content_short.php',
        'Sisimiut': 'http://ocean.dmi.dk/arctic/sisimiut_frame_content_short.php',
        'Maniitsoq': 'http://ocean.dmi.dk/arctic/maniitsoq_frame_content_short.php',
        'Nuuk': 'http://ocean.dmi.dk/arctic/nuuk_frame_content_short.php',
        'Paamiut': 'http://ocean.dmi.dk/arctic/paamiut_frame_content_short.php',
        'Ivittuut': 'http://ocean.dmi.dk/arctic/ivittuut_frame_content_short.php',
        'Qaqortoq': 'http://ocean.dmi.dk/arctic/qaqortoq_frame_content_short.php',
        'Nanortalik': 'http://ocean.dmi.dk/arctic/nanortalik_frame_content_short.php',
        'Timmiarmiut': 'http://ocean.dmi.dk/arctic/timmiarmiut_frame_content_short.php',
        'Umiivik': 'http://ocean.dmi.dk/arctic/umiivik_frame_content_short.php',
    },
    'icecharts': {
        'SouthEast_RIC': 'http://ocean.dmi.dk/arctic/icecharts_southeast_frame_content_short.php',
        'NorthAndCentralEast_RIC': 'http://ocean.dmi.dk/arctic/icecharts_northcentraleast_frame_content_short.php',
        'Greenland_WA': 'http://ocean.dmi.dk/arctic/icecharts_gl_1_frame_content_short.php',
        'CapeFarewell_RIC': 'http://ocean.dmi.dk/arctic/icecharts_capefarewell_frame_content_short.php',
        'SouthWest_RIC': 'http://ocean.dmi.dk/arctic/icecharts_southwest_frame_content_short.php',
        'CentralWest_RIC': 'http://ocean.dmi.dk/arctic/icecharts_centralwest_frame_content_short.php',
        'NorthWest_RIC': 'http://ocean.dmi.dk/arctic/icecharts_northwest_frame_content_short.php'
    }
}

def load_known_urls(known_urls_file):
    if not os.path.isfile(known_urls_file):
        return set()

    with open(known_urls_file) as f:
        return set(f.read().splitlines())

def save_known_urls(known_urls, known_urls_file):
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
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    input_elements = soup.findAll('input', type='image')

    images = []
    for input_element in input_elements:
        preview_url = input_element['src']
        main_url = 'http://ocean.dmi.dk/arctic/' + preview_url.replace('/small/', '/').replace('.small.jpg', '.pdf')
        images.append({
            'url': main_url,
            'description': input_element.parent.parent.find('span').get_text()
        })
    return images

def identify_new_images(images, known_urls):
    new_images = []
    for image in images:
        if image['url'] not in known_urls:
            new_images.append(image)
    return new_images

def find_recipients(type, name, subscribers):
    recipients = []
    for subscriber in subscribers:
        if name in subscriber[type]:
            recipients.append(subscriber)
    return recipients

def notify_recipients(recipients, new_images, place_name, smtp_config):
    for recipient in recipients:
        if recipient['mail']:
            for new_image in new_images:
                subject = f"{place_name} {new_image['description']}"
                body = new_image['url']
                send_mail(recipient['mail'], subject, body, [image_filename(new_image)], smtp_config)

def download_images(images):
    for image in images:
        filename = image_filename(image)
        response = requests.get(image['url'])
        with open(filename, "wb") as f:
            f.write(response.content)

def image_filename(image):
    return "images/" + image['url'].rsplit('/', 1)[1]

def send_mail(send_to, subject, text, files, smtp_config):
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from']
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'])
    smtp.login(smtp_config['user'], smtp_config['pass'])

    smtp.sendmail(smtp_config['from'], send_to, msg.as_string())
    smtp.close()

def main():
    parser = argparse.ArgumentParser(description="Crawler for newest images")
    parser.add_argument('config_file', help="Path to the configuration file")
    args = parser.parse_args()

    config = load_config(args.config_file)
    known_urls = load_known_urls(config['known_urls_file'])

    for image_type, place_url_map in urls.items():
        for place_name, place_url in place_url_map.items():
            recipients = find_recipients(image_type, place_name, config['subscribers'])
            if len(recipients) == 0:
                continue

            print(f'** Crawling {image_type} of {place_name} **')
            images = crawl_for_newest_images(image_type, place_url)
            new_images = identify_new_images(images, known_urls)
            print(f'** Identified {len(new_images)} new images **')
            download_images(new_images)
            
            if config['upload_to_nextcloud']:
                for image in new_images:
                    upload_to_nextcloud(image_filename(image), config['nextcloud']['url'], config['nextcloud']['username'], config['nextcloud']['password'])
            
            if recipients:
                notify_recipients(recipients, new_images, place_name, config['smtp'])

            known_urls.update(i['url'].rstrip() for i in new_images)
            save_known_urls(known_urls, config['known_urls_file'])

if __name__ == '__main__':
    main()
