# Momentum Trading Programs

  This is part of a work in progresss project where I learn various quant concepts and try to implement them in programs. Note that the code won't run without an API key.
  
  These are programs I made with the help of FreeCodeCamp.org and then added to myself. They aren't meant for actual trading (obviously) and likely won't net an average return greater than the market average (if even that). This was just a test for me to learn the logistics of calling APIs specifically for stocks as well as working with dataframes and exporting to excel. I plan to link these to mock stock trading portfolios just to see how they perform as an experiement later down the line. 

  The base bot just uses One Year Return and ranks SP500 stocks based off that while the high quality bot sorts the stocks based off a score. This score is calculated by  getting an aggregate of their percentiles in four categories: 1 month returns, 3 month returns, 6 month returns and 1 year returns. They are ranked then based on an aggregate of this percentile score + how high/low the RSI is and the top 50 are picked to be bought with priority being given to the top-most stocks. I did the RSI function almost fully by myself save from a few wiki pages on the forumla though I am aware i can use pandas_ta to do it effortlessly.
  
  I've also made a MACD plotter to get the hang of plotting graphs using yahoo finance data and plotly.
