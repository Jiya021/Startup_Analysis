import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Startup Analysis")

df = pd.read_csv("startup_cleaned.csv")

df["date"] = pd.to_datetime(df["date"],errors="coerce")
df["year"]=df["date"].dt.year
df["month"]=df["date"].dt.month


def load_overall_analysis():
    st.title("Overall Analysis")

    # total invested amount
    total = round(df["amount"].sum())
    # max amount infused in a startup
    max_funding=df.groupby("startup")["amount"].max().sort_values(ascending=False).head(1).values[0]
    # average funding
    avg_funding=df.groupby("startup")["amount"].sum().mean()
    # total funded startup
    num_startups=df["startup"].nunique()

    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.metric("Total" ,str(total) + "Cr")
    with col2:
        st.metric("Max" ,str(max_funding) + "Cr")   
    with col3:
        st.metric("average" ,str(round(avg_funding)) + "Cr")  
    with col4:
        st.metric("funded startups" ,str(num_startups)) 

    # mom graph month
    st.header("MOM graph")
    selected_option = st.selectbox("Select Type",["Total","Count"])
    if selected_option =="Total":
        temp_df=df.groupby(["year","month"])["amount"].sum().reset_index()
    else:
        temp_df=df.groupby(["year","month"])["amount"].count().reset_index()

    temp_df["x_axis"]=temp_df["month"].astype("str") + '-' + temp_df["year"].astype("str")

    fig5, ax5 = plt.subplots()
    ax5.plot(temp_df["x_axis"],temp_df["amount"])
    ax5.tick_params(axis='x', labelsize=4)
    ax5.tick_params(axis='y', labelsize=7)
    fig5.set_figheight(3)    
    plt.xticks(rotation="vertical")
    st.pyplot(fig5)

    st.header("Sector Analysis")
    selected_option1= st.selectbox("Select Type",["Total_amount","Count_of_investments"])
    if selected_option1 =="Total_amount":
        temp_df=df.groupby(["vertical"])["amount"].sum().sort_values(ascending=False).reset_index()
    else:
        temp_df=df.groupby(["vertical"])["amount"].count().sort_values(ascending=False).reset_index()
    st.dataframe(temp_df)
    
    st.header("Type of Funding")
    funding_data=df.groupby(["year", "round"])["amount"].sum().reset_index()
    funding_data = funding_data[funding_data["amount"] > 0].set_index("year")
    st.dataframe(funding_data)

    st.header("City Wise Funding")
    selected_option2= st.selectbox("Select Type",["Total Amount","Count of investments"])
    if selected_option2 =="Total amount":
        temp_df=df.groupby(["city"])["amount"].sum().sort_values(ascending=False).reset_index()
    else:
        temp_df=df.groupby(["city"])["amount"].count().sort_values(ascending=False).reset_index()
    st.dataframe(temp_df)

    st.header("Top Startup")
    top_startup=df.groupby("startup")["amount"].sum().sort_values(ascending=False).head(1)
    st.dataframe(top_startup)

    st.header("TOP Startup (YOY)")
    grouped=df.groupby(["year", "startup"])["amount"].sum().reset_index().sort_values(by=["year", "amount"], ascending=[True, False])
    top_startups = grouped.groupby("year").head(1).set_index("year")
    st.dataframe(top_startups)
   
    st.header("TOP Investors (YOY)")
    grouped=df.groupby(["year", "investors"])["amount"].sum().reset_index().sort_values(by=["year", "amount"], ascending=[True, False])
    top_investors = grouped.groupby("year").head(1).set_index("year")
    st.dataframe(top_investors)



def load_investor_detail(investor):
    st.title(investor)

    # load the recent five investments of the investor
    last5_df = df[df["investors"].str.contains("investor")].head()[["date","startup","vertical","city","round","amount"]]
    last5_df['date'] = last5_df['date'].dt.strftime('%d-%m-%Y')
    last5_df.set_index("date",inplace=True)
    st.subheader("Most Recent Investments")
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)
    with col1:
        # biggest investment
        big_series=df[df["investors"].str.contains("investor")].groupby("startup")["amount"].sum().sort_values(ascending=False).head()
        st.subheader("Biggest Investments")
        fig, ax = plt.subplots()
        ax.bar(big_series.index,big_series.values)
        st.pyplot(fig)
    with col2:
        # verticals invested in
        vertical_series=(df[df["investors"].str.contains("investor")].groupby("vertical")["amount"].sum().nlargest(7))
        st.subheader("Sectors Invested In")
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series,labels=vertical_series.index,autopct="%0.1f%%")
        st.pyplot(fig1)

    col3, col4 = st.columns(2)
    with col3:
        # round
        round_series=df[df["investors"].str.contains("investor")].groupby("round")["amount"].sum()
        st.subheader("Stages")
        fig2, ax2= plt.subplots()
        ax2.pie(round_series,labels=round_series.index,autopct="%0.1f%%")
        st.pyplot(fig2)
    with col4:
        # city invested in
        city_series=df[df["investors"].str.contains("investor")].groupby("city")["amount"].sum().nlargest(7)
        st.subheader("Cities Invested In")
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series,labels=city_series.index,autopct="%0.1f%%")
        st.pyplot(fig3)


    # year on year investment
    year_series=df[df["investors"].str.contains("investor")].groupby("year")["amount"].sum()
    st.subheader("YOY Investment")
    fig4, ax4 = plt.subplots()
    ax4.plot( year_series.index,year_series.values)
    st.pyplot(fig4)



    # get similar investors of same vertical
    def get_vertical_of_investor(df, investor_name):
    # """Returns the vertical (sector) of the selected investor."""
        verticals = df[df["investors"].str.contains(investor, case=False, na=False)]["vertical"].unique()
        return verticals[0] if len(verticals) > 0 else None
       
    def get_similar_investors(df, investor_name):
    # """Finds all investors who have invested in the same vertical as the selected investor."""
        vertical = get_vertical_of_investor(df, investor)
        
        if vertical:
            similar_investors = df[df["vertical"] == vertical]["investors"].drop_duplicates()
            return similar_investors.head(5)
        else:
            return pd.DataFrame(columns=["investors", "vertical", "amount"])

    if selected_investor:
        similar_investors = get_similar_investors(df, selected_investor)

        if similar_investors.any():
            st.subheader(f"Investors in the same vertical as {selected_investor}:")
            st.dataframe(similar_investors)  # Display investors as a comma-separated list
        else:
            st.write("No similar investors found.")



def load_startup_detail(startup):
    st.title(startup)

    st.header("Founders")
    def get_founders(startup_name):
        return df[df['startup'].str.lower() == startup.lower()]['investors']
    founders=get_founders(startup)
    if not founders.empty:
        st.write(founders)  # Show the first investor result
        # Or, to show all matching investor entries:
        # st.dataframe(investors)
    else:
        st.write("No investor data found for this startup.")

    st.header("Industry")
    def get_industry(startup_name):
        return df[df['startup'].str.lower() == startup_name.lower()]['vertical']
    Industry=get_industry(startup)
    if not Industry.empty:
        st.write(Industry.iloc[0])  # or st.write(vertical.unique()[0])
    else:
        st.write("No industry data found.")

    st.header("SUB-Industry")
    def get_subindustry(startup_name):
        return df[df['startup'].str.lower() == startup_name.lower()]['subvertical']
    SUB_Industry=get_subindustry(startup)
    if not SUB_Industry.empty:
        st.write(SUB_Industry.iloc[0])  # or st.write(vertical.unique()[0])
    else:
        st.write("No subindustry data found.")
    
    st.header("Location")
    def get_location(startup_name):
        return df[df['startup'].str.lower() == startup_name.lower()]['city']
    location=get_location(startup)
    if not location.empty:
        st.write(location.iloc[0])  # or st.write(vertical.unique()[0])
    else:
        st.write("No location data found.")

    st.header("Funding Details")
    def get_funding_details(startup_name):
        data=df[df['startup'].str.lower() == startup_name.lower()][["date","investors","round"]]
        data['date'] = data['date'].dt.strftime('%d-%m-%Y')
        data.set_index("date",inplace=True)
        return data
    fund_details=get_funding_details(startup)
    if not fund_details.empty:
        st.write(fund_details)  # or st.write(vertical.unique()[0])
    else:
        st.write("No funding data found.")

    st.header("Similar Startups")
    # Get vertical of selected startup
    def get_vertical_of_startup(df, startup_name):
        verticals = df[df["startup"].str.lower() == startup_name.lower()]["vertical"].unique()
        return verticals[0] if len(verticals) > 0 else None

    # Get similar startups in the same vertical
    def get_similar_startups(df, startup_name):
        vertical = get_vertical_of_startup(df, startup_name)
        
        if vertical:
            similar_startups = df[df["vertical"] == vertical]["startup"].drop_duplicates()
            return similar_startups.head(5)
        else:
            return pd.DataFrame(columns=["startup"])

    # Display section
    if selected_startup:
        similar_startups = get_similar_startups(df, selected_startup)

        if not similar_startups.empty:
            st.subheader(f"Startups in the same vertical as {selected_startup}:")
            st.dataframe(similar_startups)
        else:
            st.write("No similar startups found.")




st.sidebar.title("Startup Funding Analysis")
option =st.sidebar.selectbox("Select one",["Overall Analysis","Startup","Investor"])


if option == "Overall Analysis":
    load_overall_analysis()

elif option == "Startup":
    selected_startup=st.sidebar.selectbox("select start",sorted(df["startup"].unique().tolist()))
    btn1 = st.sidebar.button("Find startup details")
    if btn1:
        load_startup_detail(selected_startup)

else:
    selected_investor=st.sidebar.selectbox("select startup",sorted(set(df["investors"].str.split(",").sum())))
    btn2 = st.sidebar.button("Find investor details")
    if btn2:
        load_investor_detail(selected_investor)
