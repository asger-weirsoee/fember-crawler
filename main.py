import datetime
import re

import scrapy


class Fember:
    id: str = None
    name: str = None
    email: str = None
    user: str = None
    balance: str = None
    username: str = None
    year: str = None
    last_pay: str = None
    last_pay_date: datetime.datetime = None

    def remove_td(self, td):
        if td is None:
            return ""
        return td.replace('<td>', '').replace('</td>', '')

    def __str__(self):
        return '{ "id": "' + self.remove_td(self.id) + ', "username": "' + self.remove_td(
            self.username) + '", name: "' + \
               self.remove_td(self.name) + '", "email": "' + self.remove_td(self.email) + \
               '", "balance": "' + self.remove_td(self.balance) + '", "year": "' + self.remove_td(
            self.year) + \
               '", "last_pay": "' + self.remove_td(
            self.last_pay) + '", "last_pay_date": "' + self.last_pay_date.isoformat() if self.last_pay_date else "" + '"}'


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://stregsystem.fklub.dk/10/user/' + str(k) for k in range(10, 1_000_000)]
    custom_settings = {
        "RETRY_ENABLED": False,
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response, **kwargs):
        fember = Fember()
        balance: str = response.css('h4::text').get()

        balance = balance.replace('Du har ', '').replace('kroner til gode!', '').strip()

        fember.id = response.xpath('/html/body/table[2]/tr[2]/td[2]').extract_first()

        fember.username = response.xpath('/html/body/table[2]/tr[3]/td[2]').extract_first()

        first_name = response.xpath('/html/body/table[2]/tr[4]/td[2]').extract_first()
        last_name = response.xpath('/html/body/table[2]/tr[5]/td[2]').extract_first()

        if first_name and last_name:
            fember.name = first_name + ' ' + last_name
        else:
            raise Exception(response.xpath)

        fember.email = response.xpath('/html/body/table[2]/tr[6]/td[2]').extract_first()

        fember.balance = balance

        fember.year = response.xpath('/html/body/table[2]/tr[7]/td[2]').extract_first()

        xxx = response.xpath('/html/body/center[4]').extract_first()
        if xxx:
            zzz = extract_last_pay(xxx)
            if zzz:
                fember.last_pay = zzz
                fember.last_pay_date = extract_date_information(xxx)

        with open('fember_list.txt', 'a+') as f:
            f.write(str(fember) + '\n')


get_monies = re.compile(r"((\d+)\.\d{2})")
get_date = re.compile(r"(d\..+\d{2}:\d{2})")


def extract_last_pay(last_pay):
    matches = get_monies.findall(last_pay)
    if len(matches) > 0:
        return matches[0][0]


def translate_month(month):
    return {
        'januar': 1,
        'februar': 2,
        'marts': 3,
        'april': 4,
        'maj': 5,
        'juni': 6,
        'juli': 7,
        'august': 8,
        'september': 9,
        'oktober': 10,
        'november': 11,
        'december': 12,
    }.get(month, None)


def extract_date_information(last_pay):
    """
    Date looks like this:
    d. 02. September 2022 14:55
    :param last_pay:
    :return:
    """
    matches = get_date.findall(last_pay)
    if len(matches) > 0:
        # Convert to datetime
        date_string = matches[0].replace('d.', '').replace('.', '').strip().split(' ')
        time = date_string[3].split(':')
        return datetime.datetime(int(date_string[2]), translate_month(date_string[1]), int(date_string[0]),
                                 int(time[0]), int(time[1]))
