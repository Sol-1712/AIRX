import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import xml.etree.ElementTree as ET
import sys
from datetime import datetime


sns.set_theme(style='darkgrid')

def plot_chart(df):
  
  file_name = os.path.basename(file_path)
  base_name, extension = os.path.splitext(file_name)
  directory = os.path.dirname(file_path)
  
  columns = get_column(df)
  headers = [df.columns[i].rstrip('*') for i in columns]
  c_headers = [header.replace(' / ', '') for header in headers]
  
  # Index holder
  x = None
  x_count = 0
  # Num columns used
  c_count = 0
  # 2nd plot
  plot2 = False
  
  # Checks for selected index  
  for column in columns: 
    column_name = df.columns[column] 
    if '*' in column_name:
      x_count += 1
      if x is None:
        x = column_name.rstrip('*')
    else:
      c_count += 1
      
  # Only index selected
  if x and c_count == 0:
    print("Chỉ (các) chỉ mục đã chọn, hãy thử lại\n")
    plot_chart(df)
    
  if x_count > 1:
    g = multi_plot(df, columns)
    
    # Filename
    num_date = convert_date()
    save = num_date + " " + df.index.name + '~(' + "+".join(c_headers) + ')'
    output_path = os.path.join(directory, f"{save}.png")
    g.savefig(output_path)
    print()
  else:
    
    fig, ax1 = plt.subplots(figsize=(20, 10))
    # Plots selected columns      
    for column in columns:
      column_name = df.columns[column]
      if '*' in column_name:
        continue
  
      avg = df[column_name].mean()
      # Second Plot
      if plot2:
        ax2 = ax1.twinx()
        if x == None:
          sns_plt = sns.lineplot(data = df, x = df.index, y = column_name, color = 'green', ax = ax2, label = column_name)
        else:
          sns_plt = sns.lineplot(data = df, x = df.index, y = column_name, ax = ax2, hue = x)
        ax2.axhline(y=avg, color = 'black', linestyle = '-.', label = f'Average ({column_name})')
        ax2.set_ylabel(column_name)
    
      # First Plot  
      else:
        # No index
        if x == None:
          sns_plt = sns.lineplot(data = df, x = df.index, y = column_name, ax = ax1, label = column_name)
          # Indexed 
        else:
          sns_plt = sns.lineplot(data = df, x=df.index, y = column_name, ax = ax1,  hue = x)
        
        ax1.axhline(y=avg, color = 'black', linestyle = '--', label = f'Average ({column_name})')
        ax1.set_xlabel(df.index.name)
        ax1.set_ylabel(column_name)
      
        # Plot 2 flag
        if c_count > 1:
          plot2 = True
    
    # Customize plot
    plt.title(dates)
    h, l = sns_plt.get_legend_handles_labels()
    if x == None:
      ax1.legend(title = "Columns", loc = 'upper left')
    else:
      ax1.legend(title = x, handles = h, labels = l, loc = 'best')
    
    if plot2:
      ax2.legend(title = "Columns", loc = 'upper right')
    
    # Filename
    if dates != 'All time':
      num_date = convert_date()
    else:
      num_date = dates
    save = num_date + " " + base_name + '~(' + "+".join(c_headers) + ')'
    output_path = os.path.join(directory, f"{save}.png")
    plt.savefig(output_path)
    print()
  
  cont = input("Đã lưu biểu đồ. Tiếp tục? (y/n): ")
  if cont == 'y':
    plot_chart(df)
  else:
    sys.exit()
	

### Plots Multiple index
def multi_plot(df, columns):
  cnames = [df.columns[i].rstrip('*') for i in columns]
  g = sns.FacetGrid(data = df, col = cnames[1], col_wrap = 3, height = 3, aspect = 2)
  g.map_dataframe(sns.lineplot, x = df.index.name, y = cnames[2], hue = cnames[0])
  g.add_legend(title = cnames[0])
  
  return g

  
### Turns the date text to numerics
def convert_date():
  date_str = dates
  if date_str:
    date_start, date_end = date_str.split(" - ")
    start_num = datetime.strptime(date_start, "%B %d, %Y")
    end_num = datetime.strptime(date_end, "%B %d, %Y")
    num_date = f"{start_num.strftime('%d-%m-%Y')}to{end_num.strftime('%d-%m-%Y')}"

    return num_date


#### Function that asks user for columns to plot
def get_column(df):
  
  # Show Column Menu
	print("Các cột có sẵn: (* chỉ số bằng nhau) \n")
	for i, col in enumerate(df.columns):
	    print(f"{i}: {col}")
		
	columns = []
	non_index = 0
	index = 0
	while True:		
		column_number_input = input("\nEnter a column number, indexes first: ")

		try:
			column_number = int(column_number_input)
			if 0 <= column_number < len(df.columns) and column_number not in columns:
		          	columns.append(column_number)
		          	if '*' not in df.columns[column_number]:
		          	  non_index += 1
		          	else:
		          	  index += 1
		          	break  
			else:
		  		print("Invalid column number. Please try again.")
    
		except ValueError:
			print("Invalid input. Please enter a valid column number.")

	while (index == 0 and non_index < 2) or (index > 0 and non_index == 0):
		column_number_input = input("\nEnter another column number, or press Enter to skip: ")
		if column_number_input == "":
		  	   break 
		try:
		  		column_number = int(column_number_input)
		  		if 0 <= column_number < len(df.columns) and column_number not in columns:
		  		      	columns.append(column_number)
		  		      	if '*' not in df.columns[column_number]:
		  		      	  non_index += 1
		  		      	else:
		  		      	  index += 1
		  		elif column_number in columns:
		  		  pass
		  		else:
		  			print("Invalid column number. Please try again.")
		  			
		except ValueError:
		  print("Invalid input. Please enter a valid column number or press Enter to skip.")
	 
	columns.sort()  
	return columns
	
	
### Function to parse xml   
def parse_xml():
  
  tree = ET.parse(file_path)
  root = tree.getroot()
  
  date_range = root.find("date-range")
  global dates
  if date_range is not None:
    dates = date_range.text
  else:
    dates = None
  
  rows = []
  for row in root.findall(".//row"):
    row_data = {cell.find("key").text: cell.find("value").text for cell in row.findall("cell")}
    rows.append(row_data)

  df = pd.DataFrame(rows)
  df.set_index(df.columns[0], inplace = True)
  df.drop('Currency code', axis = 1, inplace = True)
  
  df = clean_data(df)  
  save_csv(df)	
  return df
  
  
def clean_data(df):
  
  df.replace('--', 0, inplace = True)
  df_copy = df.copy()
  
  for idx, column in enumerate(df.columns):
    df[column] = df[column].replace({',': '', '%': ''}, regex = True)
    df_copy[column] = df_copy[column].replace({',': '', '%': ''}, regex = True)
    df[column] = pd.to_numeric(df[column], errors = 'coerce')
    if df[column].isna().any() or 'ID' in column:
      df[column] = df[column].fillna(df_copy[column])
      df.columns.values[idx] = column + '*'
    
  return df

        	
### Function that saves the file as a csv
def save_csv(df):
  
  averages = df.mean(numeric_only = True)
  averages_row = pd.DataFrame([averages], columns = df.columns)
  averages_row.index = ['Average']
  df = pd.concat([df, averages_row])
  file_name = os.path.basename(file_path)
  base_name, extension = os.path.splitext(file_name)
  directory = os.path.dirname(file_path)
  output_path = os.path.join(directory, f"{base_name} {dates}.csv")
  df.to_csv(output_path, index=True)
  print(f"Tệp được lưu dưới dạng {output_path}")
    
  return
    
    
### Function to check the file given
def check_path():
  try:
    df = parse_xml()
    return df
  except FileNotFoundError:
    check = input("Invalid file path, try again or press Enter to exit: ")
    if check == "":
      sys.exit()
    else:
      global file_path 
      file_path = check
      df = check_path()
  except ET.ParseError:
    print("File is not a valid XML file. ")
    sys.exit()
  except Exception as e:
    print(e)
    sys.exit()
  
  return df
    
    
def main():
	
	file_name = input("Nhập đường dẫn đến tập tin của bạn (với phần mở rộng!): ").strip()
	global file_path
	file_path = os.path.join(os.getcwd(), file_name)
	df = check_path()

	#	PRINTING	STUFF
	print('\nMẫu tệp: \n')
	print(f'{df.head(10)} \n')
	
	
	plot_chart(df)
	
	
if __name__ == "__main__":
	main()
