import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from datetime import date
import plotly.express as px

conn=mysql.connector.connect(
    host="localhost",
    user="root",
    password="25Mysql@",
    database="nutrition"
)

def execute_query(query):
    cursor=conn.cursor()
    cursor.execute(query)
    result=cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(result,columns=columns)
    
st.set_page_config(
    page_title="Nutrition Paradox"
)
st.title("Obesity and Malnutrition Analysis")

tab1,tab2=st.tabs(["Queries","EDA"])

queries={
    "1.Top 5 regions with the highest average obesity levels in the most recent year(2022) ":
        "Select Region,AVG(Mean_Estimate) as avg_obesity from obesity where Year=2022 group by Region order by avg_obesity desc limit 5",
    "2. Top 5 countries with highest obesity estimates ":
        "Select Country , AVG(Mean_Estimate) as avg_obesity from obesity group by Country order by avg_obesity desc limit 5",
    "3. Obesity trend in India over the years(Mean_estimate) ":
        "select Year, avg(Mean_Estimate) from obesity where Country='India' group by year order by year",
    
    "4. Average obesity by gender":
        "select Gender , AVG(Mean_Estimate) as avg_obesity from obesity group by Gender order by avg_obesity desc",
    
    "5. Country count by obesity level category and age group":
    "select Obesity_level , Age_Group , count(DISTINCT Country) as country_count from obesity group by obesity_level,age_group order by obesity_level,Age_Group",

    "6 a). Top 5 countries least reliable countries(with highest CI_Width)":
    "select Country , avg(CI_Width) as avg_ci_width from obesity group by country order by avg_ci_width desc limit 5",
    "6 b). Top 5 most consistent countries (smallest average CI_Width)":
    "select Country , avg(CI_Width) as avg_ci_width from obesity group by country order by avg_ci_width asc limit 5",

    "7. Average obesity by age group":
    "select Age_Group ,avg(Mean_Estimate)  as avg_obesity from obesity group by Age_Group order by avg_obesity desc",

    "8. Top 10 Countries with consistent low obesity (low average + low CI) over the years":
    "select Country,avg(Mean_Estimate)  as avg_obesity, avg(CI_Width) as avg_ci_width , (avg(Mean_Estimate) + avg(CI_Width))  as low_consistent_obesity from obesity group by Country order by low_consistent_obesity asc limit 10",

    "9. Countries where female obesity exceeds male by large margin (same year)":       
    "select f.country, f.year, f.mean_estimate as female_obesity, m.mean_estimate as male_obesity, (f.mean_estimate - m.mean_estimate) as obesity_gap from obesity f join obesity m on f.country = m.country and f.year = m.year where f.gender = 'female' and m.gender = 'male' and (f.mean_estimate - m.mean_estimate)>15 order by obesity_gap desc",

    "10.Global average obesity percentage per year":
    "select Year,avg(Mean_Estimate) as avg_obesity_percentage from obesity group by Year order by Year",
    
    "11.Avg. malnutrition by age group":
    "select Age_Group,year, avg(Mean_Estimate) as avg_malnutrition from malnutrition group by Age_Group,year order by year asc ",
    
    "12.Top 5 countries with highest malnutrition(mean_estimate)":
    "select Country,avg(Mean_Estimate) as avg_malnutrition from malnutrition group by Country order by avg_malnutrition desc limit 5",
    
    "13.Malnutrition trend in African region over the years ":
    "select Region,Year,avg(Mean_Estimate) as avg_malnutrition from malnutrition where Region='Africa' group by Year order by Year",
    
    "14.Gender-based average malnutrition":
    "select Gender,avg(Mean_Estimate) as avg_malnutrition from malnutrition group by Gender order by avg_malnutrition desc",
    
    "15.Malnutrition level-wise (average CI_Width by age group) ":
    "select Malnutrition_Level,Age_Group,avg(CI_Width) as avg_ci_width from malnutrition group by Malnutrition_Level,Age_Group order by Malnutrition_Level,Age_Group",
    
    "16.Yearly malnutrition change in specific countries(India, Nigeria, Brazil)":
    "select Country,Year,avg(Mean_Estimate) as avg_me from malnutrition where Country in ('India','Nigeria','Brazil') group by Country,Year order by Country,Year",
    
    "17.Regions with lowest malnutrition averages ":
    "select Region,avg(Mean_Estimate) as avg_malnutrition from malnutrition group by Region order by avg_malnutrition asc limit 10",

    "18.Countries with increasing malnutrition":
    "select curr.country, (curr.mean_estimate - max(prev.mean_estimate))  as increase from malnutrition curr join malnutrition prev on curr.country = prev.country and prev.year < 2022 where curr.year = 2022 group by curr.country, curr.mean_estimate having increase > 0 order by increase desc;",
    
    "19.Min/Max malnutrition levels year-wise comparison":
    "select Year,min(Mean_Estimate) as min_year_me,max(Mean_Estimate) as max_year_me from malnutrition group by Year order by Year",
    
    "20.High CI_Width flags for monitoring(CI_width > 5)":
"select country, year, region, gender, max(ci_width) as ci_width, avg(mean_estimate) as mean_estimate from malnutrition where ci_width > 5 group by country, year, region, gender order by ci_width desc, year desc",
    
    "21.Obesity vs malnutrition comparison by country(any 5 countries)":
    "select o.Country,o.Year,avg(o.Mean_Estimate) as obesity_avg,avg(m.Mean_Estimate) as malnutrition_avg from obesity o join malnutrition m on o.Country=m.Country and o.Year=m.Year where o.Country in ('India','United States','United Kingdom','Nigeria','China') group by o.Country,o.Year order by o.Country,o.Year",
    
    "22.Gender-based disparity in both obesity and malnutrition":
    "select o.Gender,avg(o.Mean_Estimate) as obesity_avg,avg(m.Mean_Estimate) as malnutrition_avg,(avg(o.Mean_Estimate)-avg(m.Mean_Estimate)) as disparity from obesity o join malnutrition m on o.Gender=m.Gender group by o.Gender",
    
    "23.Region-wise avg estimates side-by-side(Africa and America)":
    "select o.Region,avg(o.Mean_Estimate) as obesity_avg,avg(m.Mean_Estimate) as malnutrition_avg from obesity o join malnutrition m on o.Region=m.Region where o.Region in ('Africa','America','Americas') group by o.Region",
    
    "24.Countries with obesity up & malnutrition down":
    "select o.Country,avg(o.Mean_Estimate) as obesity_avg ,avg(m.Mean_Estimate) as malnutrition_avg from obesity o join malnutrition m on o.Country=m.Country group by o.Country having obesity_avg>malnutrition_avg order by (obesity_avg-malnutrition_avg) desc",

    "25.Age-wise trend analysis ":
    "select o.Age_Group,o.Year,avg(o.Mean_Estimate) as obesity_avg,avg(m.Mean_Estimate) as malnutrition_avg from obesity o join malnutrition m on o.Age_Group=m.Age_Group and o.Year=m.Year group by o.Age_Group,o.Year order by o.Age_Group,o.Year"
}

with tab1:
    st.header("Queries")
    selected=st.selectbox("Select a query to run:",list(queries.keys()))
    df=execute_query(queries[selected])
    st.dataframe(df)

with tab2:
    st.header("EDA Visualizations")
    
    df_obesity = pd.read_sql("SELECT *FROM obesity", conn)
    df_malnutrition = pd.read_sql("SELECT *FROM malnutrition", conn)
          
    st.subheader("Obesity Data")
    st.dataframe(df_obesity)
    st.subheader("Malnutrition Data")
    st.dataframe(df_malnutrition)

    fig1,ax1 = plt.subplots(figsize=(16, 8))
    st.subheader("1.Line Chart: Global Obesity & Malnutrition Trends")
    ob_global=df_obesity.groupby('Year')['Mean_Estimate'].mean().reset_index()
    mal_global=df_malnutrition.groupby('Year')['Mean_Estimate'].mean().reset_index()
    sns.lineplot(data=ob_global,x='Year',y='Mean_Estimate',label='Obesity',ax=ax1)
    sns.lineplot(data=mal_global,x='Year',y='Mean_Estimate',label='Malnutrition',ax=ax1)
    ax1.set_xlabel("Gender",fontsize=16)
    ax1.set_ylabel("Mean_Estimate",fontsize=16)
    st.pyplot(fig1)

    st.subheader("2.i) Bar Chart: Top 10 Countries by Obesity vs Malnutrition")
    fig2,ax2 = plt.subplots(figsize=(16, 8))
    top10_ob=(df_obesity.groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(10).reset_index())
    top10_mal=(df_malnutrition[df_malnutrition['Country'].isin(top10_ob['Country'])].groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(10).reset_index())
    top10_ob['Type'] = 'Obesity'
    top10_mal['Type'] ='Malnutrition'
    comb=pd.concat([top10_ob,top10_mal])
    sns.barplot(data=comb,x='Country',y='Mean_Estimate',palette='Set1',hue='Type',ax=ax2)
    st.pyplot(fig2)

    st.subheader("2.ii) Bar Chart: Top 10 Countries by Obesity vs Malnutrition")
    fig9,ax9 = plt.subplots(figsize=(16, 8))
    top10_mal=(df_malnutrition.groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(10).reset_index())
    top10_ob=(df_obesity[df_obesity['Country'].isin(top10_mal['Country'])].groupby('Country')['Mean_Estimate'].mean().sort_values(ascending=False).head(10).reset_index())
    top10_ob['Type']= 'Obesity'
    top10_mal['Type']= 'Malnutrition'
    comb=pd.concat([top10_mal,top10_ob])
    sns.barplot(data=comb,x='Country',y='Mean_Estimate',palette='Set1',hue='Type',ax=ax9)
    st.pyplot(fig9)

    st.subheader("3. Map Visual: Obesity Levels by Country")
    df_obesity_sorted=df_obesity.sort_values("Year")
    fig3 =px.choropleth(df_obesity_sorted,locations="Country",locationmode="country names", color="obesity_level",hover_name="Country",animation_frame="Year",width=1000,height=500)
    st.plotly_chart(fig3)

    st.subheader("4. Stacked Bar: Obesity and Malnutrition by Gender")
    fig4, ax4 =plt.subplots(figsize=(16, 8))
    ob_gender= df_obesity.groupby('Gender')['Mean_Estimate'].mean()
    mal_gender = df_malnutrition.groupby('Gender')['Mean_Estimate'].mean()
    ax4.bar(ob_gender.index, ob_gender.values, label='Obesity')
    ax4.bar(mal_gender.index, mal_gender.values, bottom=ob_gender.values, label='Malnutrition')
    ax4.set(xlabel="Gender", ylabel="Mean Estimate(%)")
    ax4.legend()
    st.pyplot(fig4)

    st.subheader("5. Pie Chart: Country Count by Obesity Level")
    fig5,ax5 =plt.subplots(figsize=(5, 5))
    level_counts= df_obesity['obesity_level'].value_counts()
    ax5.pie(level_counts.values,labels=level_counts.index,autopct='%1.1f%%')
    ax5.legend()
    st.pyplot(fig5)

    st.subheader("6. Heatmap: CI_Width Distribution by Region for malnutrition")
    heat_df =df_malnutrition.pivot_table(values='CI_Width', index='Age_Group', columns='Region', aggfunc='mean')
    fig6,ax6= plt.subplots(figsize=(10,6))
    sns.heatmap(heat_df, annot=True, cmap='YlGnBu', ax=ax6)
    st.pyplot(fig6)

    st.subheader("7. Obesity Burden per Region")
    fig7,ax7 =plt.subplots(figsize=(16, 8))
    region_sum=df_obesity.groupby('Region')['Mean_Estimate'].sum().reset_index()
    sns.barplot(data=region_sum,x='Region',y='Mean_Estimate',palette='Blues',ax=ax7)
    ax7.tick_params(axis='x',rotation=45)
    st.pyplot(fig7)

    st.subheader("8. Obesity by Region and Gender")
    fig8,ax8 = plt.subplots(figsize=(16, 8))
    df_obs_grouped =(df_obesity .groupby(['Region','Gender'])['Mean_Estimate'].mean().reset_index())
    sns.barplot(data=df_obs_grouped,x='Region',y='Mean_Estimate',hue='Gender',palette='Set1',ax=ax8)
    ax8.tick_params(axis='x',rotation=45)
    st.pyplot(fig8)
