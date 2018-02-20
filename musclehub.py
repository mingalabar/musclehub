
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[2]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[3]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[4]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[5]:


# Examine visits here
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[6]:


# Examine fitness_tests here
sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
''')


# In[7]:


# Examine applications here
sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# In[8]:


# Examine purchases here
sql_query('''
SELECT *
FROM purchases
LIMIT 5
''')


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[19]:


df = sql_query('''
SELECT visits.first_name, visits.last_name, visits.gender, visits.email, 
    visits.visit_date, fitness_tests.fitness_test_date, applications.application_date, purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON visits.email = fitness_tests.email 
    AND visits.first_name = fitness_tests.first_name
    AND visits.last_name = fitness_tests.last_name
LEFT JOIN applications
    ON visits.email = applications.email
    AND visits.first_name = applications.first_name
    AND visits.last_name = applications.last_name
LEFT JOIN purchases
    ON visits.email = purchases.email
    AND visits.first_name = purchases.first_name
    AND visits.last_name = purchases.last_name
WHERE visits.visit_date >= "7-1-17"

''')


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[21]:


import pandas as pd
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[53]:


df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'A' if x is not None else 'B')


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[54]:


ab_counts = df.groupby('ab_test_group').count().reset_index()
print (ab_counts)


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[105]:


ab_test_labels = ["Fitness Test", "No Fitness Test"]
plt.pie(ab_counts.email, labels=ab_test_labels, autopct="%0.1f%%")
plt.axis('equal')
plt.savefig("ab_test_pie_chart.png")

plt.show()



# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[56]:


df['is_application'] = df.application_date.apply(lambda x: "Application" if x is not None else "No Application")


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[57]:


app_counts = df.groupby(['ab_test_group', 'is_application'])['email'].count().reset_index()
print(app_counts)


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[58]:


app_pivot = app_counts.pivot(
    columns = 'is_application',
    index = 'ab_test_group',
    values = 'email').reset_index()
print(app_pivot)


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[59]:


app_pivot['Total'] = app_pivot.Application + app_pivot['No Application']
print(app_pivot)


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[60]:


app_pivot['Percent with Application'] = app_pivot.Application / app_pivot.Total
print app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[75]:


from scipy.stats import chi2_contingency

X = [[250, 2254],
     [325, 2175]]
chi2, pval, dof, expected = chi2_contingency(X)
print pval


# ## Step 5: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[52]:


df['is_member'] = df.purchase_date.apply(lambda x: "Member" if x is not None else "Not Member")


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[65]:


just_apps = df[df.is_application == "Application"]
print(just_apps.head(5))


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[71]:


member = just_apps.groupby(['ab_test_group', 'is_member'])['email'].count().reset_index()

member_pivot = member.pivot(
    columns = 'is_member',
    index = 'ab_test_group',
    values = 'email')

member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']
member_pivot['Percentage Members'] = member_pivot.Member / member_pivot.Total
print(member_pivot)


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[76]:


from scipy.stats import chi2_contingency

X = [[200, 50],
     [250, 75]]
chi2, pval, dof, expected = chi2_contingency(X)
print pval


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[73]:


final_member = df.groupby(['ab_test_group', 'is_member'])['email'].count().reset_index()

final_member_pivot = final_member.pivot(
    columns = 'is_member',
    index = 'ab_test_group',
    values = 'email')

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']
final_member_pivot['Percentage Members'] = final_member_pivot.Member / final_member_pivot.Total
print(final_member_pivot)


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[78]:


from scipy.stats import chi2_contingency

X = [[200, 2304],
     [250, 2250]]
chi2, pval, dof, expected = chi2_contingency(X)
print pval


# ## Step 6: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[102]:


ax = plt.subplot()
plt.bar(ab_test_labels, app_pivot['Percent with Application'])
plt.title("% of people who filled up an application")
ax.set_yticks([0, 0.05, 0.10, 0.15])
ax.set_yticklabels(['0%', '5%', '10%', '15%'])
plt.savefig('percentage_application.png')
plt.show()


# In[103]:


ax = plt.subplot()
plt.bar(ab_test_labels, member_pivot['Percentage Members'])
plt.title("% of people who became members after filling up an application")
ax.set_yticks([0, 0.25, 0.50, 0.75, 1])
ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
plt.savefig("percentage_member_withapplication.png")
plt.show()


# In[104]:


ax = plt.subplot()
plt.bar(ab_test_labels, final_member_pivot['Percentage Members'])
plt.title("% of members")
ax.set_yticks([0, 0.02, 0.04, 0.06, 0.08, 0.1])
ax.set_yticklabels(['0%', '2%', '4%', '6%', '8%', '10%'])
plt.savefig("percentage_member.png")
plt.show()

