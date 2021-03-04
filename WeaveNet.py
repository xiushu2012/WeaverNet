# -*- coding: utf-8 -*-

import akshare as ak
import numpy as np  
import pandas as pd  
import math
import datetime
import os
import matplotlib.pyplot as plt
import openpyxl

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',1000)





def get_akshare_comparison(xlsfile):

	shname='compare'
	isExist = os.path.exists(xlsfile)
	if not isExist:
		bond_cov_comparison_df = ak.bond_cov_comparison()
		bond_cov_comparison_df.to_excel(xlsfile,sheet_name=shname)
		print("xfsfile:%s create" % (xlsfile))  
	else:
		print("xfsfile:%s exist" % (xlsfile))
		

	#print(bond_cov_comparison_df)
	return xlsfile,shname

def calc_value_center():
	stock_premium = [0.81,0,-0.1,-5.56,-3,8.34,0.28,-5.2,-8.24,2.34,-7.3,-26.52,-0.29]
	debt_premium =  [-2.79,0.79,2.09,2.58,2.89,4.63,5.18,7.33,7.4,7.44,7.46,9.23,9.52]
	return np.mean(stock_premium),np.mean(debt_premium)



def calc_value_center_unlist(unlistpd):
	stock_premium =  unlistpd['转股溢价率']
	debt_premium = 	 unlistpd['纯债溢价率']
	return np.mean(stock_premium), np.mean(debt_premium)

def calc_value_distance(a, b,va,vb):
	return math.sqrt((a-va)**2+(b-vb)**2)



def get_pass_days(date):
	if date == '-':
		return -99
	else:
		delt = datetime.datetime.now() - datetime.datetime.strptime(date, '%Y%m%d')
		return delt.days
def calc_expect_bond_price(zp,vb):
    return ((100+vb)/100)*zp

def calc_expect_bond_overflow(cp,ep):
    if cp == '-':
        return 100*(ep-100)/100
    else:
        return 100*(ep-cp)/cp

def calc_expect_stock_overflow(zp,sp,va):
    if zp == '-':
        return 100*((100/(100+va))*100/sp -1)
    else:
        return 100*((100/(100+va))*zp/sp -1)

#bond_cov_comparison_df = pd.read_excel('compare-.xls', 'compare')['最新价'].str.replace('-','')
#bond_expect_df = bond_cov_comparison_df['转股溢价率'].map(lambda x:-x)
#new_price_select = bond_cov_comparison_df[bond_cov_comparison_df['最新价'].astype(float) < 120.0]



if __name__=='__main__':

    from sys import argv
    tnow = ""
    if len(argv) > 1:
        if argv[1] == '*':
            tnow = datetime.datetime.now()
        else:
            tnow = datetime.datetime.strptime(argv[1], '%Y/%m/%d')
    else:
        print("please run like 'python WeaveNet.py [*|2020/07/07]'")
        exit(1)

    print("time is :" + tnow.strftime('%Y%m%d'))

    filefolder = r'./data/' + tnow.strftime('%Y%m%d')
    filein = tnow.strftime('%Y_%m_%d') + '_in.xls'
    getakpath =  "%s/%s" % (filefolder,filein)

    isExist = os.path.exists(filefolder)
    if not isExist:
        os.makedirs(filefolder)
        print("AkShareFile:%s create" % (filefolder))
    else:
        print("AkShareFile:%s exist" % (filefolder))

    resultpath,insheetname = get_akshare_comparison(getakpath)
    print("data of path:" + resultpath + "sheetname:" +insheetname)



    bond_unlisted_df = pd.read_excel(resultpath, insheetname,converters={'正股代码':str})[['转债名称','正股代码','转股溢价率','纯债溢价率','申购日期','上市日期']]
    bond_unlisted_df = bond_unlisted_df[bond_unlisted_df['上市日期'] == '-']
    bond_unlisted_df = bond_unlisted_df[bond_unlisted_df['正股代码'] != '-']


    #va,vb = calc_value_center_unlist(bond_unlisted_df)
    va,vb = calc_value_center()
    print("the average of unlisted bond 转股溢价率,纯债溢价率",va,vb)


    bond_cov_comparison_df = pd.read_excel(resultpath, insheetname,converters={'正股代码':str,'上市日期':str})[['最新价','转债名称','正股代码','转股价值','纯债价值','转股溢价率','纯债溢价率','上市日期']]
    bond_cov_comparison_df = bond_cov_comparison_df[bond_cov_comparison_df['正股代码'] != '-']

    bond_cov_comparison_df['估值距离'] = bond_cov_comparison_df.apply(lambda row: calc_value_distance(row['转股溢价率'], row['纯债溢价率'],va,vb), axis=1)
    bond_cov_comparison_df['交易天数'] = bond_cov_comparison_df.apply(lambda row: get_pass_days(row['上市日期']), axis=1)
    bond_cov_comparison_df['预期转债价格'] = bond_cov_comparison_df.apply(lambda row: calc_expect_bond_price(row['纯债价值'],vb), axis=1)
    bond_cov_comparison_df['预期转债增长'] = bond_cov_comparison_df.apply(lambda row: calc_expect_bond_overflow(row['最新价'],row['预期转债价格']), axis=1)
    bond_cov_comparison_df['预期转股增长'] = bond_cov_comparison_df.apply(lambda row: calc_expect_stock_overflow(row['预期转债价格'],row['转股价值'],va), axis=1)
    #bond_expect_sort_df = bond_cov_comparison_df.sort_values('交易天数',ascending=True)

    bond_expect_sort_df = bond_cov_comparison_df.sort_values('估值距离',ascending=True)
    bond_expect_startup_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^3.*?')]
    bond_expect_smallboard_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^0.*?')]
    bond_expect_bigboard_df = bond_expect_sort_df[bond_expect_sort_df['正股代码'].str.contains(r'^6.*?')]

    fileout = tnow.strftime('%Y_%m_%d') + '_out.xls'
    outanalypath =  "%s/%s" % (filefolder,fileout)
    writer = pd.ExcelWriter(outanalypath)
    bond_unlisted_df.to_excel(writer, 'unlist')
    bond_expect_sort_df.to_excel(writer,'analyze')
    bond_expect_startup_df.to_excel(writer,'startup')
    bond_expect_smallboard_df.to_excel(writer,'smallboard')
    bond_expect_bigboard_df.to_excel(writer,'bigboard')
    writer.save()
    print("value distance of  'unlist and analye' :" + fileout)


    #print(bond_expect_sort_df)
    # 显示散点图
    #bond_expect_sort_df.plot.scatter(x='纯债溢价率', y='转股溢价率')
    X = bond_expect_sort_df.values
    #plt.plot(X[:,6], X[:,5],"ro")
    txt = X[:,1].reshape(1, -1)[0]
    x = X[:,6].reshape(1, -1)[0]
    y = X[:,5].reshape(1, -1)[0]
    plt.scatter(x,y)
    for i in range(len(txt)):
        plt.annotate(txt[i][0:2], xy = (x[i],y[i]), xytext = (x[i]+0.1, y[i]+0.1)) #这里xy是需要标记的坐标，xytext是对应的标签坐标


    # 显示图
    plt.xlabel('纯债溢价率')
    plt.ylabel('转股溢价率')
    plt.rcParams['font.sans-serif']=['SimHei']

    fileimage = tnow.strftime('%Y_%m_%d') + '_image.png'
    imagepath =  "%s/%s" % (filefolder,fileimage)
    plt.savefig(imagepath)
    print("value image of  path:" + imagepath )
    #plt.show()




#对pandas中的Series和Dataframe进行排序，主要使用sort_values()和sort_index()。
#DataFrame.sort_values(by, axis=0, ascending=True, inplace=False, kind=‘quicksort’, na_position=‘last’)
#by：列名，按照某列排序
#axis：按照index排序还是按照column排序
#ascending：是否升序排列
#kind：选择 排序算法{‘quicksort’, ‘mergesort’, ‘heapsort’}, 默认是‘quicksort’，也就是快排
#na_position：nan排列的位置，是前还是后{‘first’, ‘last’}, 默认是‘last’
#sort_index() 的参数和上面差不多。





