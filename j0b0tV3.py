# j0b0t v3 TIE [Timing is Everything]
# Joseph Orlando
# JoeyOrlando.com
#
# Trades SPY and UPRO with leverage to try
# and meet or beat the market index.
# Timing is Everything, as trading mid-day
# brought highest returns (less loss due to
# volatility) in backtesting.
#
# Historical backtesting:  01/01/2010 -> 09/14/2016
# j0b0t v3 RETURN:         432.4%
# SPY Benchmark RETURN:    116.8%
# Initial Investment:      $1000.00

import talib

def maxPurchase(price, balance):
    if(price == 0 or balance == 0):
        return 0
    return int(balance/price)

def initialize(context):
    # SPY
    context.equity = sid(8554)
    # UPRO
    context.leveraged = sid(38533)
        
    schedule_function(startBot, date_rules.every_day(), time_rules.market_open(hours=3))  

# gentlemen, start your engines!
def startBot(context, data):
    
    # Track our position
    current_position = max(context.portfolio.positions[context.equity].amount, context.portfolio.positions[context.leveraged].amount)
    
    # Retrieve history for SPY
    high = data.history(context.equity, 'high', 40, '1d')
    low = data.history(context.equity, 'low', 40, '1d')
    close = data.history(context.equity, 'close', 40, '1d')
    prices = data.history(context.equity, 'price', 40, '1d')
    price = data.current(context.equity, 'price')
    
    # Set initial score for trading
    saleDecision = 0;

    # Retrieve MACD data
    macda, signal, hist = talib.MACD(prices, fastperiod=8,slowperiod=17,signalperiod=9)
    macd = macda[-1] - signal[-1]
    
    # Retrieve RSI
    rsi = talib.RSI(prices, timeperiod=14)[-1]
    
    # Retrieve STOCH data
    slowk, slowd = talib.STOCH(high,
                                   low,
                                   close,
                                   fastk_period=5,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
    
    
    # Begin trading logic
    if(current_position > 0):

        # we currently own some, we might look to sell
        if(macd < -0.3):
            # bad news bears! sell!
            saleDecision += (macd * 400)
            
        elif(macd < 0):
            # things are looking on the up, buy buy buy
            saleDecision += (abs(macd) * 1)
            
        else:
            # we might want to sell
            saleDecision += (macd * -1)
            
        if(rsi < 35):
            # too low!
            saleDecision += (rsi * -30)
        elif(rsi > 75):
            # too high!
            saleDecision += (rsi * -1)
        else:
            # just right :)
            saleDecision += (rsi * 2)
            
        if(slowk[-1] < 20 or slowd[-1] < 20):
            # we've hit our entry point
            saleDecision += (max(slowk[-1], slowd[-1]) * 5)
        elif(slowk[-1] > 75 or slowd[-1] > 75):
            # woah there, baby! we're not getting in at this price!
            saleDecision += (max(slowk[-1], slowd[-1]) * -2)
        else:
            # somewhere in the middle? I'll take it..
            saleDecision += (max(slowk[-1], slowd[-1])) 
    else:
        # we don't own any, we're looking to buy
        if(macd < -0.5):
            # things are looking on the up, buy buy buy
            saleDecision += (abs(macd) * 40)
            
            if(rsi < 35):
                # nice and low :)
                saleDecision += (rsi * 2)
            elif(rsi > 65):
                # too high!
                saleDecision += (rsi * -1)
    
            if(slowk[-1] < 20 or slowd[-1] < 20):
                # looks like this is our entry point, gents'
                saleDecision += (max(slowk[-1], slowd[-1]) * 5)
            elif(slowk[-1] > 75 or slowd[-1] > 75):
                # I'd rather not get in at this price...
                saleDecision += (max(slowk[-1], slowd[-1]) * -2)
            else:
                # somewhere in the middle? I'll take it..
                saleDecision += (max(slowk[-1], slowd[-1]))
        elif(macd < 0):
            # things are looking on the up, buy buy buy!
            saleDecision += (abs(macd) * 1)

            if(rsi < 35):
                saleDecision += (rsi * 2)
            elif(rsi > 65):
                saleDecision += (rsi * -1)
    
            if(slowk[-1] < 20 or slowd[-1] < 20):
                saleDecision += (max(slowk[-1], slowd[-1]) * 5)
            elif(slowk[-1] > 80 or slowd[-1] > 80):
                saleDecision += (max(slowk[-1], slowd[-1]) * -2)
            else:
                # somewhere in the middle
                saleDecision += (max(slowk[-1], slowd[-1]))
                
    # Let the data be known!            
    record(macd_val=macd)
    record(slowk_val=slowk[-1])
    record(slowd_val=slowd[-1])
    record(rsi_val=rsi)
    record(score=saleDecision)
    
    if(saleDecision > 50):     
        # Let the bulls run! Johnny! Go on and get me some of them
        # UPRO's so we can utilize their 3x leverage to optimize
        # our returns, there son! Huuuu-Weee!
        Uprice = data.current(context.leveraged, 'price')
        order(context.leveraged, maxPurchase(Uprice, context.portfolio.cash))
    elif(saleDecision > 0):
        # Whelp, she ain't pretty, but we never said this algorithm
        # was perfect.. Let's drop the leverage and stick to the good
        # ole' fashioned market indices.
        order(context.leveraged, 0)
        order(context.equity, maxPurchase(price, context.portfolio.cash))
    elif(saleDecision < 0):
        # Woah there buddy! You're goin' the wrong way!
        # I think it's just 'bout time to cut our losses,
        # what do you think?
        order(context.leveraged, 0)
        order(context.equity, 0)
