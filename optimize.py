import numpy
from numpy import *
import math
import operator
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import csv

tickers = ["KO", "SLB", "KR", "JNJ", "MRK", "DIS", "MCD", "AXP"]    # Fill in with Tickers of Stocks in Data File

periods_held = 36.0                                                   # Numer of Periods the securities are held for

monthly_return = .019634                                            # Expected Monthly Return

number_of_stocks = 8                                                # Number of Stocks in Data Set

sd = 0


def covariance(x, y):
    b, c, v = [], [], []

    mean_x = numpy.mean(x)
    mean_y = numpy.mean(y)
    length = len(x)
    i = 0

    while i < length:
        addx = pow(x[i] - mean_x, 2)
        addy = pow(y[i] - mean_y, 2)
        numer = (x[i] - mean_x) * (y[i] - mean_y)
        b.append(addx)
        c.append(addy)
        v.append(numer)
        i += 1
    coefficient = sum(v) / (math.sqrt(sum(b) * sum(c)))
    var_x = (sum(b) / (length - 1))
    var_y = (sum(c) / (length - 1))
    std_dev_x = math.sqrt(var_x)
    std_dev_y = math.sqrt(var_y)

    the_cov = (std_dev_x * std_dev_y) * coefficient

    return the_cov


def variance(x):
    b = []

    mean_x = numpy.mean(x)
    length = len(x)
    i = 0

    while i < length:
        add = pow(x[i] - mean_x, 2)
        b.append(add)
        i += 1
    vari = (sum(b) / (length - 1))

    return vari


def calculate():
    expected_return = monthly_return
    q = number_of_stocks + 2
    i = 0

    stocks = numpy.loadtxt('data.csv', delimiter=None, unpack=True)
    arr = stocks

    c = 0
    returns = numpy.zeros(number_of_stocks)         # returns of stock
    to = []
    num = []
    exponent = 1.0 / periods_held
    while c < len(returns):
        while i < periods_held:
            add_it = 1 + arr[c][i]
            to.append(add_it)
            i += 1
        xyz = reduce(operator.mul, to, 1)
        geo = ((xyz ** exponent) - 1)
        num.append(geo)
        to = []
        c += 1
        i = 0

    low = min(float(i) for i in num)
    high = max(float(i) for i in num)

    m = numpy.zeros((number_of_stocks, number_of_stocks))

    row = 0
    col = 0

    while row < number_of_stocks:
        while col < number_of_stocks:
            if col == row:
                the_var = variance(arr[col])
                m[row][col] = the_var
                col += 1
            else:
                the_cov = covariance(arr[row], arr[col])
                m[row][col] = the_cov
                col += 1

        row += 1
        col = 0

    solve(m, number_of_stocks, num, expected_return)

    frontier(m, number_of_stocks, num, high, low, monthly_return, sd)


def frontier(M, n, R, h, l, mr, s):
    inc = .0001
    while l <= h:
        def simplex_constraint(x):
            return x.sum() - 1

        def dot_constraint(x):
            return x.dot(R) - l

        def objective(x):
            return x.dot(M).dot(x)

        x0 = numpy.ones(n) / n
        bounds = [(0, numpy.inf)]*n
        constraints = (
            dict(type='eq', fun=simplex_constraint),
            dict(type='eq', fun=dot_constraint))
        V = minimize(
            objective, x0, method='SLSQP', tol=1e-8,
            bounds=bounds, constraints=constraints)

        stddev = (V.fun**.5)*100
        plt.scatter(stddev, (l*100), s=2)
        l += inc

    plt.ylabel('Expected Return')
    plt.xlabel('Std Deviation (Risk)')
    plt.title('Efficient Frontier')
    plt.plot(s, (mr*100), "rD", color="BLUE")
    plt.show()


def solve(M, n, R, E):
    def simplex_constraint(x):
        return x.sum() - 1

    def dot_constraint(x):
        return x.dot(R) - E

    def objective(x):
        return x.dot(M).dot(x)

    x0 = numpy.ones(n) / n
    bounds = [(0, numpy.inf)]*n
    constraints = (
            dict(type='eq', fun=simplex_constraint),
            dict(type='eq', fun=dot_constraint))
    V = minimize(
            objective, x0, method='SLSQP', tol=1e-8,
            bounds=bounds, constraints=constraints)

    stddev = (V.fun**.5)*100
    global sd
    sd = stddev
    annualized_return = ((1 + monthly_return) ** 12) - 1

    print("")
    print("Annualized Return:", round(annualized_return*100, 4))
    print("Monthly Return:", round(monthly_return*100, 4))
    print("Portfolio Variance:", round(V.fun, 4))
    print("Portfolio Standard Deviation:", round(stddev, 4))
    print("")
    print("Portfolio Allocations:")

    i = 0
    while i < n:
        share = V.x[i] * 100

        if share > 1.0e-10 and share > 0.01:
            print(tickers[i], "%.2f" % round(share, 2))
        i += 1


calculate()