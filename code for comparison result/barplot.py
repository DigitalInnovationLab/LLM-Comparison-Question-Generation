import pandas as pd
import matplotlib
import seaborn as sns
import numpy as np

matplotlib.use('TkAgg')  # Use TkAgg backend for rendering
import matplotlib.pyplot as plt

# Define the desired order of LLMs and Metrics
llm_order = ['Claude', 'ChatGPT', 'Databricks', 'DeepSeek', 'Gryphe', 'Llama', 'Mistral', 'Qwen', 'Upstage', 'Wizard']
metrics_order = ['relevance', 'reading_comprehension', 'question_difficulty', 'question_clarity', 'context_utilisation']
metric_title = ["Relevance", "Reading Comprehension", "Question Difficulty", "Question Clarity", "Context Utilisation"]
question_types = ["saqs", "blqs", "gfqs", "mcqs"]
qtype_titles = ["SAQs", "BLQs", "GFQs", "MCQs"]

# Load the data (ensure to replace 'b.csv' with the actual path to your data file)
df = pd.read_csv('comparison_table.csv')

# Create a figure with 3 rows and 2 columns of subplots
fig, axes = plt.subplots(1, 2, figsize=(20, 16), sharey=False)
axes = axes.flatten()  # Flatten the axes array for easier iteration

# Iterate over metrics to plot each one
#for i, metric in enumerate(metrics_order):
for j in range (0,1):
    metric = metrics_order[j]
    metric_data = df[df["Metrics"] == metric]  # Filter data for the current metric
    i = j-4
    # Pivot the data for plotting and reorder rows/columns
    pivot_data = metric_data.pivot_table(index='LLM', columns='Question Type', values='Average', fill_value=0)
    pivot_data = pivot_data.reindex(index=llm_order, columns=question_types)

    # Plot grouped bar chart for the current metric
    pivot_data.plot(kind='bar', ax=axes[i], width=0.8, edgecolor='black', legend=False)

    # Set y-axis limits after plotting
    if j == 5:  # Special handling for "generation_time"
        axes[i].set_ylim(0, 26)
    else:
        axes[i].set_ylim(0, 1)  # Set y-axis between 0 and 1 for other metrics

    # Customize the subplot appearance
    axes[i].set_title(metric_title[j], fontsize=20, pad=15)
    axes[i].grid(axis='y',alpha=0.5)
    axes[i].grid(axis='x', alpha=0)
    #axes[i].set_axisbelow(True)
    axes[i].set_xlabel('', fontsize=16)
    if j == 5:
        axes[i].set_ylabel('Average time (sec)', fontsize=20)
        axes[i].set_yticks(np.arange(0, 27, 2))
    else:
        axes[i].set_ylabel('Average Score', fontsize=20)
        axes[i].set_yticks(np.arange(0, 1.1, 0.1))
    axes[i].tick_params(axis='x', rotation=30, labelsize=16)
    axes[i].tick_params(axis='y', labelsize=16)

# Add a shared legend
# handles, labels = axes[0].get_legend_handles_labels()
# fig.legend(handles, qtype_titles, title="Question Types", loc='upper center', bbox_to_anchor=(0.5, 1.0),
#             ncol=len(question_types), fontsize=20, title_fontsize=22)

[fig.delaxes(ax) for ax in axes.flatten() if not ax.has_data()]
plt.subplots_adjust(hspace=0.8, wspace=0.11)
# Adjust layout for better visualization


plt.tight_layout(rect=[0, 0, 1, 0.93])  # Leave space at the top for the legend
plt.grid(True)
plt.show()
