from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from datetime import datetime

import os
from dotenv import load_dotenv

from alpaca_trade_api import REST
from timedelta import Timedelta

# NLP module
from NLP import finbert_analysis

# load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ENDPOINT = os.getenv("ENDPOINT")


ALPACA_CONFIG = {"API_KEY": API_KEY, "API_SECRET": API_SECRET, "PAPER": True}


# Define the strategy
class SentimentStrat(Strategy):
    def initialize(self, symbol: str, cash_at_risk: float):
        # Initialize alpaca API
        self.api = REST(API_KEY, API_SECRET, ENDPOINT)

        # Define the symbol to trade
        self.symbol = symbol

        # Time to sleep between trading iterations
        self.sleep_time = "24H"

        # Set up my own custom parameters as class attributes
        self.last_trade = None
        self.cash_at_risk = cash_at_risk

    def position_sizing(self):
        """
        Calculate the number of shares to buy based on the cash at risk

        """

        cash = self.get_cash()

        # Get the last price of the stock
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)

        return cash, last_price, quantity

    def on_trading_iteration(self):

        # Determine the number of shares to buy
        cash, last_price, quantity = self.position_sizing()

        # Additional check to ensure enough cash to buy
        if cash < last_price:
            return

        if self.last_trade is None:
            news = self.get_news(days_prior=5)
            print(news)

            # Setup the order, gain 30% and lose 10%
            order = self.create_order(
                self.symbol,
                10,
                "buy",
                type="bracket",
                take_profit_price=last_price * 1.3,
                stop_loss_price=last_price * 0.9,
            )

            self.submit_order(order)
            self.last_trade = "buy"

    def get_dates_news(self, days_prior):
        """
        Get the start and end date for the news API to use.

        Args:
        days_prior: int, the number of days prior to the current date to get news for

        Returns:
        start_time: str, the start time in the correct format
        end_time: str, the end time in the correct format

        """
        current_time = self.get_datetime()
        start_time = current_time - Timedelta(days=days_prior)
        end_time = current_time

        # Format the dates to be in the correct format
        start_time = start_time.strftime("%Y-%m-%d")
        end_time = end_time.strftime("%Y-%m-%d")

        return start_time, end_time

    def get_news(self, days_prior: int = 2):
        """
        Get news data from the news API
        """

        start_time, end_time = self.get_dates_news(days_prior)

        # Get the news data
        news = self.api.get_news(self.symbol, start=start_time, end=end_time)

        # Extract headline and summary and combine them
        for index, article in enumerate(news):
            headline = article.__dict__["_raw"]["headline"]
            summary = article.__dict__["_raw"]["summary"]

            news[index] = headline + summary

        # Extract the headlines
        headlines = [article.__dict__["_raw"]["headline"] for article in news]

        # Extract the summary
        summary = [article.__dict__["_raw"]["summary"] for article in news]

        print(news)

        pass


broker = Alpaca(ALPACA_CONFIG)
strategy = SentimentStrat(
    name="Sentiment Strategy",
    broker=broker,
    parameters={"symbol": "SPY", "cash_at_risk": 0.5},
)


# Backtest the strategy
start_date = datetime(2020, 1, 1)
end_date = datetime(2020, 1, 20)

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_at_risk": 0.5},
)
