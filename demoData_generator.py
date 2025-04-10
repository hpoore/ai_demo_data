
from openai import OpenAI
import pandas as pd
import io
import os
import re

def generate_demo_dataset(
    key,
    dimensions,
    measures,
    start_date,
    end_date,
    row_count=2500,
    output_path=None,
    model="gpt-4o",
    temperature=0.3,
    trend_config=None,
    save=True  # new flag to control saving per chunk
):
    client = OpenAI(api_key=key)

    fields_str = ", ".join(dimensions + measures)

    base_prompt = f"""
Generate a realistic dataset in CSV format with the following:
- {row_count} rows
- {row_count} total transactions
- Include a 'Date' column with dates spread between {start_date} and {end_date}
- Use consistent formatting: dates in YYYY-MM-DD, percentages as decimals (e.g., 0.25), no currency symbols
- Reuse IDs for dimension consistency if relevant
- Use real values for textual data
- Use the following columns: {fields_str}
- The best performing sales rep is Hayden Poore
- Use realistic values for all textual data
- Do not use generic values for textual data
- Include IDs on all textual data
- Simulate realistic business behavior with patterns that could be discovered using a BI tool:
  - Sales trend increasing gradually over time (Jan to Mar)
  - Region-based differences (e.g., West region performs better than East)
  - Some products have consistently high margins, others low
  - End-of-month spikes in sales volume
  - Certain Sales Reps consistently outperform others in terms of value
  - A few high-value customers appear repeatedly, with varying order sizes
  - Higher average line value for "Online" transaction type compared to "Retail"
  - Different product categories perform differently by country
  - Include data for every month in time period
  - No more than 10 locations
  - No more than 500 products
"""

    if trend_config:
        base_prompt += f"\n- Additionally, apply these user-defined business logic patterns:\n{trend_config.strip()}"

    base_prompt += """
- Ensure consistent formatting:
  - Dates in YYYY-MM-DD
  - Percentages as decimals (e.g., 0.15)
  - No currency symbols
- Maintain logical relationships between calculated fields:
  - Value = Quantity × Value per Item
  - Cost = Quantity × Cost per Item
  - Profit $ = Value - Cost
  - Profit % = (Profit $ / Value) × 100
  - Avg Line Value = Value / Invoice Line Count
  - Gross Profit per Item = Value per Item - Cost per Item
- Return only raw CSV — no markdown, explanations, or headers
- Wrap text fields in double quotes if they contain spaces
- Do not include 'csv' in output
- Include column names as header in output

"""

    prompt = base_prompt

    csv_data = None 

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You generate clean, realistic, high-quality transaction datasets for business intelligence systems."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=16384
        )

        csv_data = response.choices[0].message.content.strip()

        # Remove unwanted prefixes and formatting artifacts
        lines = csv_data.splitlines()
        
        # Drop any leading lines that contain 'plaintext', ```csv, or just ```
        while lines and (lines[0].lower().strip() in {"```plaintext","plaintext", "```", "```csv"}):
            lines.pop(0)
        
        # Drop any trailing code block markers
        while lines and lines[-1].strip() == "```":
            lines.pop()
        
        cleaned_csv_data = "\n".join(lines)
        
        # Now safely parse into DataFrame
        df = pd.read_csv(io.StringIO(cleaned_csv_data))

        if save and output_path:
            df.to_csv(output_path, index=False)
            print(f"[✅] Dataset saved to: {os.path.abspath(output_path)}")

        return df

    except Exception as e:
        print("[❌] Failed to generate or save dataset:", str(e))
        print("[🧪] Raw output preview:")
        print(csv_data[:500])
        return None

def generate_large_dataset_in_chunks(
    key,
    dimensions,
    measures,
    start_date,
    end_date,
    total_rows,
    chunk_size=250,
    output_path="demo_sales_data.csv",
    model="gpt-4o",
    temperature=0,
    trend_config=None
):
    all_chunks = []
    rows_remaining = total_rows
    chunk_num = 1

    while rows_remaining > 0:
        current_chunk_size = min(chunk_size, rows_remaining)
        print(f"[📦] Generating chunk {chunk_num} with {current_chunk_size} rows...")

        chunk_df = generate_demo_dataset(
            key=key,
            dimensions=dimensions,
            measures=measures,
            start_date=start_date,
            end_date=end_date,
            row_count=current_chunk_size,
            model=model,
            temperature=temperature,
            trend_config=trend_config,
            save=False
        )

        if chunk_df is not None:
            all_chunks.append(chunk_df)
            rows_remaining -= current_chunk_size
            chunk_num += 1
        else:
            print("[⚠️] Skipping failed chunk.")
            break

    if not all_chunks:
        print("[❌] No data generated.")
        return None

    full_df = pd.concat(all_chunks, ignore_index=True)

    if output_path:
        full_df.to_csv(output_path, index=False)
        print(f"[✅] Full dataset saved to: {os.path.abspath(output_path)}")

    return full_df
