import argparse
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

def get_risk_free_rate(start_date, end_date):

    # Calculate the risk free rate from the 90-day Treasury Bill
    tbill_data = yf.download('^IRX', start=start_date, end=end_date, progress=False)['Adj Close']
    monthly_tbill_data = tbill_data.resample('M').ffill()
    risk_free_rate = monthly_tbill_data.mean()
    print(f'Risk free rate = {risk_free_rate:.2f}%')
    return risk_free_rate / 100

def display_portfolio_stats(portfolio, portfolio_label, monthly_returns, risk_free_rate):

    allocation_column = f'{portfolio_label} Allocation'
    if allocation_column not in portfolio.columns:
        return
    weights = portfolio[allocation_column]

    portfolio_return = np.sum(portfolio['Annualized Return'] * weights)
    print(f'\n{portfolio_label} portfolio return: {portfolio_return * 100:.2f}%')

    portfolio_standard_deviation = np.sqrt(np.dot(weights.T, np.dot(monthly_returns.cov(), weights))) * np.sqrt(12)
    print(f'{portfolio_label} portfolio standard deviation: {portfolio_standard_deviation * 100:.2f}%')

    portfolio_sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_standard_deviation
    print(f'{portfolio_label} portfolio sharpe ratio: {portfolio_sharpe_ratio:.2f}')

def display_portfolio(portfolio, monthly_returns, risk_free_rate):

    display_portfolio_stats(portfolio, 'Provided', monthly_returns, risk_free_rate)
    display_portfolio_stats(portfolio, 'Optimal', monthly_returns, risk_free_rate)

    portfolio = portfolio.sort_values(by='Optimal Allocation', ascending=False)
    portfolio['Annualized Return'] = portfolio['Annualized Return'].map(lambda x: '{:.2%}'.format(x))
    portfolio['Standard Deviation'] = portfolio['Standard Deviation'].map(lambda x: '{:.2%}'.format(x))
    portfolio['Sharpe Ratio'] = portfolio['Sharpe Ratio'].map(lambda x: '{:.3f}'.format(x))
    portfolio['Optimal Allocation'] = portfolio['Optimal Allocation'].map(lambda x: '{:.2%}'.format(x))
    if 'Provided Allocation' in portfolio.columns:
        portfolio['Provided Allocation'] = portfolio['Provided Allocation'].map(lambda x: '{:.2%}'.format(x))
    print('\n', portfolio)

    print('\nAsset Correlations:')
    print(monthly_returns.corr().round(2))

def optimize_portfolio(start_date, end_date, tickers, allocation):

    risk_free_rate = get_risk_free_rate(start_date, end_date)

    # Retain only the adjusted closing price
    stock_data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']

    # Resample daily stock prices to monthly frequency
    monthly_stock_data = stock_data.resample('M').ffill()

    # Calculate monthly returns for each ticker
    monthly_returns = monthly_stock_data.pct_change().dropna()

    # Calculate standard deviation and Sharpe ratio using monthly returns
    annualized_return = monthly_returns.mean() * 12
    standard_deviation = monthly_returns.std() * np.sqrt(12)
    sharpe_ratio = (annualized_return - risk_free_rate) / standard_deviation

    # Maximize the sharpe ratio (by minimizing the negative of the sharpe ratio)
    def negative_sharpe(weights):
        portfolio_return = np.sum(annualized_return * weights)
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(monthly_returns.cov(), weights))) * np.sqrt(12)
        sharpe = (portfolio_return - risk_free_rate) / portfolio_std_dev
        return -sharpe

    # Initial guess for weights
    initial_weights = [1 / len(tickers) for _ in range(len(tickers))]

    # Set bounds for the optimization - weights between 0 and 1
    bounds = tuple((0, 1) for _ in range(len(tickers)))

    # Set constraints for the optimization - weights sum to 1
    constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})

    # Perform the optimization
    optimal_weights = minimize(negative_sharpe, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    portfolio = pd.DataFrame({
        'Annualized Return': annualized_return,
        'Standard Deviation': standard_deviation,
        'Sharpe Ratio': sharpe_ratio,
        'Optimal Allocation': optimal_weights['x']
    })

    if allocation is not None:
        provided_allocation = pd.DataFrame({
            'Tickers': tickers,
            'Provided Allocation': allocation
        })
        provided_allocation.set_index('Tickers', inplace=True)
        portfolio = portfolio.merge(provided_allocation, left_index=True, right_index=True)

    display_portfolio(portfolio, monthly_returns, risk_free_rate)

def main():

    parser = argparse.ArgumentParser(description='Optimize portfolio allocations')

    parser.add_argument('--start-date', type=str, required=True, help='Start date')
    parser.add_argument('--end-date', type=str, required=True, help='End date')
    parser.add_argument('--tickers', type=str, required=True, help='Comma delimited list of stock and ETF ticker symbols')
    parser.add_argument('--allocation', type=str, help='Comma delimited list of allocations for each ticker (Example: 50, 25, 25)')

    args = parser.parse_args()

    tickers = args.tickers.split(',')
    if args.allocation is not None:
        allocation = args.allocation.split(',')
        allocation = [float(value) for value in allocation]
        allocation_sum = sum(allocation)
        if allocation_sum != 100.0:
            print(f'Allocations ({allocation_sum}%) must sum to 100%')
            return
        allocation = [value / 100 for value in allocation]
    else:
        allocation = None

    optimize_portfolio(args.start_date, args.end_date, tickers, allocation)

if __name__ == "__main__":
    main()
