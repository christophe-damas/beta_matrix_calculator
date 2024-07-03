import pandas as pd
import numpy as np
import yfinance as yf

beta_tickers = ['BTC', 'ETH']

def ticker_list():
    return ["HEX", "XRP", "SOL", "LQTY", "MKR", "BNB", "ADA", "TRX", "MATIC", "LINK", "DOT",
            "XLM", "XMR", "ATOM", "AAVE", "BONK", "DOGE", "SHIB", "DOT", "FET", "APT",
            "RNDR", "HBAR", "WIF", "INJ", "JUP"]

def beta_calculation(data_crypto_1, data_crypto_2, length):
    returns_crypto_1 = data_crypto_1['Close'].pct_change().dropna()
    returns_crypto_2 = data_crypto_2['Close'].pct_change().dropna()

    returns_crypto_1 = returns_crypto_1[-length:]
    returns_crypto_2 = returns_crypto_2[-length:]

    if len(returns_crypto_1) != len(returns_crypto_2):
        raise ValueError("The length of returns for both cryptocurrencies must match.")

    covariance = np.cov(returns_crypto_1, returns_crypto_2)[0, 1]
    variance = np.var(returns_crypto_2)

    beta = covariance / variance

    return beta

def download_data(ticker):
    data = yf.download(ticker+"-USD")
    df = pd.DataFrame(data)
    if 'time' in df.columns:
        df.rename(columns={'time': 'date'}, inplace=True)
        df['date'] = pd.to_datetime(df['date'], unit='s')
        df.set_index('date', inplace=True)
    df = df[['Close']]
    return df

def return_beta_values(calc_lengths, tickers):
    beta_tickers = ['BTC', 'ETH']
    all_averages = {ticker: [] for ticker in tickers}
    btc_beta_df, eth_beta_df, ranked_beta_df = None, None, None

    for beta_ticker in beta_tickers:
        print(f'Calculating betas against: {beta_ticker}')
        beta_results = {ticker: [] for ticker in tickers}

        try:
            data_beta_ticker = download_data(beta_ticker)
            if data_beta_ticker.empty:
                print(f"No data for {beta_ticker}")
                continue
        except Exception as e:
            print(f"Failed to download data for {beta_ticker}: {e}")
            continue

        for ticker in tickers:
            print(f'Processing ticker: {ticker}')
            try:
                data_ticker = download_data(ticker)
                if data_ticker.empty:
                    print(f"No data for {ticker}")
                    continue
            except Exception as e:
                print(f"Failed to download data for {ticker}: {e}")
                continue

            beta_values = []
            for length in calc_lengths:
                try:
                    beta = beta_calculation(data_ticker, data_beta_ticker, length)
                    beta_values.append(beta)
                except Exception as e:
                    print(f"Could not calculate beta for {ticker} against {beta_ticker} for length {length}: {e}")
                    beta_values.append(np.nan)

            average_beta = np.nanmean(beta_values)
            beta_values.append(average_beta)

            beta_results[ticker] = beta_values
            all_averages[ticker].append(average_beta)

        df = pd.DataFrame.from_dict(beta_results, orient='index',
                                    columns=[f'Length_{length}' for length in calc_lengths] + ['Average'])
        df.insert(0, 'Token', df.index)
        df.reset_index(drop=True, inplace=True)

        if beta_ticker == "BTC":
            btc_beta_df = df
        elif beta_ticker == "ETH":
            eth_beta_df = df

    final_averages = {ticker: np.nanmean(all_averages[ticker]) for ticker in tickers}
    final_df = pd.DataFrame(list(final_averages.items()), columns=['Token', 'Average_Beta'])
    final_df['Rank'] = final_df['Average_Beta'].rank(ascending=False)
    final_df.sort_values(by='Average_Beta', ascending=False, inplace=True)
    ranked_beta_df = final_df

    btc_zscore = return_z_scores_for_df(btc_beta_df.copy(), "Length")
    eth_zscore = return_z_scores_for_df(eth_beta_df.copy(), "Length")
    ranked_zscore = return_z_scores_for_df(ranked_beta_df.copy(), "Average_Beta")

    return btc_beta_df, eth_beta_df, ranked_beta_df, btc_zscore, eth_zscore, ranked_zscore


def return_z_scores_for_df(df, keyword):

    # Identify columns that contain 'Length' in their names
    keyword_columns = [col for col in df.columns if keyword in col]

    # Z-score normalize these columns
    df[keyword_columns] = (df[keyword_columns] - df[keyword_columns].mean()) / df[keyword_columns].std()

    if keyword is "Length":
        df['Average'] = df[keyword_columns].mean(axis=1)
        df.rename(columns={'Average': 'Average_Z-Score'}, inplace=True)

    if keyword is "Average_Beta":
        df['Average_Beta'] = df[keyword_columns].mean(axis=1)
        df.rename(columns={'Average_Beta': 'Average_Z-Score'}, inplace=True)

    return df
