# Background

I wanted to experiment with ChatGPT on a small project to get a sense for how to boost my productivity by eliminating the mundane aspect of programming while helping me with things that I am a novice (pandas.DataFrame) or have only intermediate level experience (python).  It was an enjoyable experience and definitely helped me get to results quicker which is the rewarding part of programming.  The project I chose was something of which I have a great interest in - investing.  It is a simple tool which emulates the [Efficient Frontier](https://en.wikipedia.org/wiki/Efficient_frontier) functionality [here](https://www.portfoliovisualizer.com/efficient-frontier) from a site every investor should be aware of, Portfolio Visualizer.

# Tool Use

```
python3 optimize-portfolio.py --tickers VTI,VYM,VUG,BND --allocation 30,20,15,35 --start-date 2007-12-31 --end-date 2023-12-31
```

These are the tickers and allocations for a simple four fund portfolio consisting of 65% equities and 35% bonds.  Here is the tool's output for this portfolio:

```
Risk free rate = 0.91%

Provided portfolio return: 7.94%
Provided portfolio standard deviation: 11.02%
Provided portfolio sharpe ratio: 0.64

Optimal portfolio return: 6.70%
Optimal portfolio standard deviation: 8.43%
Optimal portfolio sharpe ratio: 0.69

     Annualized Return Standard Deviation Sharpe Ratio Optimal Allocation Provided Allocation
BND             2.79%              4.63%        0.405             58.53%              35.00%
VUG            12.61%             17.87%        0.655             36.85%              15.00%
VYM             9.27%             15.39%        0.543              4.62%              20.00%
VTI            10.73%             16.71%        0.588              0.00%              30.00%

Asset Correlations:
      BND   VTI   VUG   VYM
BND  1.00  0.26  0.32  0.22
VTI  0.26  1.00  0.96  0.93
VUG  0.32  0.96  1.00  0.81
VYM  0.22  0.93  0.81  1.00
```

You can experiment with the tool using ETFs and / or stocks to construct your own portfolio with the goal of maximizing the sharpe ratio.  This usually involves finding the right mix of assets with good returns and low correlations.

# TODOs

* The tool's output while very close to Portfolio Visualizer's output is not exactly the same.  Need to figure out what causes the discrepancy.

# Disclaimer

Don't do anything stupid with this tool.  Use your brain.
