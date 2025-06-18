import os
import gzip
import xml.etree.ElementTree as ET
import requests

name = "udptv"
save_as_gz = True  

output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "epgs")
os.makedirs(output_dir, exist_ok=True)  

tvg_ids_file = os.path.join(os.path.dirname(__file__), f"{name}-tvg-ids.txt")
output_file = os.path.join(output_dir, f"{name}-epg.xml")
output_file_gz = output_file + '.gz'

def fetch_and_extract_xml(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    if url.endswith('.gz'):
        try:
            decompressed_data = gzip.decompress(response.content)
            return ET.fromstring(decompressed_data)
        except Exception as e:
            print(f"Failed to decompress and parse XML from {url}: {e}")
            return None
    else:
        try:
            return ET.fromstring(response.content)
        except Exception as e:
            print(f"Failed to parse XML from {url}: {e}")
            return None

def filter_and_build_epg(urls):
    with open(tvg_ids_file, 'r') as file:
        valid_tvg_ids = set(line.strip() for line in file)

    root = ET.Element('tv')

    for url in urls:
        print(f"Fetching xml ({url})...")
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if tvg_id in valid_tvg_ids:
                print(f"tvg-id -> {tvg_id}")
                root.append(channel)

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if tvg_id in valid_tvg_ids:
                title = programme.find('title')
                if title is not None:
                    title_text = title.text if title is not None else 'No title'

                    root.append(programme)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"New EPG saved to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"New EPG saved to {output_file_gz}")


urls = [
  'http://m3u4u.com/xml/68m7n4wgg7ajewedy1ge',
  'https://raw.githubusercontent.com/pigzillaaaaa/blast-epg/refs/heads/main/blast-epg.xml',
  'https://epgshare01.online/epgshare01/epg_ripper_LT1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_CA1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_PH2.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_HR1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_ID1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_PH1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_PLEX1.xml.gz',
  'https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz',
  'https://epg.pw/api/epg.xml?lang=en&channel_id=413152',
  'https://raw.githubusercontent.com/pigzillaaaaa/amazon-epg/refs/heads/main/amazon-epg.xml'
]

if __name__ == "__main__":
    filter_and_build_epg(urls)
