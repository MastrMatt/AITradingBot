# AI Stock Trading Bot Application

This project is a Python-based application utilizing the Lumibot framework to implement a sentiment-driven trading strategy. It integrates advanced natural language processing (NLP) techniques, specifically the FinBERT model, to analyze financial news sentiment and make informed trading decisions based on predefined criteria. The application aims to capitalize on market movements influenced by public sentiment towards specific stocks, providing a unique approach to algorithmic trading.

## Features

- **Customizable Strategy Parameters**: Allows for the adjustment of critical trading parameters such as cash allocation, sentiment threshold scores, and profit/loss targets.
- **Sentiment Analysis Integration**: Utilizes the FinBERT model via the Hugging Face Transformers library for analyzing the sentiment of financial news articles.
- **Alpaca Trading Integration**: Leverages the Alpaca trading platform for executing trades based on the sentiment analysis results.
- **Backtesting Capabilities**: Supports backtesting the strategy against historical data to evaluate performance and optimize parameters.
- **Reliable News Articles**: Retrieves Reliable News Articles from Alpaca using its API. 
- **Environment Variables Management**: Uses environment variables for secure management of sensitive information like API keys and endpoints.

## Setup

To run this application locally, follow these steps:

1. **Clone the Repository**:
   ```
   git clone https://github.com/YourGitHubUsername/lumibot-sentiment-strategy.git
   cd lumibot-sentiment-strategy
   ```

2. **Install Dependencies**:
   Ensure Python 3.x is installed. Then, install the required packages listed in `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

3. **Create an Alpaca Trading Account**:
    Visit [ALPACA](https://alpaca.markets/) in order to create a trading account. Generate your API Key ,API Secret and API endpoint

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in the missing values, such as your Alpaca API key and endpoint.

4. **Run the Application**:
   Execute the main script to start the application:
   ```
   python main.py
   ```

## Usage

Upon running the application, it initializes the sentiment strategy with the specified parameters. This parameters can be modified to change the Trading Bot's behaviour. Depending on the `live` flag set in the main script, the application either runs the strategy in live trading mode or performs backtesting against historical data. The strategy analyzes recent news articles for the selected stock, evaluates their sentiment, and makes trading decisions based on the predefined thresholds and parameters.

### Strategy Parameters

The strategy is initialized with several key parameters that define its behavior:

- **`symbol`**: The ticker symbol of the stock to trade.
- **`cash_at_risk`**: The proportion of the portfolio value allocated for trading. This parameter determines how much capital is exposed to the market at any given time.
- **`threshold_score`**: The minimum confidence score required for a sentiment to be classified as positive or negative. Higher values increase the stringency of the sentiment classification.
- **`threshold_ratio`**: The minimum ratio of positive/negative sentiments required to trigger a trade. This helps filter out periods of mixed sentiment.
- **`stop_loss`**: The ratio loss(float) allowed before automatically selling the position to mitigate losses.
- **`take_profit`**: The ratio profit(float) target before exiting a winning position to lock in gains.
- **`days_prior`**: The number of days prior to the current to get news articles to analyze.


## Future Considerations

1. Integrate use with other brokers
2. Expand the strategy to support multiple assets beyond individual stocks.


## Author
Matthew Neba / [@MastrMatt](https://github.com/MastrMatt)

## License
This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions to this project are welcome Please submit pull requests or open issues to discuss potential improvements or report bugs.



---
