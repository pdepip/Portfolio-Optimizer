import urllib2
import csv
import stockquote


def main():

    tickers = ["KO", "SLB", "KR", "JNJ", "MRK", "DIS", "MCD", "AXP"]

    user_start = '2011-01-31' # One Month before desired start date
    user_end = '2013-12-31'
    file_name = 'data.csv'

    ###Switches start date to prior month to get return for

    begin_year = int(user_start.split("-",2)[0])
    begin_month = int(user_start.split("-",2)[1])
    begin_day = int(user_start.split("-",2)[2])

    if begin_month == 1:
        begin_year -= 1
        begin_month = 12
    else:
        begin_month -= 1


    user_start = "-".join((str(begin_year), str(begin_month), str(begin_day)))

    ###

    '''
    user_input = raw_input("Enter Your Stock Tickers (Separate with Comma, no spaces):")
    user_start = raw_input("Enter your Start Date (i.e. 2011-01-31):")
    user_end = raw_input("Enter your End Date (i.e. 2013-12-31):")
    tickers = user_input.split(',')
    '''

    n = len(tickers)

    adj_close = []


    i = 0

    depths = [[] for i in range(n)]

    i = 0
    for x in tickers:
        try:
            print("Getting Data For: ", x)
            data = stockquote.get_historical_prices(x, user_start, user_end)
            key = data.keys()
            key.sort()

            for day in key:
                adj_close.append(data[day]['Adj Close'])
            returns = convert(adj_close)
            depths[i] = returns
            adj_close = []

        except urllib2.HTTPError, err:
            print(err.code, "Error: Incorrect Date or Ticker Given", x)

        i += 1

    print("Writing to Data File:", file_name)

    with open(file_name, "w") as file:
        writer = csv.writer(file, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in zip(*depths):
            writer.writerow(row)


def convert(x):

    print("Converting to Return")
    ret = []
    n = len(x)

    idx = 0

    for s in x:
        idx = (idx + 1) % len(x)
        next_elem = x[idx]
        new = next_elem
        old = s
        to_add = (float(new) - float(old)) / float(old)
        ret.append(round(to_add, 6))
    return ret

main()
