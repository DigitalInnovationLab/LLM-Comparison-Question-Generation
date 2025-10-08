import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for rendering
import matplotlib.pyplot as plt



llms = ['Claude', 'ChatGPT', 'Databricks', 'DeepSeek', 'Gryphe', 'Llama', 'Mistral', 'Qwen', 'Upstage', 'Wizard']
metrics_order = ['relevance', 'reading_comprehension', 'question_difficulty', 'question_clarity', 'context_utilisation']
metric_title = ["Relevance", "Reading\nComprehension", "Question\nDifficulty", "Question\nClarity", "Context\nUtilisation",]
question_types = ["saqs", "blqs", "gfqs", "mcqs"]
qtype_titles = ["SAQs", "BLQs", "GFQs", "MCQs"]
 
# Define labels for the radar chart (example)
all_data = pd.read_csv('comparison_table.csv')
i = 0
for question_type in question_types:
    data = all_data[all_data['Question Type'] == question_type]

    # Extract unique metrics and determine the number of metrics
    metrics = data['Metrics'].unique()
    num_metrics = len(metrics)

    group_mean = data.groupby(['Metrics'])[['Average']].mean().sort_values(['Metrics'], ascending=False)
    group_max = data.groupby(['Metrics'])[['Average']].max().sort_values(['Metrics'], ascending=False)
    group_min = data.groupby(['Metrics'])[['Average']].min().sort_values(['Metrics'], ascending=False)

    print(group_mean)

    # group_mean = np.mean(data, axis=0)
    # group_max = np.max(data, axis=0)
    # group_min = np.min(data, axis=0)

    # Close the circle for radar chart
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]

    # Prepare data for radar chart by appending the first value to close the circle
    group_mean_values = group_mean['Average'].to_numpy().tolist()
    group_mean_values += group_mean_values[:1]

    group_max_values = group_max['Average'].to_numpy().tolist()
    group_max_values += group_max_values[:1]

    group_min_values = group_min['Average'].to_numpy().tolist()
    group_min_values += group_min_values[:1]

    # Initialize radar chart
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    print(group_max_values)
    print(group_min_values)
    print(group_mean_values)

    # Plot the group's boundary and average pattern
    ax.fill(angles, group_max_values, color='blue', alpha=0.1, label='Group Max')
    ax.fill(angles, group_min_values, color='red', alpha=0.1, label='Group Min')
    ax.plot(angles, group_mean_values, color='green', linewidth=2, label='Group Mean')

    # Add category labels
    #ax.set_yticks([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_title,fontsize=20, wrap=True, va='center')
    #ax.tick_params(axis='x', rotation=90, labelsize=16)
    ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.set_ylim(0, 1)

    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=16)

    # Title
    plt.title("Grouped pattern of performance Metrics for "+qtype_titles[i] , pad=20, fontsize=20)
    i = i+1
    plt.tight_layout()
    plt.show()


    # # Create angles for the radar chart
    # angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    # angles += angles[:1]  # Close the circle
    #
    # # Initialize the radar chart
    # fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    #
    # # Plot each LLM's data
    # for llm in llms:
    #     llm_data = filtered_data[filtered_data['LLM'] == llm]
    #     scores = llm_data['Average'].tolist()
    #     scores += scores[:1]  # Close the circle
    #
    #     ax.plot(angles, scores, label=llm, linewidth=2, linestyle='solid')
    #     ax.fill(angles, scores, alpha=0)  # Set fill transparency
    #
    # # Configure the radar chart
    # ax.set_theta_offset(np.pi / 2)
    # ax.set_theta_direction(-1)
    # ax.set_xticks(angles[:-1])
    # ax.set_xticklabels(metric_title, fontsize=20, wrap=True, va='center')
    # ax.set_rlabel_position(5)
    # ax.tick_params(axis='x', rotation=90, labelsize=16)
    # ax.set_yticks([0.1, 0.2,0.3,0.4,0.5, 0.6, 0.7,0.8,0.9, 1.0, 1.1])
    # ax.set_yticklabels(['0.1', '0.2','0.3','0.4','0.5','0.6','0.7','0.8', '0.9','1.0','1.1'], fontsize=16)
    # ax.set_ylim(0, 1)
    #
    # # Use solid grid lines
    # ax.grid(linewidth=1, linestyle='-')
    #
    # # Set the title and legend
    # ax.set_title(qtype_titles[i], fontsize=22)
    # i = i + 1
    # ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=16)
    #
    # # Adjust layout and display the chart
    # plt.tight_layout()
    # plt.show()


 
#