# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 15:35:08 2019

@author: 吴嫒博
"""


import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
from collections import Counter
#加载画图包
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib

#导入统计、聚类包
from statsmodels.stats.anova import anova_lm
from sklearn.cluster import KMeans
from scipy.stats import pearsonr
from scipy.stats import spearmanr

from statsmodels.formula.api import ols
from scipy import stats


# %matplotlib inline
# %config InlineBackend.figure_format='retina' #⽤用来提升Retina屏幕图像的分辨率
#中文显示
plt.rcParams['font.family'] = ['Arial Unicode MS']

#去掉告警信息
import warnings
warnings.filterwarnings("ignore")

#from prettytable import PrettyTable#需要安装 prettytable，安装后，可以让打印输出的表格更好看


class DescriptiveStatistics(object):
    def __init__(self,file_path):
        self.file_path = file_path
        
        
    def load_data(self,file_path,sep = '\t',fill_null = 1):
        df = pd.read_table(self.file_path,sep=sep)
    
        row_number = df.shape[0]
        column_number = df.shape[1]
        print('-'*50) 
        print()
        print('数据有 %d 行， %d 列' % (row_number,column_number))
        print('\n')
        print('前6行数据如下：\n')
        print(df.head())
        print('\n')
        print('-'*50) 
        print()
        print('每一列的类型如下：\n')
        print(df.info())
        ##缺失值处理
        null_num = df.isnull().sum()
        
        s1 = null_num[null_num>0]
        null_columns = null_num[null_num>0].index
        s2 = null_num[null_num>row_number*0.1]
        
        print()
        print('-'*50) 
        print()
        if s2.empty:
            if s1.empty: print()
            else:
                print('含缺失值的列，缺失值个数在总行数的10%以内\n')   
        else:
            print('特别注意，以下几列，缺失值个数超过总行数10%，请自行判断填充后的结果是否合理：\n')
            print(null_num[null_num>row_number*0.1].index) 
            print('\n')
        
        
        
        if s1.empty:
            print('数据无缺失值')
            return df
            
        else:
            print()
            print('-'*50) 
            print()
    
            print('有缺失值的列及缺失值个数：\n')
            print(null_num[null_num>0])
            
            #缺失值处理
            
            print()
            print('-'*50) 
            print()
    
            
            if fill_null==1:
                print('\n缺失值处理：向后填充\n')
                df[null_columns] = df[null_columns].fillna(method='bfill')
    
                #查看是否仍然有缺失值，如果有，再向前填充一下
                null_num2 = df.isnull().sum()
    
                s3 = null_num2[null_num2>0]
                null_columns2 = null_num2[null_num2>0].index
                if s3.empty: 
                    print('')
                else:
                    df[null_columns2] = df[null_columns2].fillna(method='ffill')
    
    
                null_num3 = df.isnull().sum()    
                s4 = null_num3[null_num3>0]
                if s4.empty:
                    print('填充处理后，无缺失值\n')
                else:
                    print('仍有缺失值，需手动处理\n')
                
                return df
            else :
                return df
            
            
    def data_detail_1_Category(self,df,Category_variable_name):
        #列出每个类别的个数
        #value_counts 其实对分类变量、数值变量都可以用。但仅对分类变量有意义
        
        a = pd.DataFrame(df[Category_variable_name].value_counts())
        #计算总体百分比
        b = pd.DataFrame(df[Category_variable_name].value_counts()).apply(lambda x : x/sum(x)).round(3)
        
        c = pd.merge(a,b,left_index=True,right_index=True)
        
        #重命名
        c.columns = ['计数','总体百分比']
        print('-'*100)
        print()
        print('分类变量，每个类别数据量分布：')
        print()
        print(c)
        print()
        print('-'*100)
        
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = [u'SimHei']  #FangSong/黑体 FangSong/楷体
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        fig = plt.gcf()
        
        title_1 = Category_variable_name + ' 不同类别分布---条形图'
        title_2 = Category_variable_name + ' 不同类别占比---扇形图'
        
        
        fig.set_size_inches(16,6)
        
        # 分成2x2，占用第一个，即第一行第一列的子图 
        plt.subplot(121)
        
        sns.countplot(data=df,x=Category_variable_name)
        plt.title(title_1)
        # 分成2x2，占用第二个，即第一行第二列的子图 
        plt.subplot(122)
        #扇形图
        freq = pd.DataFrame(df[Category_variable_name].value_counts())
        plt.pie(x=freq,  #要统计的数据
                labels = freq.index, #分类标签名称
                startangle=90, #起始角度，90度
                autopct='%1.f%%' #添加占比，设置文本格式
               )
        plt.title(title_2)
        plt.show()
            
    def detect_outliers(self, df, features):
        outlier_indices = []
    
        for col in features:
            Q1 = np.percentile(df[col], 25)
            Q3 = np.percentile(df[col], 75)    
            IQR = Q3 - Q1    
            outlier_step = 1.5 * IQR    
            outlier_list_col = df[(df[col] < Q1 - outlier_step) | (df[col] > Q3 + outlier_step)].index    
            outlier_indices.extend(outlier_list_col)    
        outlier_indices = Counter(outlier_indices)        
        multiple_outliers = list( k for k, v in outlier_indices.items() )    
        return multiple_outliers
  

    #绘图
    def plot_data_1_Numeric(self,df,column_name):
        fig = plt.gcf()
        
        title_1 = column_name + ' --直方图'
        title_2 = column_name + ' -核密度图(KDE)'
        title_3 = column_name + ' -箱线图'
        
        
        fig.set_size_inches(16,4)
        
        # 分成3x1，占用第一个，即第一行第一列的子图 
        plt.subplot(131)
        
        df[column_name].hist()
        plt.title(title_1)
        # 分成3x1，占用第二个，即第一行第二列的子图 
        plt.subplot(132)
        #扇形图
        sns.kdeplot(df[column_name].values)
        plt.title(title_2)
        # 分成3x1，占用第3个，即第一行第二列的子图 
        plt.subplot(133)
        sns.boxplot(data=df,x=column_name)
        plt.title(title_3)
        plt.show() 
    
    
    #封装好的结果
    def data_detail_1_Numeric(self,df,Numeric_variable_name):
        #列出每个类别的个数
        #value_counts 其实对分类变量、数值变量都可以用。但仅对分类变量有意义
        
        #调用异常值处理函数
        Outliers_to_drop = self.detect_outliers(df, [Numeric_variable_name])
        df_new = df.drop(Outliers_to_drop, axis=0).reset_index(drop=True)
        
        
        print('-'*100)
    #     print('------------------------------------------------------------------------------------------------------') 
        print('%s 的基础统计量：' %(Numeric_variable_name))    
        print()
        print(df[Numeric_variable_name].describe())
        
        
        if not Outliers_to_drop:
            print()
            print('-'*100)
    #         print('------------------------------------------------------------------------------------------------------') 
            print()
            print('数据没有异常值（箱线图识别法）')
            print()
            print('-'*100)
    #         print('------------------------------------------------------------------------------------------------------') 
            print()
            print('数据分布图像：')
            print()
            self.plot_data_1_Numeric(df,Numeric_variable_name)
    
    
            print()
        else:
            
            print()
            print('-'*100)
    #         print('------------------------------------------------------------------------------------------------------') 
            print('没有做异常值处理的分布图像：')
            print()
            self.plot_data_1_Numeric(df,Numeric_variable_name)
            print()
            print('-'*100)
    #         print('------------------------------------------------------------------------------------------------------') 
            print('用箱线图做完异常值处理（丢弃）后的分布图像：')
            print()
            ##################################
            #做完异常值处理，绘图
    
            print()
            self.plot_data_1_Numeric(df_new,Numeric_variable_name)
            plt.show()           
            

    #关联性分析

    def chisquare_test(self,df,column_name1,column_name2):

        df['test_index'] = 1
        df_new = df[['test_index',column_name1,column_name2]].groupby([column_name1,column_name2]).count()
        print('------------------------------------------------------------------------------------------------------')
        print('%s 和 %s 卡方检验： ' % (column_name1,column_name2))

        from scipy import stats

        #卡方检验
        # test = stats.chisquare(df_new)

        #p值在显著性水平0.05下小于0.05

        p = stats.chisquare(df_new)[1]
        print('P值为：%d\n' % p)
        p = float(p)
        if p > 0.05:
                print('不拒绝原假设,无充分证据表明两个因素之间存在关系')
        else:
            if p < 0.05:
                print('显著性水平α=0.05下,拒绝原假设,充分相关,建议作图分析做进一步判断到底是因子里面哪个因素起作用')
            elif p < 0.01:
                print('显著性水平α=0.01下,拒绝原假设,显著相关,建议作图详细分析')

    #分类变量X分类变量

    def Category_vs_Category(self,df, Category_variable_1,Category_variable_2,is_test=1):
        df['test_index'] = 1
        s =  df.pivot_table(df[['test_index']],index=Category_variable_1,columns=Category_variable_2,
                       aggfunc=[len])

        s_rate =  df.pivot_table(df[['test_index']],index=Category_variable_1,columns=Category_variable_2,
                       aggfunc=[len])/df['test_index'].count()
        print('------------------------------------------------------------------------------------------------------')
        print('%s 和 %s 类别分布： ' % (Category_variable_1,Category_variable_2))
        print()
        print(s)

        print()
        print('------------------------------------------------------------------------------------------------------')
        print()
        fig = plt.gcf()
        fig.set_size_inches(8,6)
        sns.heatmap(s_rate.round(2),
                annot=True,#设置显示数据标签
                fmt='.2f' #数字格式控制
                #,mask=x.values<200 , #把小于200的区域覆盖掉
                ,cmap='Blues' #设定颜色
               )
        plt.title('%s 和 %s 类别分布热力图' % (Category_variable_1,Category_variable_2))
        plt.show()
        print()

        if is_test!=1:
            return 0
        else :self.chisquare_test(df, Category_variable_1,Category_variable_2)

#连续变量
    def Category_vs_Numeric(self,df,Category_variable,Numeric_variable,is_outliers=1):    
        if is_outliers==1:    
            Outliers_to_drop = self.detect_outliers(df, [Numeric_variable])
            df_new = df.drop(Outliers_to_drop, axis=0).reset_index(drop=True)
        else:
            df_new=df

        count =pd.DataFrame(df_new[[Numeric_variable,Category_variable]].groupby([Category_variable]).count())
        mean =pd.DataFrame(df_new[[Numeric_variable,Category_variable]].groupby([Category_variable]).mean().round(2))
        std = pd.DataFrame(df_new[[Numeric_variable,Category_variable]].groupby([Category_variable]).std().round(2))


        agg_result = pd.merge(mean,std,left_index=True,right_index=True)
        agg_result_2 = pd.merge(count,agg_result,left_index=True,right_index=True)
        #重命名
        agg_result_2.columns = ['计数','均值','标准差']

        print('------------------------------------------------------------------------------------------------------') 
        print('不同 %s 类别下 %s 的均值、标准差： ' % (Category_variable,Numeric_variable))
        print()
        print(agg_result_2)
        print()

        print('------------------------------------------------------------------------------------------------------') 
        print()
        fig = plt.gcf()   
        fig.set_size_inches(16,4)

        # 分成2x2，占用第一个，即第一行第一列的子图 
        plt.subplot(131)

        #按照x分组后，按estimator统计，以结果作为条形图的高度
        sns.barplot(data=df, 
                    x=Category_variable, #按x分组
                    y=Numeric_variable #对y做统计
                    #estimator=np.mean #支持多种统计量，默认为均值
                   )
        plt.title('不同%s类别下%s的均值 ' % (Category_variable,Numeric_variable))
        # 分成2x2，占用第二个，即第一行第二列的子图 
        plt.subplot(132)
        #扇形图

        category = df_new[Category_variable].values

        print(set(category))
        for i in set(category):
            temp_df = df_new.loc[category ==i]
            sns.kdeplot(temp_df[Numeric_variable],label=i
                       )
        plt.title('不同%s类别下%s的kde图 ' % (Category_variable,Numeric_variable))

        plt.subplot(133)
        #扇形图

        category = df_new[Category_variable].values

        print(set(category))
        sns.violinplot(data=df, 
                    x=Category_variable, #按x分组
                    y=Numeric_variable #对y做统计
                    #estimator=np.mean #支持多种统计量，默认为均值
                   )
        plt.title('不同%s类别下%s的violinplot图 ' % (Category_variable,Numeric_variable))

        plt.show()
        print()
        print('------------------------------------------------------------------------------------------------------') 
        print()

        category = df[Category_variable].values


        #######正态性检验
        if len(np.unique(category))==2:
            print('两个类别变量，T检验')

            s=[]
            for i in np.unique(category):
                temp_df = df.loc[category ==i]
                a = temp_df[Numeric_variable]

                normed_a = (a-a.mean())/a.std()                
                #
                statistic, pvalue=stats.kstest(normed_a, 'norm')
                s.append(a)

            #用ttest_ind做T检验，要求输入原始样本数据
            t_stats, p_value = stats.ttest_ind(*s)

            print("P value is %.10f" %(p_value)) # 双边检验

            if p_value>0.05:
                print('%s 与%s  T检验： 没有显著差异' %(Category_variable,Numeric_variable))
            else:
                print('%s 与%s  T检验： 有显著差异' %(Category_variable,Numeric_variable))

        else:
            print('多类别变量，方差分析：')
            num =0
            s=[]
            for i in np.unique(category):
                temp_df = df.loc[category ==i]
                a = temp_df[Numeric_variable]

                normed_a = (a-a.mean())/a.std()                
                #
                statistic, pvalue=stats.kstest(normed_a, 'norm')
                s.append(a)
                 # p值>0.05,可以认为服从正态分布

                if pvalue<=0.05:
                    print('%s 为 %s 时，%s 正态性检验： 不服从正太分布' %(Category_variable,i,Numeric_variable))
                    print(stats.kstest(normed_a, 'norm'))
                    print('\n')
                    break
                else:
                    print('%s 为 %s 时，%s 正态性检验： 服从正太分布' %(Category_variable,i,Numeric_variable))
                    print(stats.kstest(normed_a, 'norm'))

            num=num+1
            if num>=len(np.unique(category)):
                print(stats.levene(*s))

                levene_test, pvalue=stats.levene(*s)

                if pvalue<=0.05:
                    print('%s 与%s 莱文检验： 不满足方差相等条件' %(Category_variable,Numeric_variable))
                    exit
                else:
                    print('%s 与%s 莱文检验： 满足方差相等条件,可以进行方差分析' %(Category_variable,Numeric_variable))


            #单因素方差分析



                #不同社区（Neighborhood)
                #formula = 'Avg_price~Neighborhood'
                formula = Numeric_variable + '~' + Category_variable
                print(formula)
                anova_results = anova_lm(ols(formula,df_new).fit())
                print(anova_results)
                #P值小于0.05，可以拒绝不同社区对房价没有影响的假设,可以认为社区对售价有显著影响
  

            
    def Numeric_vs_Numeric(self,df,Numeric_variable_1,Numeric_variable_2,is_outliers=1):    


        print('------------------------------------------------------------------------------------------------------') 

        if is_outliers==1:
            print('用箱线图做异常值处理（丢弃）：')
            #合并特征，做异常值处理
            features = []
            features.append(Numeric_variable_1)
            features.append(Numeric_variable_2)
            #print(features)
            Outliers_to_drop = self.detect_outliers(df, features)
            df_new = df.drop(Outliers_to_drop, axis=0).reset_index(drop=True)

            x = df_new[Numeric_variable_1].values 
            y = df_new[Numeric_variable_2].values 

            #计算pearson相关系数      
            r_row, p_value = pearsonr(x, y) 
            print('%s 和 %s 的Pearson 相关系数为：%s ，P值为：' % (Numeric_variable_1,Numeric_variable_2,r_row.round(2)),p_value.round(3)) #pearson 相关系数

            r_row, p_value = spearmanr(x, y) 
            print('%s 和 %s 的Spearman 相关系数为：%s ，P值为：' % (Numeric_variable_1,Numeric_variable_2,r_row.round(2)),p_value.round(3)) #pearson 相关系数

            print()
            print()
            fig = plt.gcf()   
            fig.set_size_inches(8,6)

            # 分成2x2，占用第一个，即第一行第一列的子图 
            sns.scatterplot(data=df_new, 
                        x=Numeric_variable_1,
                        y=Numeric_variable_2
                       )
            plt.title('%s  VS  %s' % (Numeric_variable_1,Numeric_variable_2))

        else:
            print('没有单独做异常值处理：')

            x = df[Numeric_variable_1].values 
            y = df[Numeric_variable_2].values 

            #计算pearson相关系数      
            r_row, p_value = pearsonr(x, y) 
            print('%s 和 %s 的Pearson 相关系数为：%s ，P值为：' %(Numeric_variable_1,Numeric_variable_2,r_row.round(2)),p_value.round(3)) #pearson 相关系数

            r_row, p_value = spearmanr(x, y) 
            print('%s 和 %s 的Spearman 相关系数为：%s ，P值为：'% (Numeric_variable_1,Numeric_variable_2,r_row.round(2)),p_value.round(3)) #pearson 相关系数

            print()
            print()

            fig = plt.gcf()   
            fig.set_size_inches(8,6)

            # 分成2x2，占用第一个，即第一行第一列的子图 
            sns.scatterplot(data=df, 
                        x=Numeric_variable_1,
                        y=Numeric_variable_2
                       )
            plt.title('%s  VS  %s' % (Numeric_variable_1,Numeric_variable_2))


            
    def pairplot_corrsets(self,df):    
        print('散点图矩阵:')
        fig = plt.gcf()   
        sns.pairplot(data=df
                   )
        plt.show()
        print()
        print()
        print('------------------------------------------------------------------------------------------------------') 
        print('请注意不能对分类变量求相关系数哦～')
        ###相关系数矩阵
        plt.figure(figsize=(8,6)) #设置图片大小
        sns.heatmap(df.corr(),  #相关系数矩阵
                    annot=True,
                    fmt='.2f',
                    mask=df.corr().values<0.5 #小于0.5的值不展示
                    ,cmap='Blues'
                   )


        plt.title('相关系数矩阵')
            
            
            
# #############################测试
# x = DescriptiveStatistics(file_path = 'queue_feature.txt')
# df = x.load_dada(file_path = 'queue_feature.txt')
# x.data_detail_for_one(df,'consume_type')
# x.data_detail_for_con(df,'kuai_predict_time')
# x.Category_vs_Category(df,'consume_type','p_gender')
# x.Category_vs_Numeric(df,'consume_type','kuai_predict_time')

        
        
        
        
        
        
        
        
        
        
        
        
        
        
