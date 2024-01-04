from datetime import datetime, timedelta
import asyncio

import aiofiles
import aiohttp


class GetExchage:
    def __init__(self, message: str, name: str) -> None:
        self.all_currencies = 'EUR', 'USD', 'CHF', 'GBP', 'PLZ', 'SEK', 'CAD', 'XAU'
        self.currencies = ['EUR', 'USD']
        self.days = 1
        self.customer_name = name
        self.parsing(message)

    def parsing(self, message):
        for cmd in message.upper().split():
            if cmd.isdigit():
                self.days = min(int(cmd), 10)
            if cmd in self.all_currencies:
                self.currencies.append(cmd)

    async def log_exchange_rate_requests(self):
        async with aiofiles.open('exchr_cmd.log', 'a') as afh:
            await afh.write(
                f"{datetime.today().strftime('%d.%m.%Y  %H:%M:%S')}  {self.customer_name} requested {self.currencies} currencies ExRate for last {self.days} days \n")

    async def log_exceptions(self, message):
        async with aiofiles.open('exchr_cmd.log', 'a') as afh:
            await afh.write(f"{datetime.today().strftime('%d.%m.%Y  %H:%M:%S')}  {message} \n")

    def __get_dates_list(self, days) -> list:
        return [(datetime.now() - timedelta(days=day)).strftime('%d.%m.%Y') for day in range(int(days))]

    async def creating_async_tasks(self, dates):
        async with asyncio.TaskGroup() as tg:
            return [tg.create_task(self.__get_currencies_from_api_pb(date)) for date in dates]

    async def __get_currencies_from_api_pb(self, date):
        async with aiohttp.ClientSession() as session:
            params = {'json': '', 'date': date}
            try:
                async with session.get('https://api.privatbank.ua/p24api/exchange_rates', params=params,
                                       ssl=True) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        asyncio.create_task(self.log_exceptions(response.status))
            except aiohttp.ClientConnectionError as err:
                asyncio.create_task(self.log_exceptions(err))

    def __json_to_text(self, cur):
        filtered_currencies = list(filter(lambda x: x['currency'] in self.currencies, cur['exchangeRate']))
        formatted_currencies = [
            [cur['date'], x['currency'], {'sale': x.get('saleRate'), 'purchase': x.get('purchaseRate')}] for x in
            filtered_currencies]
        return formatted_currencies

    def __return_readable_results(self, responce_list):
        message = "Exchange rates:\n"

        for date_group in [self.__json_to_text(r.result()) for r in responce_list]:
            for date, currency, rates in date_group:
                message += f"<br>  Date: {date}, Currency: {currency}<br>"
                message += f"    Sale: {rates['sale']}, Purchase: {rates['purchase']}<br>"

        message += '''
    You can enhance your request by typing:<br>
    exchange EUR 2    <-- get exchange rate for last two days<br>
    available currencies: 'EUR', 'USD', 'CHF', 'GBP', 'PLZ', 'SEK', 'CAD', 'XAU'<br>
    '''
        return message

    async def get_exchange(self):
        asyncio.create_task(self.log_exchange_rate_requests())
        dates = self.__get_dates_list(self.days)
        tasks = await self.creating_async_tasks(dates)
        return self.__return_readable_results(tasks)
