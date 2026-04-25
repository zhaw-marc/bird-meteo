"""Prompt templates for AI-generated summaries."""

FINDINGS_PROMPT_TEMPLATE = """
You are a Swiss ornithologist and data scientist. Summarize the following bird sighting and weather analysis results.

### Analysis Context
- **Species**: {species}
- **Date Range**: {start_date} to {end_date}

### Statistical Results
#### Weather Impact (Pearson Correlation)
- **Weather Parameter**: {weather_param}
- **Correlation Coefficient (r)**: {pearson_r:.4f}
- **p-value**: {p_value_weather:.4e}
- **Sample Size (n)**: {n_weather} days

#### Regional Comparison (Independent t-test)
- **Region A**: {region_a}
- **Region B**: {region_b}
- **Comparison Metric**: {metric}
- **t-statistic**: {t_statistic:.4f}
- **p-value**: {p_value_regions:.4e}
- **Sample Sizes**: n_a={n_a}, n_b={n_b} days

### Instructions
1. Interpret these results for a scientific report.
2. Explain the biological significance of the weather correlation (or lack thereof).
3. Discuss the differences (or similarities) between the two regions.
4. Mention if the results are statistically significant (p < 0.05).
5. Keep the tone professional, objective, and concise (max 300 words).
6. Format the output with clear headings and Markdown.
"""
