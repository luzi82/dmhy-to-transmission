import argparse
import datetime
import defusedxml.ElementTree as ET
import json
import logging
import os
import re
import requests
import transmission_rpc
import urllib.parse

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default="config.json")
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    with open(args.config, 'rt', encoding='utf-8') as fin:
        config_data = json.load(fin)

    yyyymmdd = datetime.datetime.now().strftime('%Y%m%d')
    yyyymm = yyyymmdd[:6]
    # print(yyyymmdd)

    log_path = config_data.get('log_path', 'log')
    log_yyyymm_path = os.path.join(log_path, yyyymm)
    os.makedirs(log_yyyymm_path, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_yyyymm_path, f'{yyyymmdd}-main.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    torrent_data_list = []
    config_source_list = config_data['source_list']
    for config_source in config_source_list:
        try:
            logger.info(f'AUGENSBVFD config_source={config_source}')
            url = 'https://share.dmhy.org/topics/rss/rss.xml?' + urllib.parse.urlencode(config_source['query'])
            logger.info(f'JYYIMCDVGJ url={url}')
            rss = requests.get(url).text
            rss_root = ET.fromstring(rss)
            items = rss_root.findall('./channel/item')
            for item in items:
                title = item.find('title').text
                if 'title_re_list' in config_source:
                    title_re_list_result = config_source['title_re_list']
                    title_re_list_result = map(lambda x: re.fullmatch(x, title), title_re_list_result)
                    title_re_list_result = all(title_re_list_result)
                    if not title_re_list_result:
                        continue
                enclosure_url = item.find('enclosure').attrib['url']
                # print('===')
                # print(title)
                # print(enclosure_url)
                logger.info(f'XYFAPNOYGY title={title}')
                logger.info(f'DZDWVPWWWV enclosure_url={enclosure_url}')
                torrent_data_list.append({
                    'title': title,
                    'enclosure_url': enclosure_url
                })
        except Exception as e:
            logger.exception(e)

    added_torrent_data_list = []
    if not args.test:
        for client_config in config_data['client_list']:
            client = transmission_rpc.Client(**client_config['connection'])
            current_torrent_list = client.get_torrents()
            current_torrent_hash_list = [torrent.hashString for torrent in current_torrent_list]
            current_torrent_hash_set = set(current_torrent_hash_list)
            for torrent_data in torrent_data_list:
                ret = client.add_torrent(torrent_data['enclosure_url'])
                already_added = ret.hashString in current_torrent_hash_set
                logger.info(f'FIISPXRZNJ client_id={client_config["client_id"]}')
                logger.info(f'MXEFZHRTPA title={torrent_data["title"]}')
                logger.info(f'UURNFNTQPD hashString={ret.hashString}')
                logger.info(f'ZOKLDTROID already_added={already_added}')
                current_torrent_hash_set.add(ret.hashString)

    # for added_torrent_data in added_torrent_data_list:
    #     print('===')
    #     print(added_torrent_data['client_id'])
    #     print(added_torrent_data['torrent_data']['title'])

    print('HGAPHXGKSJ DONE')
