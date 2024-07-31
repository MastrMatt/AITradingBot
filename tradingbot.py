from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy
from lumibot.traders import Trader
from lumibot.entities import TradingFee
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
#! NEED TO ADD ROBUSTNESS IF TRADES ARE NOT EXECUTED


class SentimentStrat(Strategy):
    def initialize(
        self,
        symbol: str,
        cash_at_risk: float,
        threshold_score: float,
        threshold_ratio: float,
        stop_loss: float,
        take_profit: float,
        days_prior: int,
        sleeptime: str,
    ):
        # Initialize alpaca API
        self.api = REST(API_KEY, API_SECRET, ENDPOINT)

        # Define the symbol to trade
        self.symbol = symbol

        # Time to sleep between trading iterations
        self.sleeptime = sleeptime

        # Set up my own custom parameters as class attributes
        self.cash_at_risk = cash_at_risk
        self.threshold_score = threshold_score
        self.threshold_ratio = threshold_ratio
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.days_prior = days_prior

        # some class attributes
        self.last_trade = None

    def position_sizing(self):
        """
        Calculate the number of shares to buy based on the cash at risk

        """

        cash = self.get_cash()

        # Get the last known price of the stock
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)

        return cash, last_price, quantity

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

    def sentiments_thresholding(self, sentiments):
        """
        Aggregate the sentiment analysis results and return the final sentiment

        Args:
        sentiments: list, the sentiment analysis results
        threshold_score: float, the confidence score for the sentiment to be considered positive or negative
        threshold_ratio: float, the ratio of positive or negative sentiments to achieve
        goal_sentiment: str, the goal sentiment to achieve (positive or negative)

        Returns:
        threshold_met: bool, whether the threshold for the sentiment is met
        """
        # Get the number of positive, negative, and neutral sentiments
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        positive_threshold_met = False
        negative_threshold_met = False

        for sentiment in sentiments:
            if (
                sentiment["label"] == "positive"
                and sentiment["score"] >= self.threshold_score
            ):
                positive_count += 1
            elif (
                sentiment["label"] == "negative"
                and sentiment["score"] >= self.threshold_score
            ):
                negative_count += 1
            else:
                neutral_count += 1

        # Get the total number of sentiments
        total_count = positive_count + negative_count + neutral_count

        # Get the ratio of positive and negative sentiments
        positive_ratio = positive_count / total_count
        negative_ratio = negative_count / total_count

        # Check if the threshold for the sentiment is met
        if positive_ratio >= self.threshold_ratio:
            positive_threshold_met = True

        if negative_ratio >= self.threshold_ratio:
            negative_threshold_met = True

        print(f"Positive ratio: {positive_ratio}, Negative ratio: {negative_ratio}")
        return (positive_threshold_met, negative_threshold_met)

    def get_sentiments_signal(self):
        """

        Get the sentiment signal for the stock based on the news. The signal is based on the sentiment analysis of the news articles. The signal is positive if the sentiment is positive and the confidence score is above the threshold, and the signal is negative if the sentiment is negative and the confidence score is above the threshold.


        """

        start_time, end_time = self.get_dates_news(days_prior=self.days_prior)

        # Get the news data
        news = self.api.get_news(self.symbol, start=start_time, end=end_time)

        # Extract headline and summary and combine them
        for index, article in enumerate(news):
            headline = article.__dict__["_raw"]["headline"]
            summary = article.__dict__["_raw"]["summary"]

            news[index] = headline + summary

        # perform sentiment analysis on the news
        sentiments = finbert_analysis.get_sentiment(news)

        # perform thresholding on the sentiments
        positive_threshold_met, negative_threshold_met = self.sentiments_thresholding(
            sentiments
        )

        return positive_threshold_met, negative_threshold_met

    def on_trading_iteration(self):

        # Determine the number of shares to buy
        cash, last_price, quantity = self.position_sizing()

        # Additional check to ensure enough cash to buy at least one share
        if cash < last_price:
            return

        # Get the sentiment signal
        positive_threshold_met, negative_threshold_met = self.get_sentiments_signal()

        if positive_threshold_met:
            # price is going up, check is last order was a short
            if self.last_trade == "sell":
                # close the short, sell_all() is responsible for closing each open position and cancelling all open orders
                self.sell_all()

            # Setup the order, gain 30% and lose 10%
            order = self.create_order(
                self.symbol,
                quantity,
                "buy",
                type="bracket",
                take_profit_price=round(last_price * (1 + self.take_profit)),
                stop_loss_price=round(last_price * (1 - self.stop_loss)),
            )

            self.submit_order(order)
            self.last_trade = "buy"

        elif negative_threshold_met:
            # price is going down, check if last order was a buy
            if self.last_trade == "buy":
                # close the long, sell_all() is responsible for closing each open position and cancelling all open orders
                self.sell_all()

            # Setup the order, gain 30% and lose 10%
            order = self.create_order(
                self.symbol,
                quantity,
                "sell",
                type="bracket",
                take_profit_price=round(last_price * (1 - self.take_profit)),
                stop_loss_price=round(last_price * (1 + self.stop_loss)),
            )

            self.submit_order(order)
            self.last_trade = "sell"


if __name__ == "__main__":

    # whether to run the strategy in live mode
    live = False

    # Setup for backtesting and live trading
    trader = Trader()

    broker = Alpaca(ALPACA_CONFIG)

    strategy = SentimentStrat(
        name="Sentiment Strategy",
        broker=broker,
        parameters={
            "symbol": "SPY",
            "cash_at_risk": 0.5,
            "threshold_score": 0.8,
            "threshold_ratio": 0.2,
            "sleeptime": "24H",
            "stop_loss": 0.1,
            "take_profit": 0.3,
            "days_prior": 3,
        },
    )

    if live:
        trader.add_strategy(strategy)
        trader.run_all()
    else:

        # Backtest the strategy
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2021, 1, 1)

        # Create two trading fees, one that is a percentage and one that is a flat fee
        trading_fee_1 = TradingFee(flat_fee=5)  # $5 flat fee
        trading_fee_2 = TradingFee(percent_fee=0.02)  # 1% trading fee

        strategy.backtest(
            YahooDataBacktesting,
            start_date,
            end_date,
            parameters={
                "symbol": "SPY",
                "cash_at_risk": 0.5,
                "threshold_score": 0.8,
                "threshold_ratio": 0.2,
                "sleeptime": "24H",
                "stop_loss": 0.1,
                "take_profit": 0.3,
                "days_prior": 3,
            },
            buy_trading_fees=[trading_fee_1, trading_fee_2],
            sell_trading_fees=[trading_fee_1, trading_fee_2],
        )
