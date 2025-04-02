#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import argparse
import sys
from lxml import etree
import math

requests.packages.urllib3.disable_warnings()
class RapidDnsSearch:
    def __init__(self,ip , domain, proxy, output_file_name):
        self.ip=ip if ip else None
        self.domain = domain.replace("http://", "").replace("https://", "").rstrip("/") if domain else None
        self.proxy = {"http": proxy, "https": proxy} if proxy else None
        self.output_file_name = output_file_name if output_file_name else None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        }
        self.url=None
        self.subdomains=[]

    def search(self):
        if "-i" not in sys.argv and "-d" not in sys.argv:
            sys.exit("请指定一个ip或域名")

        if self.ip and not self.domain:
            self.url = f"https://rapiddns.io/s/{self.ip}"
        if self.domain and not self.ip:
            self.url = f"https://rapiddns.io/s/{self.domain}"

        print("正在查询请稍等...")

        try:
            response = requests.get(url=self.url, headers=self.headers, proxies=self.proxy, verify=False)
            selector = etree.HTML(response.text)
            total = selector.xpath('//div[@class="d-flex align-items-left"]/div[3]/span/text()')
            if int(total[0])==0:
                sys.exit("未查询到任何子域名")
            if int(total[0])>100:
                subdomains = selector.xpath('//table[@id="table"]//tr/td[1]/text()')
                subdomains = list(set(subdomains))
                for subdomain in subdomains:
                    self.subdomains.append(subdomain)
                for i in range(2,math.ceil(int(total[0])/100)+1):
                    url=f"{self.url}?page={i}"
                    response2 = requests.get(url=url, headers=self.headers, proxies=self.proxy, verify=False)
                    selector2 = etree.HTML(response2.text)
                    subdomains = selector2.xpath('//table[@id="table"]//tr/td[1]/text()')
                    subdomains = list(set(subdomains))
                    for subdomain in subdomains:
                        self.subdomains.append(subdomain)
            self.subdomains=list(set(self.subdomains))
            for subdomain in self.subdomains:
                print(subdomain)
        except Exception as e:
            print(e)

        if "-o" in sys.argv:
            with open(f"{self.output_file_name}","a",encoding='utf-8') as file:
                file.write("")
                for subdomain in self.subdomains:
                    file.write(subdomain+'\n')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", dest="ip", help="指定一个ip或ip范围,例如-i xx.xx.xx.0/24", required=False)
    parser.add_argument("-d", "--domain", dest="domain", help="指定一个域名", required=False)

    parser.add_argument("-p", "--proxy", "-proxy", dest="proxy", help="设置代理,例如:--proxy=http://127.0.0.1:8080",
                        required=False)
    parser.add_argument("-o", "--output", dest="output_file_name", help="输出到一个指定文件", required=False)
    args = parser.parse_args()
    rapiddns_search = RapidDnsSearch(args.ip,args.domain,  args.proxy, args.output_file_name)
    rapiddns_search.search()

if __name__ == "__main__":
    main()

