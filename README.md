# Momentum Trading Algorithms

  These are two bots I made with the help of FreeCodeCamp. They aren't meant for actual trading and likely won't net an average return greater than the market average (if even that). This was just a test for me to learn the logistics of calling APIs specifically for stocks as well as working with dataframes and exporting to excel. I plan to link these to mock stock trading portfolios just to see how they perform as an experiement later down the line. 

  The base bot just uses One Year Return and ranks SP500 stocks based off that while the high quality bot sorts the stocks based off a score. This score is calculated by  getting an aggregate of their percentiles in four categories: 1 month returns, 3 month returns, 6 month returns and 1 year returns. They are ranked then based on an aggregate of this percentile score and the top 50 are picked to be bought with priority being given to the top-most stocks.
