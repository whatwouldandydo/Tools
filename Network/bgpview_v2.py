"""
Author: www.linkedin.com/in/whatwouldandydo
Date: 2021-06-17
Summary: Edit codes from bgpview.py to make it shorter, don't repeat same code.
Use BGPView API to perform nslookup for BGP ASN, Prefixes, Peers,
Upstreams, Downstream and IP.
"""

import requests
import json
import time
import traceback
from pprint import pprint
from urllib3.exceptions import InsecureRequestWarning

""" Disable SSL self-sign certificate warning """
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class RequestBGPapi:
    """ Replace as_number with number.
    Main URL = "https://api.bgpview.io/"
    ASN = "https://api.bgpview.io/asn/as_number"
    ASN Prefixes = "https://api.bgpview.io/asn/as_number/prefixes"
    ASN Peers = "https://api.bgpview.io/asn/as_number/peers"
    ASN Upstreams = "https://api.bgpview.io/asn/as_number/upstreams"
    ASN Downstreams = "https://api.bgpview.io/asn/as_number/downstreams"
    ASN IXs = "https://api.bgpview.io/asn/as_number/ixs"

    # Replace ip_address/cidr with network/mask (/24).
    Prefix = "https://api.bgpview.io/prefix/ip_address/cidr"

    # Replace ip_address with individual IP address.
    IP = "https://api.bgpview.io/ip/ip_address"

    # Replace ix_id with number.
    IX = "https://api.bgpview.io/ix/ix_id"

    # Replace digitalocean with words
    Search = https://api.bgpview.io/search?query_term=digitalocean
    """

    def __init__(self, api_endpoint, asn_ip_var):
        """ Get variables for API endpoint and ASN/IP/IX/Prefix """
        self.api_endpoint = api_endpoint
        self.asn_ip_var = asn_ip_var

    def run_bgpview_api(self):
        """ A Global method to run API request
        Replace as_number, ip_address/cidr, ip_address, ix_id,
        and digitalocean with valid user entered variable
        """

        self.data_from_api = None

        if "as_number" in self.api_endpoint:
            bgpview_url = self.api_endpoint.replace("as_number", str(self.asn_ip_var))
        elif "ip_address/cidr" in self.api_endpoint:
            bgpview_url = self.api_endpoint.replace("ip_address/cidr", str(self.asn_ip_var))
        elif "ip_address" in self.api_endpoint:
            bgpview_url = self.api_endpoint.replace("ip_address", str(self.asn_ip_var))
        elif "ix_id" in self.api_endpoint:
            bgpview_url = self.api_endpoint.replace("ix_id", str(self.asn_ip_var))
        elif "digitalocean" in self.api_endpoint:
            bgpview_url = self.api_endpoint.replace("digitalocean", str(self.asn_ip_var))

        self.web_url = bgpview_url

        """ When API request fails, retry it 3 times with 3 seconds wait """
        query_try = 0
        while query_try != 3:
            try:
                web_request = requests.get(f"{bgpview_url}", verify=False)
                time.sleep(0.5)

                if web_request.status_code == 200:
                    meta_data = web_request.json()
                    self.data_from_api = meta_data
                    # "ok" or "error""
                    self.api_status = meta_data["status"]
                    # "Query was successful" means good and has data
                    self.api_status_message = meta_data["status_message"]
                    break

            except Exception as e:
                print(f"===> ERROR: {e.args} <===")
                traceback.print_exc()
                print()

            query_try += 1
            print("Sleep 3 seconds")
            print(f"Query Try: {query_try}")
            time.sleep(1)
        else:
            print(f"===> ERROR: Query request to {bgpview_url} three times but failed. <===")
            print(f"===> ERROR: {bgpview_url} status code {web_request} <===\n")

        """ Return as tupble(dict, str, str)
        dict = self.data_from_api
        str = self.api_status
        str = self.api_status_message """
        return self.data_from_api, self.api_status, self.api_status_message


class RequestASN(RequestBGPapi):
    """ Get ASN information such as owner, country, and more..."""
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number"
        self.asn = None
        self.asn_name = None
        self.asn_location = None
        self.asn_date_allocated = None
        self.asn_date_updated = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_info(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            if status == "error" or "Malformed input" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid AS number. <===\n")
            elif status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                asn = data["asn"]
                asn_name = data["description_short"]
                asn_location = data["country_code"]
                asn_date_allocated = data["rir_allocation"]["date_allocated"]
                asn_date_updated = data["date_updated"]

                # "assigned", "allocated", "available", "reserved", "unknown"
                rir_allocation_status = data["rir_allocation"]["allocation_status"]

                # "assigned", "reserved", "unknown" 
                iana_assignment_status = data["iana_assignment"]["assignment_status"]

                if iana_assignment_status == "assigned":
                    if "unknown" not in rir_allocation_status:
                        self.asn = f"ASN: {asn}"
                        self.asn_name = f"Name: {asn_name}"
                        self.asn_location = f"Location: {asn_location}"
                        self.asn_date_allocated = f"Created Date: {asn_date_allocated}"
                        self.asn_date_updated = f"Last Update: {asn_date_updated}"

                elif "reserved" in iana_assignment_status and rir_allocation_status:
                    self.asn = f"ASN: {asn}"
                    self.asn_name = "Private AS Number (RFC6996)"
                    self.asn_location = "Use within the Organization Network"
                    self.asn_date_allocated = "N/A"
                    self.asn_date_updated = "N/A"
                elif "unknown" in iana_assignment_status and rir_allocation_status:
                    self.asn = f"ASN: {asn}"
                    self.asn_name = "Not a valid AS Number"
                    self.asn_location = "N/A"
                    self.asn_date_allocated = "N/A"
                    self.asn_date_updated = "N/A"
                else:
                    self.asn = f"ASN: {asn}"
                    self.asn_name = "NEED VALIDATION FROM HUMAN"
                    self.asn_location = "NEED VALIDATION FROM HUMAN"
                    self.asn_date_allocated = "NEED VALIDATION FROM HUMAN"
                    self.asn_date_updated = "NEED VALIDATION FROM HUMAN"
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()
            print()

        """ Return sample
            ('ASN: 1',
            'Name: Level 3 Parent, LLC',
            'Location: US',
            'Created Date: 2001-09-20 00:00:00',
            'Last Update: 2021-05-15 07:42:08') """
        return self.asn, self.asn_name, self.asn_location, self.asn_date_allocated, self.asn_date_updated


class RequestASNprefixes(RequestBGPapi):
    """ Get prefixes IPv4 and IPv6 from the AS number """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number/prefixes"
        self.ipv4_prefixes = None
        self.ipv4_parent_prefixes = None
        self.ipv6_prefixes = None
        self.ipv6_parent_prefixes = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_prefixes(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            ipv4_prefixes = []
            ipv4_parent_prefixes = []
            ipv6_prefixes = []
            ipv6_parent_prefixes = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                ipv4_prefixes_list = data["ipv4_prefixes"]
                ipv6_prefixes_list = data["ipv6_prefixes"]
                
                for line in ipv4_prefixes_list:
                    for k, v in line.items():
                        if type(v) == dict:
                            if v["prefix"] is not None:
                                parent = v["prefix"]
                                ipv4_parent_prefixes.append(parent)
                        elif k == "prefix":
                            ip = v
                        elif k == "description":
                            name = v
                        elif k == "country_code":
                            location = v
                            ipv4_info = f"<{ip} {name} ({location}>)"
                            ipv4_prefixes.append(ipv4_info)

                for line in ipv6_prefixes_list:
                    for k, v in line.items():
                        if type(v) == dict:
                            if v["prefix"] is not None:
                                parent = v["prefix"]
                                ipv6_parent_prefixes.append(parent)
                        elif k == "prefix":
                            ip = v
                        elif k == "description":
                            name = v
                        elif k == "country_code":
                            location = v
                            ipv6_info = f"<{ip} {name} ({location}>)"
                            ipv6_prefixes.append(ipv6_info)
            elif status == "error" or "Malformed" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid AS number. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(ipv4_prefixes) == 0:
                self.ipv4_prefixes = f"AS Number {self.asn_ip_var} has no IPv4 Prefixes"
            else:
                ipv4_prefixes.insert(0, f"AS Number {self.asn_ip_var} IPv4 Prefixes .....")
                self.ipv4_prefixes = ipv4_prefixes

            if len(ipv4_parent_prefixes) == 0:
                self.ipv4_parent_prefixes = f"AS Number {self.asn_ip_var} has no IPv4 Parent Prefixes"
            else:
                ipv4_parent_prefixes.insert(0, f"AS Number {self.asn_ip_var} IPv4 Parent Prefixes .....")
                self.ipv4_parent_prefixes = list(dict.fromkeys(ipv4_parent_prefixes))

            if len(ipv6_prefixes) == 0:
                self.ipv6_prefixes = f"AS Number {self.asn_ip_var} has no IPv6 Prefixes"
            else:
                ipv6_prefixes.insert(0, f"AS Number {self.asn_ip_var} IPv6 Prefixes .....")
                self.ipv6_prefixes = ipv6_prefixes

            if len(ipv6_parent_prefixes) == 0:
                self.ipv6_parent_prefixes = f"AS Number {self.asn_ip_var} has no IPv6 Parent Prefixes"
            else:
                ipv6_parent_prefixes.insert(0, f"AS Number {self.asn_ip_var} IPv6 Parent Prefixes .....")
                self.ipv6_parent_prefixes = list(dict.fromkeys(ipv6_parent_prefixes))

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        return self.ipv4_prefixes, self.ipv4_parent_prefixes, self.ipv6_prefixes, self.ipv6_parent_prefixes


class RequestASNPeers(RequestBGPapi):
    """ Get ASN IPv4 and IPv6 peering partners """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number/peers"
        self.ipv4_asn_peers = None
        self.ipv6_asn_peers = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_peers(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            ipv4_peers = []
            ipv6_peers = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                ipv4_peers_list = data["ipv4_peers"]
                ipv6_peers_list = data["ipv6_peers"]

                for line in ipv4_peers_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv4_asn_info = f"<{asn} -- {name} -- {location}>"
                            ipv4_peers.append(ipv4_asn_info)

                for line in ipv6_peers_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv6_asn_info = f"<{asn} -- {name} -- {location}>"
                            ipv6_peers.append(ipv6_asn_info)
            elif status == "error" or "Malformed" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid AS number. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(ipv4_peers) == 0:
                self.ipv4_asn_peers = "No IPv4 Peers"
            else:
                ipv4_peers.insert(0, f"AS Number {self.asn_ip_var} IPv4 Peering Partners .....")
                self.ipv4_asn_peers = ipv4_peers
            
            if len(ipv6_peers) == 0:
                self.ipv6_asn_peers = "No IPv6 Peers"
            else:
                ipv6_peers.insert(0, f"AS Number {self.asn_ip_var} IPv6 Peering Partners .....")
                self.ipv6_asn_peers = ipv6_peers

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        # Return sample <ASN: 394487 -- Name: Data Truck -- Location: US>
        return self.ipv4_asn_peers, self.ipv6_asn_peers


class RequestANSupstreams(RequestBGPapi):
    """ Get Upstream BGP AS number, names, and countries """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number/upstreams"
        self.ipv4_upstreams_asn = None
        self.ipv6_upstreams_asn = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_upstreams(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            ipv4_upstreams = []
            ipv6_upstreams = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                ipv4_upstreams_list = data["ipv4_upstreams"]
                ipv6_upstreams_list = data["ipv6_upstreams"]

                for line in ipv4_upstreams_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv4_up_info = f"<{asn} -- {name} -- {location}>"
                            ipv4_upstreams.append(ipv4_up_info)

                for line in ipv6_upstreams_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv6_up_info = f"<{asn} -- {name} -- {location}>"
                            ipv6_upstreams.append(ipv6_up_info)
            elif status == "error" or "Malformed" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid AS number. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(ipv4_upstreams) == 0:
                self.ipv4_upstreams_asn = f"AS Number {self.asn_ip_var} NO IPv4 Upstreams"
            else:
                ipv4_upstreams.insert(0, f"AS Number {self.asn_ip_var} IPv4 Upstreams .....")
                self.ipv4_upstreams_asn = ipv4_upstreams

            if len(ipv6_upstreams) == 0:
                self.ipv6_upstreams_asn = f"AS Number {self.asn_ip_var} NO IPv6 Upstreams"
            else:
                ipv6_upstreams.insert(0, f"AS Number {self.asn_ip_var} IPv6 Upstreams .....")
                self.ipv6_upstreams_asn = ipv6_upstreams

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

    
        # Return sample <ASN: 394487 -- Name: Data Truck -- Location: US>
        return self.ipv4_upstreams_asn, self.ipv6_upstreams_asn


class RequestASNdownstreams(RequestBGPapi):
    """ Get Downstreams BGP AS number, names, and countries """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number/downstreams"
        self.ipv4_downstreams_asn = None
        self.ipv6_downstreams_asn = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_downstreams(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            ipv4_downstreams = []
            ipv6_downstreams = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                ipv4_downstreams_list = data["ipv4_downstreams"]
                ipv6_downstreams_list = data["ipv6_downstreams"]

                for line in ipv4_downstreams_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv4_down_info = f"<{asn} -- {name} -- {location}>"
                            ipv4_downstreams.append(ipv4_down_info)
                
                for line in ipv6_downstreams_list:
                    for k, v in line.items():
                        if k == "asn":
                            asn = f"ASN: {v}"
                        elif k == "description":
                            name = f"Name: {v}"
                        elif k == "country_code":
                            location = f"Location: {v}"
                            ipv6_down_info = f"<{asn} -- {name} -- {location}>"
                            ipv6_downstreams.append(ipv6_down_info)
            elif status == "error" or "Malformed" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid AS number. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(ipv4_downstreams) == 0:
                self.ipv4_downstreams_asn = f"AS Number {self.asn_ip_var} NO IPv4 Downstreams"
            else:
                ipv4_downstreams.insert(0, f"AS Number {self.asn_ip_var} IPv4 Downstreams .....")
                self.ipv4_downstreams_asn = ipv4_downstreams
            
            if len(ipv6_downstreams) == 0:
                self.ipv6_downstreams_asn = f"AS Number {self.asn_ip_var} NO IPv6 Downstreams"
            else:
                ipv6_downstreams.insert(0, f"AS Number {self.asn_ip_var} IPv6 Downstreams .....")
                self.ipv6_downstreams_asn = ipv6_downstreams

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        # Return sample <ASN: 29447 -- Name: Iliad Italia S.p.A -- Location: FR>
        return self.ipv4_downstreams_asn, self.ipv6_downstreams_asn


class RequestASNixs(RequestBGPapi):
    """ Get Internet Exchange name, remote peers information
    such as AS number, name, IPv4/IPv6 peering addresses,
    city, country, and speed
    """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/asn/as_number/ixs"
        self.asn_ixs = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_asn_ixs(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            ixs_list = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]

                for line in data:
                    for k, v in line.items():
                        if k == "ix_id":
                            ix = f"IX ID: {v}"
                        elif k == "name":
                            name = v
                        elif k == "name_full":
                            if name is not None:
                                name_full = f"Name: {v} ({name})"
                            else:
                                name_full = f"Name: {v}"
                        elif k == "country_code":
                            country = v
                        elif k == "city":
                            if country is not None:
                                location = f"Location: {v}, {country}"
                            elif v is not None:
                                location = f"Location: {v}"
                            else:
                                location = f"Location: None"
                        elif k == "ipv4_address":
                            if v is not None:
                                ipv4 = f"IPv4 Address: {v}"
                            else:
                                ipv4 = f"IPv4 Address: None"
                        elif k == "ipv6_address":
                            if v is not None:
                                ipv6 = f"IPv6 Address: {v}"
                            else:
                                ipv6 = f"IPv6 Address: None"
                        elif k == "speed":
                            if v == 0 or v == "0" or v is None:
                                speed = f"Speed: None"
                            else:
                                speed = f"Speed: {v}"
                            ixs_info = f"<{ix} -- {name_full} -- {location} -- {ipv4} -- {ipv6} -- {speed}>"
                            ixs_list.append(ixs_info)
            elif status == "error" or "Malformed" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid Internet Exchange number. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(ixs_list) == 0:
                self.asn_ixs = f"AS Number {self.asn_ip_var} has NO Internet Exchange data."
            else:
                ixs_list.insert(0, f"AS Number {self.asn_ip_var} Internet Exchange Information .....")
                self.asn_ixs = ixs_list

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        return self.asn_ixs


class RequestPrefix(RequestBGPapi):
    """ Get prefix owner, ASN, address, and upstreams ASN """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/prefix/ip_address/cidr"
        self.prefix_detail = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_prefix(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            prefix_list = []

            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]

                prefix = data["prefix"]
                name = data["name"]
                description_short = data["description_short"]
                country = data["country_codes"]["whois_country_code"]
                date_allocated = data["rir_allocation"]["date_allocated"]
                asns = data["asns"]

                for line in asns:
                    for k, v in line.items():
                        if k == "asn":
                            asn = v
                        elif k == "name":
                            as_name = v
                        elif k == "description":
                            as_desc = v
                        elif k == "country_code":
                            as_country = v
                
                prefix_info = f"<Prefix: {prefix} -- Name: {description_short} -- Location: {country} -- Date Assigned: {date_allocated} | ASN: {asn} Name: {as_name} Location:{as_country}>"
                prefix_list.append(prefix_info)
            elif status == "error" and "Prefix not found" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} Prefix not found in BGP table or not a valid prefix. <===\n")
            elif status == "error" and "Malformed input" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid entry. Example: 192.209.63.0/24. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

            if len(prefix_list) == 0:
                self.prefix_detail = f"No Data on prefix {self.asn_ip_var}"
            else:
                self.prefix_detail = prefix_list
        
        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        return self.prefix_detail


class RequestIPAddress(RequestBGPapi):
    """ Get public IP address owner, ASN, and country"""
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/ip/ip_address"
        self.ip_address_details = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_ip_address(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                ip = data["ip"]

                asn_list = []

                ip_prefixes_list = data["prefixes"]

                if len(ip_prefixes_list) == 0:
                    prefix = "None"
                    description = "None"
                    ip_location = "None"
                    asn_list.append("None")
                elif len(ip_prefixes_list) != 0:
                    for line in ip_prefixes_list:
                        if line is not None:
                            for k, v in line.items():
                                if k == "prefix":
                                    prefix = v
                                elif k == "description":
                                    description = v
                                elif k == "country_code":
                                    ip_location = v
                                elif k == "asn":
                                    asn = v["asn"]
                                    asn_desc = v["description"]
                                    asn_location = v["country_code"]
                                    if asn is not None:
                                        asn_info = f"ASN: {asn}, Name: {asn_desc}, Location: {asn_location}"
                                        asn_list.append(asn_info)

                ip_info = f"<IP: {ip} Prefix: {prefix} -- Name: {description} -- Location: {ip_location} -- Used by Autonomous Systems: {asn_list}>"

                self.ip_address_details = ip_info

            elif status == "error" and "Malformed input" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid entry. Example: 192.209.63.1 <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")


        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()
        
        return self.ip_address_details


class RequestInternetExchange(RequestBGPapi):
    """ Get Internet Exchange name, name, and member ASNs, IPv4/IPv6, speed"""
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/ix/ix_id"
        self.internet_exchange_details = None
        self.internet_exchange_members = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_internet_exchange(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]
        print(status_message)

        try:
            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                name = data["name_full"]
                city = data["city"]
                country = data["country_code"]
                ix_asn_members = data["members_count"]
                asn_members = data["members"]

                if city is None:
                    ix_info = f"IX: {self.asn_ip_var} -- Name: {name} -- ASN Membership: {ix_asn_members} -- Location: {country}"
                    self.internet_exchange_details = ix_info
                else:
                    ix_info = f"IX: {self.asn_ip_var} -- Name: {name} -- ASN Membership: {ix_asn_members} -- Location: {city}, {country}"
                    self.internet_exchange_details = ix_info

                as_info_list = []
                for line in asn_members:
                    for k, v in line.items():
                        if k == "asn":
                            asn = v
                        elif k == "description":
                            as_name = v
                        elif k == "country_code":
                            as_location = v
                        elif k == "ipv4_address":
                            ipv4 = v
                        elif k == "ipv6_address":
                            ipv6 = v
                        elif k == "speed":
                            if v == 0:
                                speed = None
                            else:
                                speed = v
                                as_info = f"<ASN: {asn}, Name: {as_name}, Location: {as_location}, IPv4: {ipv4}, IPv6: {ipv6}, Speed: {speed}>"
                                as_info_list.append(as_info)
                    
                    self.internet_exchange_members = as_info_list

            elif status == "error" and "Could not find IX" in status_message:
                print(f"===> ERROR: {self.asn_ip_var} is NOT a valid entry. <===\n")
            else:
                print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()
        
        return self.internet_exchange_details, self.internet_exchange_members


class RequestBGPSearch(RequestBGPapi):
    """ Search for word in BGPView.
    Data return as dict key name asn,
    ipv4_prefixes, ipv6_prefixes, internet_exchanges """
    def __init__(self, api_endpoint, asn_ip_var):
        api_endpoint = "https://api.bgpview.io/search?query_term=digitalocean"
        self.asn_ip_var = asn_ip_var
        self.asn_info = None
        self.ipv4_prefixes_info = None
        self.ipv6_prefixes_info = None
        self.internet_exchanges_info = None
        super().__init__(api_endpoint, asn_ip_var)

    def get_search_result(self):
        raw_data = self.run_bgpview_api()
        meta_data = raw_data[0]
        status = raw_data[1]
        status_message = raw_data[2]

        try:
            if status == "ok" and "Query was successful" in status_message:
                data = meta_data["data"]
                asns = data["asns"]
                ipv4_prefixes = data["ipv4_prefixes"]
                ipv6_prefixes = data["ipv6_prefixes"]
                internet_exchanges = data["internet_exchanges"]

                asn_list = []
                if len(asns) != 0:
                    for line in asns:
                        for k, v in line.items():
                            if k == "asn":
                                as_num = v
                            elif k == "name":
                                as_name = v
                            elif k == "description":
                                as_desc = v
                            elif k == "country_code":
                                as_location = v
                                as_info = f"<ASN: {as_num}, Name: {as_name}, Description:{as_desc}, Location: {as_location}>"
                                asn_list.append(as_info)

                ipv4_list = []
                if len(ipv4_prefixes) != 0:
                    for line in ipv4_prefixes:
                        for k, v in line.items():
                            if k == "prefix":
                                ipv4_pref = v
                                print(ipv4_pref)
                            elif k == "country_code":
                                ipv4_location = v
                            elif k == "description":
                                ipv4_name = v
                                ipv4_info = f"<IPv4 Prefix: {ipv4_pref}, Name: {ipv4_name}, Location: {ipv4_location}>"
                                ipv4_list.append(ipv4_info)

                ipv6_list = []
                if len(ipv6_prefixes) != 0:
                    for line in ipv6_prefixes:
                        for k, v in line.items():
                            if k == "prefix":
                                ipv6_pref = v
                            elif k == "country_code":
                                ipv6_location = v
                            elif k == "description":
                                ipv6_name = v
                                ipv6_info = f"<IPv4 Prefix: {ipv6_pref}, Name: {ipv6_name}, Location: {ipv6_location}>"
                                ipv6_list.append(ipv6_info)

                ix_list = []
                if len(internet_exchanges) != 0:
                    for line in internet_exchanges:
                        for k, v in line.items():
                            if k == "ix_id":
                                ix_id = v
                            elif k == "name_full":
                                ix_name = v
                            elif k == "country_code":
                                ix_country = v
                            elif k == "city":
                                ix_city = v
                                if ix_city is None:
                                    ix_info = f"<Internet Exchange ID: {ix_id}, Name: {ix_name}, Location: {ix_country}>"
                                    ix_list.append(ix_info)
                                else:
                                    ix_info = f"<Internet Exchange ID: {ix_id}, Name: {ix_name}, Location: {ix_city}, {ix_country}>"
                                    ix_list.append(ix_info)
                else:
                    print(f"===> Unkown Error: Please Review {self.web_url}, Status Code: {status}, Status Message:{status_message}<===\n")

                self.asn_ip_var = f'BGPView Search: "{self.asn_ip_var}" '

                if len(asn_list) != 0:
                    self.asn_info = asn_list
                else:
                    self.asn_info = f"No Autonomous System Numbers Found."

                if len(ipv4_list) != 0:
                    self.ipv4_prefixes_info = ipv4_list
                else:
                    self.ipv4_prefixes_info = f"No IPv4 Information Found."

                if len(ipv6_list) != 0:
                    self.ipv6_prefixes_info = ipv6_list
                else:
                    self.ipv6_prefixes_info = f"No IPv6 Information Found."
                
                if len(ix_list) != 0:
                    self.internet_exchanges_info = ix_list
                else:
                    self.internet_exchanges_info = f"No Internet Exchange Information Found."

        except Exception as e:
            print(f"===> ERROR: {e.args} <===")
            traceback.print_exc()

        return self.asn_ip_var, self.asn_info, self.ipv4_prefixes_info, self.ipv6_prefixes_info, self.internet_exchanges_info


if __name__ == "__main__":
    a = "https://api.bgpview.io/"
    b = 1
    c = "2001:1508::/32"
    d = "193.189.100.205"
    e = "vietnam"
    f = "dfdsfdd"

    t1 = RequestASN(a, b)
    # print(t1.get_asn_info())

    t2 = RequestASNprefixes(a, b)
    # print(t2.get_asn_prefixes())

    t3 = RequestASNPeers(a, b)
    # print(t3.get_asn_peers())

    t4 = RequestANSupstreams(a, b)
    # print(t4.get_asn_upstreams())

    t5 = RequestASNdownstreams(a, b)
    # print(t5.get_asn_downstreams())

    t6 = RequestASNixs(a, b)
    # print(t6.get_asn_ixs())

    t7 = RequestPrefix(a, c)
    # print(t7.get_prefix())

    t8 = RequestIPAddress(a, d)
    # print(t8.get_ip_address())

    t9 = RequestInternetExchange(a, b)
    # print(t9.get_internet_exchange())

    t10 = RequestBGPSearch(a, e)
    # print(t10.get_search_result())


    import datetime

    d1 = datetime.datetime.now()

    for i in range(65555):
    # for i in range(64000, 65555):
        d2 = datetime.datetime.now()
        t1 = RequestASN(a, i)
        print(t1.get_asn_info())
        print()
        
        # t2 = RequestASNprefixes(a, i)
        # print(t2.get_asn_prefixes())

        # t3 = RequestASNPeers(a, i)
        # print(t3.get_asn_peers())

        # t4 = RequestANSupstreams(a, i)
        # print(t4.get_asn_upstreams())

        # t5 = RequestASNdownstreams(a, i)
        # print(t5.get_asn_downstreams())

        # t6 = RequestASNixs(a, i)
        # print(t6.get_asn_ixs())

        # t7 = RequestPrefix(a, c)
        # print(t7.get_prefix())

        # t8 = RequestIPAddress(a, d)
        # print(t8.get_ip_address())

        # t9 = RequestInternetExchange(a, i)
        # print(t9.get_internet_exchange())

        # t10 = RequestBGPSearch(a, e)
        # print(t10.get_search_result())

        d3 = datetime.datetime.now()
        print(f"Running Time: {d2 - d1}")
        print(f"Query Time: {d3 - d2}")
        print()
