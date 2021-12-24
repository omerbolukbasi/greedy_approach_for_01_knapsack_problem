#!/usr/bin/env python
# coding: utf-8

# # Knapsack Problem <br><br>
# ### Greedy Approach

# In[43]:


# Get inputs

input_file_name = "sample1.txt"

with open(input_file_name, "r") as f:
    
    # Store all input into an input_list.
    input_list = f.read()
    input_list = input_list.replace("\n"," ")
    input_list = input_list.split()
    
    #Convert items to integer.
    input_list = [int(i) for i in input_list]
    
    # Store first 2 items as m and n respectively. m: Number of knapsacks, n: Number of items
    m = input_list[0]
    n = input_list[1]

    # Store following n items into item_values_list.
    item_values_list = input_list[2:2+n]
    
    # Store following m items into knapsack_capacities.
    knapsack_capacities = input_list[2+n:2+n+m]
    
    # Store following n*m items into items_wight_matrix.
    items_weight_matrix = []
    for k in range(m):
        items_weight_matrix.append(input_list[2+n+m+n*k:2+n+m+n*(k+1)])
    
f.close()


# In[44]:


import pandas as pd
import numpy as np


# In[45]:


# Store item lists into a Pandas data frame in order to visualize better.
df = pd.DataFrame(items_weight_matrix)
df = df.T
df["values"] = item_values_list
df_original = df
df


# In the greedy method for 1 constraint knapsack problem, v/w is calculated for each item. And the items are sorted in 
# knapsacks based on this v/w values. The single knapsack is filled with the items that have highest v/w values. Higher v/w
# values are considered as high valued but low cost items. So, initailly the items that have highest values but lowest 
# weights are consumed with this method.
# 
# In this homework we reduce the multi constraint knapsack problem to a single constraint knapsack problem by calculating
# a single v/w value which is produced from multiple weights.
# 
# In order to reduce the multiple constraints into 1 constraint first we normalize the weights with the following formula:
# 
# Mean Normalization:
# normalized_df=(df-df.mean())/df.std()
# 
# We also test the Min-Max Normalization and Log Normalization but the test results are not as good as mean normalization.
# 

# In[46]:



# First we normalize the constraints in order to get a unitless knapsack versions. 
for i in range(m):
    # No Normalization:
    #df["normalized_{}".format(i)] = df[i]
    
    # Mean Normalization (0 - 1):
    df["normalized_{}".format(i)] = (df[i] - df[i].mean()).abs()/df[i].std()
    
    # Min Max Normalization:
    #df["normalized_{}".format(i)] = (df[i] - df[i].min())/(df[i].max() - df[i].min())
    
    # Logarithm Normalization:
    #df["normalized_{}".format(i)] = np.log2((df[i]+1)/2)

# Second all normailzed constraints are added.
df["sum_of_normalized_constraint"] = 0
for i in range(m):
    df["sum_of_normalized_constraint"] = df["sum_of_normalized_constraint"] + df["normalized_"+str(i)]

# Now we can calculate normalized single v/w from the normalized sum.

df["v/w(normalized)"] = df["values"] / df["sum_of_normalized_constraint"]

# Based on the greedy approach, sort the items by v/w

df = df.sort_values(by = "v/w(normalized)", ascending=False)

df


# In[48]:


# Fill in the knapsacks
# First calculate the accumulation of constraints. Remember that the items are sorted in the way that normalized v/w
# value gets the highest rate.

for knapsack_id in range(m):
    df["knapsack_accumulation_{}".format(knapsack_id)] = df[knapsack_id].expanding(min_periods=2).sum()
df 


# In[50]:


# Filter out the items when accumulated constraints exceed the corresponding knapsack capacity.

df_remainder = df

for knapsack_id in range(m):
    df_remainder = df_remainder.query('knapsack_accumulation_{} > {}'.format(knapsack_id,knapsack_capacities[knapsack_id]))
    
for knapsack_id in range(m):
    df = df.query('knapsack_accumulation_{} <= {}'.format(knapsack_id,knapsack_capacities[knapsack_id]))
df


# In[51]:


# Fill the remainder empty places in the knapsacks with the remainder items which can fit with the empty spaces.

# All remainder items are being tried for the last empty spaces in the knapsacks.
for i in df_remainder.index:
    can_not_add_item = False
    for k in range(m):
        if df_remainder[k].loc[i] + df["knapsack_accumulation_{}".format(k)].iloc[-1] > knapsack_capacities[k]:
            # If one of the knapsack is out of bounds after adding the candidate item then we set this item 
            # as can_not_add_item = True.
            can_not_add_item = True
    if not can_not_add_item:
        # If any item can pass all constraints after added, then we update df (the items that will be put in knapsacks)
        # by adding this item.
        for k in range(m):
            df_remainder.at[i,"knapsack_accumulation_{}".format(k)] = df_remainder[k].loc[i]+df.iloc[-1]["knapsack_accumulation_{}".format(k)]
        df = df.append(df_remainder.loc[i])
df


# In[52]:


# Get the total_value from the remaining items.
Total_Value = df["values"].sum()
Total_Value = int(Total_Value)
Total_Value


# In[53]:


# Get 0 - 1 item list that put in the knapsacks.

items_in_knapsack = df.index

# Items that put in the knapsacks are set as '1' in the original data frame. And the rest is set as '0'.
df_original_ = df_original.reset_index()
df_original_ = df_original_.rename(columns={"index":"item_id"})
df_original_.loc[df_original_["item_id"].isin(items_in_knapsack), "items_in_knapsack"] = 1
df_original_["items_in_knapsack"] = df_original_["items_in_knapsack"].fillna(0)
df_original_["items_in_knapsack"] = df_original_["items_in_knapsack"].astype(int)
df_original_


# In[54]:


# Now output file is generated with the Total_Value and items_in_knapsack.

with open("output_"+input_file_name,"w") as f:
    f.write(str(Total_Value)+"\n")
    for i in df_original_["items_in_knapsack"]:
        f.write(str(i)+"\n")
f.close()

