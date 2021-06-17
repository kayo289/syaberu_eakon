#!/usr/bin/env python3
import pandas as pd
import numpy as np
from datetime import datetime as dt
from matplotlib import pyplot as plt
from scipy import stats
from mlxtend.evaluate import cochrans_q
from mlxtend.evaluate import mcnemar_table
from mlxtend.evaluate import mcnemar
import itertools
plt.rcParams['font.family'] = 'Hiragino Sans'

##############################################
# Parameters
##############################################
maxtime = 20 #アンケート回答時間の最大値 (分)

##############################################
# Functions
##############################################

def plotHist(df, colname): # dataframeと列名を与えるとヒストグラムを描画
    plt.figure()
    plt.hist(df[colname], bins = 50)
    plt.xlim(0, 1000)
    plt.xlabel(colname)
    plt.ylabel('頻度')
    plt.savefig("plot/"+colname,
                dpi = 400,
                bbox_inches='tight')
    plt.close()

def continuousParam(df, colname, displayname = ''): # 連続変数の要約
    name = '## ' + colname
    if displayname != '':
        name = '{}: '.format(displayname)
    array = df[colname].values
    print(name,
          '平均 (標準偏差), {:.1f} ({:.1f}); 中央値 (Q1–Q3), {:.1f} ({:.1f}–{:.1f}); 最小値–最大値, {:.1f}–{:.1f}; S-W test p-value, {:.3f}  '\
              .format(np.mean(array),
                      np.std(array),
                      np.median(array),
                      np.percentile(array, 25),
                      np.percentile(array, 75),
                      np.min(array),
                      np.max(array),
                      stats.shapiro(array)[1]))
    return array

def FigureContinuousQuestionForMovie(df, colname, ylabel, indexlist = ['1', '2', '3','4'],
                                     height = [11, 11, 12, 13], sig0 = [1, 3, 1, 2], sig1 = [2, 4, 3, 4],
                                     ylim0 = 0, ylim1 = 14, yticks = True): # 論文に挿入するための画像描画
    list_data_permovie = []
    print('## ' + colname + '  ')
    for i, j in enumerate(indexlist):
        array = continuousParam(df, colname + j, i)
        list_data_permovie.append(array)

    plt.figure(figsize = (7, 3.5))
    plt.boxplot(list_data_permovie) # boxplot
    plt.ylim(ylim0, ylim1)
    plt.xticks(range(1, 5), ['公益行動条件', '公益通知条件', '私益行動条件', '私益通知条件'])
    # plt.hlines(height, sig0, sig1, linewidth = 0.7, color = 'black')

    # if yticks:
        # plt.yticks(range(0, 11, 2), range(0, 11, 2))

    plt.ylabel(ylabel)

    for i, j, k in zip(height, sig0, sig1):
        plt.text((j + k)/2, i - 0.3, '*', fontsize = 15, horizontalalignment = 'center')

    plt.plot([], [], ' ', label='$*: \it{p} < 0.05\,&\,\it{r} > 0.1$')
    plt.legend(frameon=False, bbox_to_anchor=(1.02, 0.96), loc='lower right')

    plt.savefig("plot/figure_"+ylabel,
                dpi = 400,
                bbox_inches='tight')
    print("保存した")

##############################################
# Main
##############################################
df = pd.read_excel('data/sumdata.xlsx')
print(df.columns)

df = df.dropna()
# 回答時間を計算
starttime = pd.Series([dt.strptime(str(i), '%Y%m%d%H%M%S') for i in df['開始時刻(自動で入力されます。変更しないでください)']]) # 回答開始時刻
df['回答時間(秒)'] = (df['タイムスタンプ'] - starttime).dt.total_seconds() # 回答送信時刻から回答開始時刻を引いて回答にかかった時間を計算

# 回答に欠損のあるデータを除外
df_full = df.dropna()

# 回答時間でデータを抽出
df_crop = df_full[np.logical_and(30 <= df_full['回答時間(秒)'],
                                 df_full['回答時間(秒)'] <= 60*maxtime)] # 37秒以下, maxtime以上を除外
plotHist(df_crop, '回答時間(秒)')

# 各変数のまとめ
print('# 回答者全ての人数:', len(df.index))
print('# 回答に欠損のない回答者の人数:', len(df_full.index))
print('\n# 解析対象の回答者の人数: {} (回答者全体の{:.1f}%)'.format(len(df_crop.index),
                                                              100*len(df_crop.index)/len(df.index)))

# コクランのq検定
q,p_value = cochrans_q(np.array(["はい"]*len(df_crop.index)),df_crop["目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？1"].to_numpy(), df_crop["目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？2"].to_numpy(), df_crop["目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？3"].to_numpy(), df_crop["目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？4"].to_numpy())
print('Q: %.3f' % q)
print('p-value: %.6f' % p_value)

# mcnemar
lis = [1,2,3,4]
for pair in itertools.combinations(lis, 2):
	print(f"✅==動画{pair[0]}と{pair[1]}のmcnemar==")
	q,p_value = mcnemar(mcnemar_table(np.array(["はい"]*len(df_crop.index)),df_crop[f"目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？{pair[0]}"].to_numpy(), df_crop[f"目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？{pair[1]}"].to_numpy()))
	print('McNemar\'s Chi^2: %.3f' % q)
	print('McNemar\'s p-value: %.6f' % p_value)
	if p_value < 0.05:
		print(f"# 動画{pair[0]}")
		print(df_crop[f'目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？{pair[0]}'].value_counts(normalize=True) * 100)
		print(f"# 動画{pair[1]}")
		print(df_crop[f'目の前には「エアコンの指示を承認する」ボタンがあります。このあとボタンを押しますか？{pair[1]}'].value_counts(normalize=True) * 100)
	t_value, p_value = stats.ttest_ind(df_crop[f'動画内に登場した喋る家電の好感度を教えてください{pair[0]}'].to_numpy(), df_crop[f'動画内に登場した喋る家電の好感度を教えてください{pair[1]}'].to_numpy(), equal_var=True)
	print("👍==好感度について==")
	print("t_value:", t_value)
	print("p_value:", p_value)
	if p_value < 0.008:
		print(f"p = {p_value:.3f} のため、帰無仮説が棄却されました。AとBに差があります")
	else:
		print(f"{p_value:.3f} のため、帰無仮説が採択されました。AとBに差はありません")
	t_value, p_value = stats.ttest_ind(df_crop[f'動画内に登場した喋る家電の嫌悪感を教えてください{pair[0]}'].to_numpy(), df_crop[f'動画内に登場した喋る家電の嫌悪感を教えてください{pair[1]}'].to_numpy(), equal_var=True)
	print("👎==嫌悪感について==")
	print("t_value:", t_value)
	print("p_value:", p_value)
	if p_value < 0.025:
		print(f"p = {p_value:.3f} のため、帰無仮説が棄却されました。AとBに差があります")
	else:
		print(f"{p_value:.3f} のため、帰無仮説が採択されました。AとBに差はありません")

# # 論文に挿入するための画像描画
# FigureContinuousQuestionForMovie(df_crop, 'この後、動画内にある喋る空気清浄機の電源をつけたいですか？つけたくないですか？',
#                                  ylabel = '受容度', indexlist = ['inverseアA', 'アB', 'inverseイA', 'イB'])
FigureContinuousQuestionForMovie(df_crop, '動画内に登場した喋る家電の好感度を教えてください', ylabel = '好感度')
FigureContinuousQuestionForMovie(df_crop, '動画内に登場した喋る家電の嫌悪感を教えてください', ylabel = '嫌悪感')
