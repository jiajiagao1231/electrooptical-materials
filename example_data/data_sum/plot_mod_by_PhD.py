import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path




def main():
	#first we need the dataframe
	file="example_data/data_sum/electroopitcal.xlsx"
	df = pd.read_excel(file, sheet_name="Tabelle1")
	print(df)
    #set the "name" column as index
	df.set_index("name", inplace=True)
    
	sorted_df = df.sort_values(by="exp", ascending=True)
    #plot values of sorted_df exp vs all columns that are not exp not source and not name
	columns_to_plot = sorted_df.columns.difference(["exp", "source", "name"])
	fig, ax = plt.subplots(figsize=(15,15))
	for col in columns_to_plot:
		ax.plot(sorted_df["exp"], sorted_df[col], "x", label=col)
	#plot the exp column as a line
	ax.plot(sorted_df["exp"], sorted_df["exp"], "k-")
	ax.set_xlabel("exp")
	ax.set_ylabel("prediction")
	#we want the xticks to be the name entries
	# Keep the x-axis scale as normal (exp values), but annotate each point with the index string below the x-axis
	for x, label in zip(sorted_df["exp"], sorted_df.index):
		ax.annotate(label, (x, ax.get_ylim()[0]), xytext=(0, -20), textcoords='offset points',
			ha='center', va='top', rotation=90, fontsize=10)
	#set x axis and y axis to be equal
	#ax.set_aspect('equal', adjustable='box')
	ax.legend()
	plt.savefig("example_data/data_sum/plot_all_PhD.pdf", bbox_inches='tight')
	#plt.show()
	#clear figure and axis to avoid replotting 
	plt.clf()
	plt.cla()
	

	#now we do the same again but only plot the part that is source i in the plot of plot_i.pdf
	max_sources= sorted_df["source"].max()
	min_sources= sorted_df["source"].min()
	for i in range(min_sources, max_sources+1):
		fig, ax = plt.subplots(figsize=(15,15))
		sorted_df_i = sorted_df[sorted_df["source"] == i]
		for col in columns_to_plot:
			ax.plot(sorted_df_i["exp"], sorted_df_i[col], "x", label=col)
		ax.plot(sorted_df_i["exp"], sorted_df_i["exp"], "k-")
		ax.set_xlabel("exp")
		ax.set_ylabel("prediction")
		# Keep the x-axis scale as normal (exp values), but annotate each point with the index string below the x-axis
		for x, label in zip(sorted_df_i["exp"], sorted_df_i.index):
			ax.annotate(label, (x, ax.get_ylim()[0]), xytext=(0, -20), textcoords='offset points',
				ha='center', va='top', rotation=90, fontsize=10)
		ax.legend()
		plt.savefig(f"example_data/data_sum/plot_source_{i}.pdf", bbox_inches='tight')
		plt.clf()
		plt.cla()

	#now we still do it separately but plot the ratios. x axis is just equally spaced from 0 to N where N
	#is the number of entries in sorted_df_i
	for i in range(min_sources, max_sources+1):	
		fig, ax = plt.subplots(figsize=(15,15))
		sorted_df_i = sorted_df[sorted_df["source"] == i]
		x_values = np.arange(len(sorted_df_i))
		for col in columns_to_plot:
			ax.plot(x_values, sorted_df_i[col] / sorted_df_i["exp"], "x", label=col)
		ax.plot(x_values, np.ones_like(x_values), "k-")
		ax.set_xlabel("index")
		ax.set_ylabel("prediction / exp")
		ax.set_xticks(x_values)
		ax.set_xticklabels(sorted_df_i.index, rotation=90)
		ax.legend()
		plt.savefig(f"example_data/data_sum/plot_source_{i}_ratio.pdf", bbox_inches='tight')
		#plt.show()
		plt.clf()
		plt.cla()

	#jia likes bar diagrams so we do the bar diagrams for the ratios (same as obve just not point plots)

	for i in range(min_sources, max_sources+1):
		fig, ax = plt.subplots(figsize=(15,15))
		sorted_df_i = sorted_df[sorted_df["source"] == i]
		x_values = np.arange(len(sorted_df_i))
		n_cols = len(columns_to_plot)
		bar_width = 0.8 / n_cols  # 80% of space per exp entry, divided among columns

		for idx, col in enumerate(columns_to_plot):
			offset = (idx - n_cols / 2) * bar_width + bar_width / 2
			ax.bar(x_values + offset, sorted_df_i[col] / sorted_df_i["exp"], 
				   width=bar_width, label=col)

		ax.axhline(y=1, color='k', linestyle='-')
		ax.set_xlabel("index")
		ax.set_ylabel("prediction / exp")
		ax.set_xticks(x_values)
		ax.set_xticklabels(sorted_df_i.index, rotation=90)
		ax.legend()
		plt.savefig(f"example_data/data_sum/plot_source_{i}_ratio_bar.pdf", bbox_inches='tight')
		plt.clf()
		plt.cla()#plt.show()

if __name__ == "__main__":
    main()
